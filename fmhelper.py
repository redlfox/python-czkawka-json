from html import parser
from mimetypes import init
import sys, time, re
try:
	import orjson
except ImportError:
	import json as orjson
from pprint import pprint
from pathlib import Path, PurePath
import argparse
import configparser
from utils_s import get_encoding, writeToFile, readFromFile, readFromFileE, convert_size, getFileOperationMode, getBatchFileExt
import pandas as pd
import platform

# import cv2

# Set file with biggest size as source, if multiple files have same size, set the one with shortest path depth, if still multiple files, set the one with longest file name length as source
def detectJsonStructure(CZJson):
	FirstItemCZJson = next(iter(CZJson))
	isListJson = False
	n2LevelInSets = False
	if isinstance(FirstItemCZJson, list):
		isListJson = True
	elif isinstance(CZJson.get(FirstItemCZJson)[0], dict):
		n2LevelInSets = False
	elif isinstance(CZJson.get(FirstItemCZJson)[0], list):
		if CZJson.get(FirstItemCZJson)[0][0].get("path"):
			n2LevelInSets = True
		else:
			sys.exit("Unknown structure in file.")
	else:
		sys.exit("Unknown structure in file.")
	return isListJson, n2LevelInSets

def getBiggestFile(CZFileItems: list) -> None:
	CZFileItems.sort(key=lambda x: x['size'], reverse=True)
	# print(CZFileItems)
	return CZFileItems[0]

def setFitSourceAndTargetFiles(CZFileItems: list, CAFileSource: dict = {}) -> None:
	CZFilesEqualSizeSorted = []
	CZFilesSorting = []
	CZFilesSorted = []
	CZFilesSources = []
	CZFilesTargets = []
	CZFilesTargetsTemp = []
	CZFileItemsPaths = [fi['path'] for fi in CZFileItems]
	CZFileItemsDupPaths = set([fp for fp in CZFileItemsPaths if CZFileItemsPaths.count(fp) > 1])
	if CZFileItemsDupPaths:
		print("Duplicate file paths found in czkawka file items:", CZFileItemsDupPaths)
		CZFileItemsDF = pd.DataFrame(CZFileItems)
		CZFileItemsDF.drop_duplicates(subset=['path'], keep='last', inplace=True)
		CZFileItems = CZFileItemsDF.to_dict("records")
		print("Removed duplicate file paths.")
	if not CZFileItems or len(CZFileItems) == 0:
		return ([], [])
	if len(CZFileItems) < 2:
		return ([], [])
	CZFileItems.sort(key=lambda x: x['size'], reverse=True)
	CZFilesSizes = [fi['size'] for fi in CZFileItems]
	# pprint(CZFilesSizes)

	while len(CZFilesSizes) > 0:
		CZFilesEqualSize = [fi for fi in CZFileItems if fi["size"] == CZFilesSizes[0]]
		# print("czkawkaFileItemsInASize:", CZFilesEqualSize)
		CZFilesEqualSizeSorted = []
		if len(CZFilesEqualSize) > 1:
			CZFilesEqualSize.sort(key=lambda x: len(Path(x['path']).parts), reverse=False)
			CZFilesEqualSizePathDepths = [len(Path(fi['path']).parts) for fi in CZFilesEqualSize]
			# print(
			#     "czkawkaFileItemsInASizePathLength:", CZFilesEqualSizePathDepths
			# )
			while len(CZFilesEqualSizePathDepths) > 0:
				CZFilesInSameDepth = [
				    fi for fi in CZFilesEqualSize if len(Path(fi['path']).parts) == CZFilesEqualSizePathDepths[0]
				]
				if len(CZFilesInSameDepth) > 1:
					CZFilesInSameDepth.sort(key=lambda x: len(PurePath(x['path']).name), reverse=True)
					# print("czkawkaFileItemsInSameDepth:", CZFilesInSameDepth)
				CZFilesEqualSizePathDepths = [
				    pd for pd in CZFilesEqualSizePathDepths if pd != CZFilesEqualSizePathDepths[0]
				]
				CZFilesEqualSizeSorted.extend(CZFilesInSameDepth)
		else:
			CZFilesEqualSizeSorted.extend(CZFilesEqualSize)
		CZFilesSizes = [sz for sz in CZFilesSizes if sz != CZFilesSizes[0]]
		CZFilesSorting.extend(CZFilesEqualSizeSorted)
	CZFilesSorted = CZFilesSorting
	CZFilesSorting = []
	CZFilesSources.append(CZFilesSorted[0]) if CZFilesSorted else None
	if CZFilesSources:
		if len(CZFilesSources) > 1:
			print("Files to be source:", CZFilesSources)
			CZFilesTargetsTemp = CZFileItems
			for fs in CZFilesSources:
				CZFilesTargets = [fi for fi in CZFilesTargetsTemp if fi['path'] != fs['path']]
		else:
			print("File to be source:", CZFilesSources)
			CZFilesTargets = [fi for fi in CZFileItems if fi['path'] != CZFilesSources[0]['path']]
		if len(CZFilesSources) + len(CZFilesTargets) > len(CZFileItems):
			print("Mismatch in file counts after setting source and targets.")
			return ([], [])
		return (CZFilesSources, CZFilesTargets)
	else:
		print("No valid files found to remove.")

def generateCLICommands(
    operation: str, target: Path, source: Path = None, forceConfirm: bool = False, gioTrash: bool = False,
    toNewFile: bool = False
) -> str:
	SystemType = platform.system()
	commandArguments = ""
	forceExecuteOption = ""
	newFileOption = ""
	targetStr = str(target)
	if SystemType == "Linux" or SystemType == "Darwin":
		if re.match(r".*([`'!]).*", targetStr):  # also for cygwin and msys2
			targetStr = re.sub(r"([\s`'!()&])", r"\\\1", targetStr)
		else:
			targetStr = '"{}"'.format(target)
	elif SystemType == "Windows":
		targetStr = '"{}"'.format(target)
	else:
		targetStr = '"{}"'.format(target)
	if operation == "trash":
		if SystemType == "Linux" or SystemType == "Darwin":
			if not gioTrash:
				return f'trash-put {targetStr}'
			elif gioTrash:
				if forceConfirm:
					forceExecuteOption = "-f "
				return f'gio trash {forceExecuteOption}{targetStr}'
		elif SystemType == "Windows":
			print("Windows trash operation is not implemented yet.")
			return f'{targetStr}'
	elif operation == "delete":
		if SystemType == "Linux" or SystemType == "Darwin":
			if not forceConfirm:
				commandArguments = "-i "
			else:
				commandArguments = "-f "
			return f'rm {commandArguments}{targetStr}'
		elif SystemType == "Windows":
			if not forceConfirm:
				return f'del /P {targetStr}'
			else:
				return f'del /F /Q {targetStr}'
	elif operation == "overwrite":
		if SystemType == "Linux" or SystemType == "Darwin":
			if not forceConfirm:
				return f'cp -i "{source}" {targetStr}'
			else:
				return f'cp -f "{source}" {targetStr}'
		elif SystemType == "Windows":
			if forceConfirm:
				forceExecuteOption = "/Y "
			if toNewFile:
				newFileOption = "echo f | "
			return f'{newFileOption}xcopy {forceExecuteOption}"{source}" {targetStr}'
	else:
		print("Unknown file operation:", operation)
		return ""
	if not (SystemType == "Linux" or SystemType == "Darwin" or SystemType == "Windows"):
		print("Unsupported system type for file operations:", SystemType)
		return ""

def main() -> None:

	init()
	batchFileExt = getBatchFileExt()
	parser = argparse.ArgumentParser(description="Tool to process files.")
	parser.add_argument("input", nargs="?", default=None, help="file path to process.")
	parser.add_argument(
	    "-sd", "-source-dir", default=None,
	    help="Set source directory paths in json that will be processed. Separate multiple directories with comma."
	)
	parser.add_argument(
	    "-td", "-target-dir", default=None,
	    help="Optional, set target directory paths in json that will be processed, treat all files in duplicate sets as targets if blank. Separate multiple directories with comma."
	)
	parser.add_argument(
	    "-tdf", "-target-dir-file", default=None,
	    help="Optional, target directory paths in json that will be processed, treat all files in duplicate sets as targets if blank. Read directories from given file."
	)
	parser.add_argument(
	    "-ed", "-excluded-dir", default=None,
	    help="Optional, excluded directory paths in json that will be ignored. Separate multiple directories with comma."
	)
	parser.add_argument(
	    "-edf", "-excluded-dir-file", default=None,
	    help="Optional, excluded directory paths in json that will be ignored. Read directories from given file."
	)
	parser.add_argument("-r", "-read", action="store_true", help="Optional, test")
	parser.add_argument("-dry", action="store_true", help="Optional, do not perform any file operations.")
	parser.add_argument(
	    "-fe", "-filter-exist", action="store_true", help="Filter to include existing files and folders."
	)
	parser.add_argument("-ff", "-filter-file", action="store_true", help="Filter to include existing files.")
	parser.add_argument(
	    "-m", "-mode", default=None,
	    help="Optional, file operation mode. \"d\" for delete, \"t\" for trash, \"o\" for overwrite."
	)
	parser.add_argument(
	    "-nb", "-no-backup", action="store_true", help="Optional, do not create backup before overwrite files."
	)
	parser.add_argument(
	    "-s", "-skip-compare", action="store_true",
	    help="Optional, do not compare files in duplicate sets to filter files for operation."
	)
	parser.add_argument(
	    "-d", "-destination", default=None, help="Optional, set destination for saving generated json files."
	)
	parser.add_argument("-bd", "-backup-destination", default=None, help="backup-destination.")
	parser.add_argument(
	    "-p", "-json-prefix", default=None, help="Optional, set prefix of filenames for generated json files to save."
	)
	parser.add_argument("-rs", "-real-sizes", action="store_true", help="Optional, use real file sizes.")
	parser.add_argument("-db", "-debug", action="store_true", help="Optional, show debug information.")
	parser.add_argument(
	    "-c", "-command", action="store_true",
	    help="Optional, give commands for file operations instead of using python."
	)
	parser.add_argument("-o", "-organize", action="store_true", help="Organize files from files.")
	parser.add_argument("-i", "-interact", action="store_true", help="Interact with files.")
	parser.add_argument("-cs", "-calculate-space", action="store_true", help="Calculate releasable space from files.")
	parser.add_argument("-ns", "-no-slc", action="store_true", help="test.")
	args = parser.parse_args()

	FilePath: Path | None = Path(args.input) if args.input else None
	if FilePath and FilePath.is_file():
		print("File path from argument:", FilePath)
	else:
		print("No valid file path provided.")
		sys.exit()
	filterExist = False
	filterFile = False
	if args.ff:
		filterFile = True
	if args.fe:
		filterExist = True
	cc1 = 0
	if args.o:
		cc1 += 1
	if args.i:
		cc1 += 1
	if cc1 > 1:
		sys.exit("Can not use mutiple mode.")
	try:
		PathListFromFile = readFromFileE(FilePath, "utf-8").splitlines()
	except Exception as e:
		# handle_caught_exception(e, known=True)
		print(f"Failed to load file. Error: {e}")
		sys.exit()
		return None
	pathListNew = []
	for pathStr in PathListFromFile:
		path = Path(pathStr)
		if filterFile:
			if path.is_file():
				pathListNew.append(path)
	if pathListNew:
		pathListInput = pathListNew
	else:
		pathListInput = PathListFromFile

	FileDestination = PurePath()
	if args.d:
		FileDestination = PurePath(args.d)
	skipCompare: bool = args.s
	if args.o:
		dirsToSetAsSource = []
		dirsToSetAsTarget = []
		forceSelectBiggestSource = False
		autoSelectSource = False
		useCommands = False
		if args.sd:
			try:
				dirsToSetAsSource = re.sub("\'|\"", "", args.sd).split(",")
				print("Source directories from argument: ")
				pprint(dirsToSetAsSource)
				# sys.exit()
			except Exception as e:
				print(f"Failed to parse source directories. Error: {e}")
				sys.exit()
				return None
		if args.td:
			try:
				dirsToSetAsTarget = re.sub("\'|\"", "", args.td).split(",")
				print("Target directories from argument: ")
				pprint(dirsToSetAsTarget)
				# sys.exit()
			except Exception as e:
				print(f"Failed to parse target directories. Error: {e}")
				sys.exit()
				return None
		if args.tdf:
			if dirsToSetAsTarget:
				dirsToSetAsTarget.extend((readFromFile(args.tdf)).splitlines())
			else:
				dirsToSetAsTarget = readFromFile(args.tdf).splitlines()
		if args.ed:
			try:
				excludedDirs = args.ed.split(",")
				print("Excluded directories from argument: ")
				pprint(excludedDirs)
			except Exception as e:
				print(f"Failed to parse excluded directories. Error: {e}")
				sys.exit()
				return None
		if args.edf:
			if excludedDirs:
				excludedDirs.extend((readFromFile(args.edf)).splitlines())
			else:
				excludedDirs = readFromFile(args.edf).splitlines()
		if args.c:
			useCommands = True
		# File operation mode.
		fileOperationMode: str | None = str(args.m) if args.input else None
		fileOperationModeFull = getFileOperationMode(fileOperationMode)

		fileOperateSet: dict = {}
		systemCLICommands: str = ""
		targetCommands: list = []
		backupCommands: list = []
		targetFilePaths = []
		for targetPath in pathListInput:
			targetFilePath = Path(targetPath)
			CZFilesToOperatePerSet: list = []
			CZFilesToOperatePerSetMapping: dict = {}
			CZFilesSources = None
			CZFileIndexNum = 0
			CZFileExcludedFromTargets = []
			CZFilesToSetAsSource = []
			if useCommands:
				if fileOperationMode == "d" or fileOperationMode == "t":
					targetCommands.append(generateCLICommands(operation=fileOperationModeFull, target=targetFilePath))
				if fileOperationMode == "o":
					if args.bd:
						targetFileBackupPath = PurePath(args.bd) / targetFilePath.name
						backupCommands.append(
						    generateCLICommands(
						        operation="overwrite", target=targetFileBackupPath, source=targetFilePath, toNewFile=True
						    )
						)

			if fileOperationMode == "o":
				afsasaf = "\n".join(str(fi) for fi in targetFilePaths)
				print(afsasaf)
			if useCommands:
				if backupCommands:
					backupCommandsStr = '\n'.join(backupCommands)
					print("generated backup commands:")
					for c in backupCommands:
						print(c)
					if FileDestination:
						writeToFile(
						    str(FileDestination / f"{str(FilePath.name)}-bak.{batchFileExt}"), backupCommandsStr,
						    openmode='w', file_encoding='utf-8'
						)
		print("generated commands:")
		for c in targetCommands:
			targetCommandsStr = '\n'.join(targetCommands)
			print(c)
			writeToFile(
			    str(FileDestination / f"{str(FilePath.name)}-topc.{batchFileExt}"), targetCommandsStr, openmode='w',
			    file_encoding='utf-8'
			)

			# if CZfileOperationMode == "t":
			# 	pass
			# elif CZfileOperationMode == "d":
			# 	CZFilesToBeDeleted.extend(CZFilesToOperatePerSet)
			# elif CZfileOperationMode == "o":
			# 	CZFilesToBeOverwritten.extend(CZFilesToOperatePerSet)
			# else:
			# 	print("Unknown file operation mode:", CZfileOperationMode)
			# sys.exit()
		# print(CZJsonFilePath.name)
		# sys.exit()
	# if args.i:
	# 	if isListJson:
	# 		CZJsonNew = []
	# 	else:
	# 		CZJsonNew = {}
	# 	CZJsonFromFileItemIndex = 0
	# 	for duplicateSetKey in CZJsonFromFile:
	# 		# print(duplicateSetKey)
	# 		# print(duplicateSetKey)
	# 		# print(CZJsonFromFileItemIndex)
	# 		if isListJson:
	# 			duplicateSet = CZJsonFromFile[CZJsonFromFileItemIndex]
	# 		elif n2LevelInSets:
	# 			duplicateSet = CZJsonFromFile.get(str(duplicateSetKey))[0]
	# 		else:
	# 			duplicateSet = CZJsonFromFile.get(str(duplicateSetKey))
	# 		fileItemsCountLikelyExist = len(duplicateSet)
	# 		CZFileIndexNum = 0
	# 		# if isListJson:
	# 		# 	pass
	# 		# elif duplicateSetKey not in CZJsonNew:
	# 		# 	CZJsonNew[duplicateSetKey]=[]
	# 		CZJsonSetTemp = []
	# 		skipSet = False
	# 		for fileItem in duplicateSet:
	# 			CZFileIndexNum += 1
	# 			filePathInSet = Path(fileItem['path'])
	# 			# print("File path in the set:", filePathInSet)
	# 			# sys.exit()
	# 			if filePathInSet.is_file():  # todo: add premission detection
	# 				print("File path in the set exists:", filePathInSet)
	# 				CZJsonSetTemp.append(fileItem)
	# 			else:
	# 				print("File path in the set does not exist:", filePathInSet)
	# 				fileItemsCountLikelyExist -= 1
	# 			if fileItemsCountLikelyExist <= 1:
	# 				print(
	# 				    "Only one file likely exists in this duplicate set, skipping further checks for this set."
	# 				)
	# 				# if isListJson:
	# 				# 	pass
	# 				# elif duplicateSetKey in CZJsonNew:
	# 				# 	del CZJsonNew[duplicateSetKey]
	# 				# todo: check if biggest file missing.
	# 				skipSet = True
	# 				break
	# 		if not skipSet:
	# 			if isListJson:
	# 				CZJsonNew.append(CZJsonSetTemp)
	# 			else:
	# 				CZJsonNew[duplicateSetKey] = CZJsonSetTemp
	# 		CZJsonFromFileItemIndex += 1
	# 	if FileDestination and not args.dry:
	# 		# writeToFile()
	# 		writeToFile(
	# 		    str(FileDestination / FilePath.name),
	# 		    orjson.dumps(CZJsonNew,
	# 		                 option=orjson.OPT_INDENT_2).decode('utf-8'),
	# 		    openmode='w',
	# 		    file_encoding='utf-8'
	# 		)
	# 	else:
	# 		if args.dry:
	# 			print("Dry test.")
	# 		pprint(CZJsonNew)
	# 	if CZJsonNew:
	# 		CZJsonInput = CZJsonNew
	# 	else:
	# 		CZJsonInput = CZJsonFromFile
	# 	if args.cs:
	# 		releasableSpace = 0
	# 		isListJson, n2LevelInSets = detectJsonStructure(CZJsonFromFile)
	# 		CZJsonInputItemIndex = 0
	# 		for duplicateSetKey in CZJsonInput:
	# 			# print(duplicateSetKey)
	# 			if isListJson:
	# 				duplicateSet = CZJsonInput[CZJsonInputItemIndex]
	# 			elif n2LevelInSets:
	# 				duplicateSet = CZJsonInput.get(str(duplicateSetKey))[0]
	# 			else:
	# 				duplicateSet = CZJsonInput.get(str(duplicateSetKey))
	# 			# pprint(duplicateSet)
	# 			duplicateSet.sort(key=lambda x: x['size'], reverse=True)
	# 			for fi in duplicateSet[1:]:
	# 				releasableSpace += fi["size"]
	# 			CZJsonInputItemIndex += 1

	# 		print("Releasable space:", convert_size(releasableSpace))

if __name__ == "__main__":
	main()

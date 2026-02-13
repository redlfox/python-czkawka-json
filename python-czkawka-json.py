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
from utils_s import get_encoding, writeToFile,readFromFile,convert_size
import pandas as pd
import platform
import cv2

# Set file with biggest size as source, if multiple files have same size, set the one with shortest path depth, if still multiple files, set the one with longest file name length as source
def getBiggestFile(CZFileItems: list) -> None:
	CZFileItems.sort(key=lambda x: x['size'], reverse=True)
	# print(CZFileItems)
	return CZFileItems[0]

def setFitSourceAndTargetFiles(CZFileItems: list,CAFileSource:dict={}) -> None:
	CZFilesEqualSizeSorted = []
	CZFilesSorting = []
	CZFilesSorted = []
	CZFilesSources = []
	CZFilesTargets = []
	CZFilesTargetsTemp = []
	CZFileItemsPaths = [fi['path'] for fi in CZFileItems]
	CZFileItemsDupPaths = set(
	    [fp for fp in CZFileItemsPaths if CZFileItemsPaths.count(fp) > 1]
	)
	if CZFileItemsDupPaths:
		print(
		    "Duplicate file paths found in czkawka file items:",
		    CZFileItemsDupPaths
		)
		CZFileItemsDF = pd.DataFrame(CZFileItems)
		CZFileItemsDF.drop_duplicates(
		    subset=['path'], keep='last', inplace=True
		)
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
		CZFilesEqualSize = [
		    fi for fi in CZFileItems if fi["size"] == CZFilesSizes[0]
		]
		# print("czkawkaFileItemsInASize:", CZFilesEqualSize)
		CZFilesEqualSizeSorted = []
		if len(CZFilesEqualSize) > 1:
			CZFilesEqualSize.sort(
			    key=lambda x: len(Path(x['path']).parts), reverse=False
			)
			CZFilesEqualSizePathDepths = [
			    len(Path(fi['path']).parts) for fi in CZFilesEqualSize
			]
			# print(
			#     "czkawkaFileItemsInASizePathLength:", CZFilesEqualSizePathDepths
			# )
			while len(CZFilesEqualSizePathDepths) > 0:
				CZFilesInSameDepth = [
				    fi for fi in CZFilesEqualSize if
				    len(Path(fi['path']).parts) == CZFilesEqualSizePathDepths[0]
				]
				if len(CZFilesInSameDepth) > 1:
					CZFilesInSameDepth.sort(
					    key=lambda x: len(PurePath(x['path']).name),
					    reverse=True
					)
					# print("czkawkaFileItemsInSameDepth:", CZFilesInSameDepth)
				CZFilesEqualSizePathDepths = [
				    pd for pd in CZFilesEqualSizePathDepths
				    if pd != CZFilesEqualSizePathDepths[0]
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
			print("Files to be source: ", CZFilesSources)
			CZFilesTargetsTemp = CZFileItems
			for fs in CZFilesSources:
				CZFilesTargets = [
				    fi for fi in CZFilesTargetsTemp if fi["path"] != fs["path"]
				]
		else:
			print("File to be source: ", CZFilesSources)
			CZFilesTargets = [
			    fi
			    for fi in CZFileItems if fi["path"] != CZFilesSources[0]["path"]
			]
		if len(CZFilesSources) + len(CZFilesTargets) > len(CZFileItems):
			print("Mismatch in file counts after setting source and targets.")
			return ([], [])
		return (CZFilesSources, CZFilesTargets)
	else:
		print("No valid files found to remove.")

def generateCLICommands(
    operation: str,
    target: Path,
    source: Path=None,
    forceConfirm: bool = False,
    gioTrash: bool = False,
	toNewFile: bool = False
) -> str:
	SystemType = platform.system()
	commandArguments=""
	forceExecuteOption = ""
	newFileOption = ""
	if SystemType == "Linux" or SystemType == "Darwin":
		if re.match(r".*(\'|!).*",target): # also for cygwin and msys2
			targetStr=re.sub(r"([\s'!()&])",r"\\\1",target)
		else:
			targetStr='"{}"'.format(target)
	elif SystemType == "Windows":
		targetStr='"{}"'.format(target)
	else:
		targetStr='"{}"'.format(target)
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
				commandArguments="-i "
			else:
				commandArguments="-f "
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
		print("Unknown file operation: ", operation)
		return ""
	if not (
	    SystemType == "Linux" or SystemType == "Darwin" or
	    SystemType == "Windows"
	):
		print("Unsupported system type for file operations: ", SystemType)
		return ""

def main() -> None:

	init()

	parser = argparse.ArgumentParser(
	    description="Tool to process Czkawka JSON files."
	)
	parser.add_argument(
	    "input",
	    nargs="?",
	    default=None,
	    help="Czkawka JSON file path to process."
	)
	parser.add_argument(
	    "-sd",
	    "-source-dir",
	    default=None,
	    help=
	    "Set source directory paths in json that will be processed. Separate multiple directories with comma."
	)
	parser.add_argument(
	    "-td",
	    "-target-dir",
	    default=None,
	    help=
	    "Optional, set target directory paths in json that will be processed, treat all files in duplicate sets as targets if blank. Separate multiple directories with comma."
	)
	parser.add_argument(
	    "-tdf",
	    "-target-dir-file",
	    default=None,
	    help=
	    "Optional, target directory paths in json that will be processed, treat all files in duplicate sets as targets if blank. Read directories from given file."
	)
	parser.add_argument(
	    "-ed",
	    "-excluded-dir",
	    default=None,
	    help=
	    "Optional, excluded directory paths in json that will be ignored. Separate multiple directories with comma."
	)
	parser.add_argument(
	    "-edf",
	    "-excluded-dir-file",
	    default=None,
	    help=
	    "Optional, excluded directory paths in json that will be ignored. Read directories from given file."
	)
	parser.add_argument(
	    "-r",
	    "-read",
	    action="store_true",
	    help=
	    "Optional, test"
	)
	parser.add_argument(
	    "-dry",
	    action="store_true",
	    help=
	    "Optional, do not perform any file operations."
	)
	parser.add_argument(
	    "-g",
	    "-get-metadata",
	    action="store_true",
	    help=
	    "Optional, get file metadata by file type."
	)
	parser.add_argument(
	    "-m",
	    "-mode",
	    default=None,
	    help=
	    "Optional, file operation mode. \"d\" for delete, \"t\" for trash, \"o\" for overwrite."
	)
	parser.add_argument(
	    "-nb",
	    "-no-backup",
	    action="store_true",
	    help="Optional, do not create backup before overwrite files."
	)
	parser.add_argument(
	    "-s",
	    "-skip-compare",
	    action="store_true",
	    help="Optional, do not compare files in duplicate sets to filter files for operation."
	)
	parser.add_argument(
	    "-d",
	    "-destination",
	    default=None, 
	    help="Optional, set destination for saving generated json files."
	)
	parser.add_argument(
	    "-p",
	    "-json-prefix",
	    default=None, 
	    help="Optional, set prefix of filenames for generated json files to save."
	)
	parser.add_argument(
	    "-rs",
	    "-real-sizes",
	    action="store_true",
	    help="Optional, use real file sizes."
	)
	parser.add_argument(
	    "-db",
	    "-debug",
	    action="store_true",
	    help="Optional, show debug information."
	)
	parser.add_argument(
	    "-c",
	    "-command",
	    action="store_true",
	    help=
	    "Optional, give commands for file operations instead of using python."
	)
	parser.add_argument(
	    "-o",
	    "-organize",
	    action="store_true",
	    help=
	    "Organize files from Czkawka json files."
	)
	parser.add_argument(
	    "-i",
	    "-interact",
	    action="store_true",
	    help=
	    "Interact with Czkawka json files."
	)
	parser.add_argument(
	    "-cs",
	    "-calculate-space",
	    action="store_true",
	    help=
	    "Calculate releasable space from Czkawka json files."
	)
	args = parser.parse_args()

	CZJsonFilePath: Path | None = Path(args.input) if args.input else None
	if CZJsonFilePath and CZJsonFilePath.is_file():
		print("Czkawka JSON file path from argument: ", CZJsonFilePath)
	else:
		print("No valid Czkawka JSON file path provided.")
		sys.exit()
	cc1=0
	if args.o:
		cc1+=1
	if args.i:
		cc1+=1
	if cc1>1:
		sys.exit("Can not use mutiple mode.")
	try:
		czkawkaJsonFromFile = orjson.loads(readFromFile(CZJsonFilePath))
	except Exception as e:
		# handle_caught_exception(e, known=True)
		print(f"Failed to load json file. Error: {e}")
		sys.exit()
		return None
	FirstKeyCzkawkaJsonFromFile = next(iter(czkawkaJsonFromFile))
	# print("FirstKeyCzkawkaJsonFromFile: ", FirstKeyCzkawkaJsonFromFile)
	# print(type(czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0]))
	if isinstance(
		czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0], dict
	):
		n2LevelInSets = False
	elif isinstance(
		czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0], list
	):
		if czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile
								)[0][0].get("path"):
			n2LevelInSets = True
		else:
			sys.exit("Unknown structure in czkawka json file.")
	else:
		sys.exit("Unknown structure in czkawka json file.")
	# sys.exit()
	# with open(CZJsonFilePath, "r", encoding=get_encoding(CZJsonFilePath)) as f:
	CZJsonDestination=PurePath()
	if args.d:
		CZJsonDestination=PurePath(args.d)
	skipCompare: bool = args.s
	if args.o:
		dirsToSetAsSource=[]
		dirsToSetAsTarget=[]
		forceSelectBiggestSource=False
		autoSelectSource=False
		useCommands=False
		if args.sd:
			try:
				dirsToSetAsSource = re.sub("\'|\"","",args.sd).split(",")
				print("Source directories from argument: ")
				pprint(dirsToSetAsSource)
				# sys.exit()
			except Exception as e:
				print(f"Failed to parse source directories. Error: {e}")
				sys.exit()
				return None
		if args.td:
			try:
				dirsToSetAsTarget = re.sub("\'|\"","",args.td).split(",")
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
				dirsToSetAsTarget=readFromFile(args.tdf).splitlines()
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
				excludedDirs=readFromFile(args.edf).splitlines()
		if args.c:
			useCommands=True
		# File operation mode, use trash mode if not provided or invalid
		CZFileOperationMode: str | None = str(args.m) if args.input else None
		if CZFileOperationMode and CZFileOperationMode in ["d", "t", "o"]:
			if CZFileOperationMode=="d":
				CZFileOperationModeFull="delete"
			if CZFileOperationMode=="t":
				CZFileOperationModeFull="trash"
			if CZFileOperationMode=="o":
				CZFileOperationModeFull="overwrite"
			print("File operation mode from argument:", CZFileOperationModeFull)
		else:
			print(
				"No valid file operation mode provided, won't perform any file operations."
			)
		# print("File operation mode argument: ", CZFileOperationMode)

		CZFilesToBeOverwritten = []
		CZFilesToBeDeleted = []
		CZFilesToOperateMapping = []
		# Proccessing every duplicate set in czkawka json data
		for duplicateSetKey in czkawkaJsonFromFile:
			# print(duplicateSetKey)
			if n2LevelInSets:
				duplicateSet = czkawkaJsonFromFile.get(str(duplicateSetKey))[0]
			else:
				duplicateSet = czkawkaJsonFromFile.get(str(duplicateSetKey))
			fileItemsCountLikelyExist = len(duplicateSet)
			CZFilesToOperatePerSet: list = []
			CZFilesToOperatePerSetMapping: dict = {}
			CZFilesSources = None
			CZFileIndexNum=0
			CZFileExcludedFromTargets=[]
			CZFilesToSetAsSource=[]
			for fileItem in duplicateSet:
				CZFileIndexNum+=1
				targetMatched=False
				if fileItemsCountLikelyExist <= 1:
					print(
						"Only one file likely exists in this duplicate set, skipping further checks for this set."
					)
					# todo: check if biggest file missing.
					break
				# fileItem=orjson.loads(orjson.dumps(fileItem))

	# print("File item:", fileItem, "type:", type(fileItem))
				filePathInSet = Path(fileItem["path"])
				# print("File path in the set:", filePathInSet)
				# sys.exit()
				if filePathInSet.is_file(): # todo: add premission detection
					print("File path in the set exists:", filePathInSet)
				else:
					print("File path in the set does not exist:", filePathInSet)
					fileItemsCountLikelyExist -= 1
				for dst in dirsToSetAsTarget:
					pattern = re.sub(
						r"\\\\\\\\", r"\\\\", rf"^{re.escape(dst)}(\\|/).+"
					)  # Fix broken backslashes in pattern
					# pattern = re.sub(r"\\ ",r" ",pattern)
					print(pattern)
					# print(fileItem["path"])
					# print(str(filePathInSet))
					# tsdsds="S:\\.+"
					# print(tsdsds)
					# tsdsdsraw=r"S:\\.+"
					# tsdsdsraw=r"^.*S:\\btdl\\adult\\\[F.*"
					# print(tsdsdsraw)
					# if re.match(r"^S.+", r"S:\btdl\adult\[forget skyrim]_b68c01f9c98de57b3f268c0c389689547cfc24a5\Clc-Devil-光辉.mp4"):
					# if re.match("^S.+", fileItem["path"]):
					# if re.match(pattern, fileItem["path"],flags=re.IGNORECASE):
					# 	print("matched var pattern!")
					# if re.match(tsdsdsraw, fileItem["path"],flags=re.IGNORECASE):
					# 	print("matched tsdsdsraw!")
					# sys.exit()
					if re.match(pattern, fileItem["path"],flags=re.IGNORECASE):
						print(
							"File path in the set to be handle:", fileItem["path"]
						)
						CZFilesToOperatePerSet.append(fileItem)
						targetMatched=True
						break
				if not targetMatched:
					CZFileExcludedFromTargets.append(fileItem)
				if len(CZFilesToOperatePerSet) == len(duplicateSet):
						
					print(
						"All files in this duplicate set are to handle, picking the largest file as source."
					)
					try:
						CZFilesSources, CZFilesToOperatePerSet = setFitSourceAndTargetFiles(
							CZFilesToOperatePerSet
						)
					except Exception as e:
						sys.exit(f"Failed to set biggest file as source. Error: {e}")
					break
				elif len(CZFilesToOperatePerSet) < len(duplicateSet) and CZFileIndexNum==len(duplicateSet):
					# print(len(duplicateSet))
					# print(f"CZFileExcludedFromTargets: {CZFileExcludedFromTargets}")
					#todo: Force select biggest file.
					#todo: Select biggest file in this duplicate set by default.
					if forceSelectBiggestSource:
						CZFilesToSetAsSource=CZFileExcludedFromTargets
					else:
						for fi in CZFileExcludedFromTargets:
							if dirsToSetAsSource:
								sourceMatched=False
								for dss in dirsToSetAsSource:
									pattern = re.sub(
										r"\\\\\\\\", r"\\\\", rf"^{re.escape(dss)}(\\|/).+"
									)  # Fix broken backslashes in pattern
									if re.match(pattern, fi["path"],flags=re.IGNORECASE):
										print(
											"File path in the set matched source pattern:", fi["path"]
										)
										CZFilesToSetAsSource.append(fi)
										sourceMatched=True
										break
								# if sourceMatched==False:
								# 	sys.exit(f"{fi}")
							else:
								if autoSelectSource:
									CZFilesToSetAsSource=CZFileExcludedFromTargets
								else:
									sys.exit(f"Exited. file path: {fi["path"]}, index: {CZFileIndexNum}")
								#todo: Add auto selecter.
					if not CZFilesToSetAsSource:
						sys.exit("Can't find any files to be set as source.")
					CZFilesSources=getBiggestFile(CZFilesToSetAsSource) # todo: add an option to select the file by real size.
					print(f"Source file: {CZFilesSources}")
					# sys.exit()
					# CZFilesSources=CZFilesSource
				elif len(CZFilesToOperatePerSet) > len(duplicateSet):
					sys.exit("WTF? Too many items!")
			# sys.exit()
			if CZFilesToOperatePerSet:
				fileItemsToHandlePaths = [
					fi['path'] for fi in CZFilesToOperatePerSet
				]
				print(
					"Files to handle in this duplicate set:", fileItemsToHandlePaths
				)
				# print("Files to handle in this duplicate set:", fileItemsToHandle)
				# CZFilesToOperatePerSetMapping[duplicateSetKey] = {}
				# CZFilesToOperatePerSetMapping[duplicateSetKey]["source"
				#                                               ] = CZFilesSources
				# CZFilesToOperatePerSetMapping[duplicateSetKey][
				#     "target"] = CZFilesToOperatePerSet
				CZFilesToOperatePerSetMapping["source"
															] = CZFilesSources
				CZFilesToOperatePerSetMapping[
					"target"] = CZFilesToOperatePerSet
				# pprint(fileItemsToHandleStructure)
				# print(CZFilesToOperatePerSetMapping)
				# sys.exit()
				CZFilesToOperateMapping.append(CZFilesToOperatePerSetMapping)
		# pprint(CZFilesToOperateMapping)
		pprint(CZFilesToOperateMapping)
		fileOperateSet: dict = {}
		systemCLICommands: str = ""
		targetCommands: list = []
		backupCommands: list = []
		targetFilePaths=[]
		# sys.exit()
		for fileOperateSet in CZFilesToOperateMapping:
			for targetFile in fileOperateSet["target"]:
				targetFilePath = Path(targetFile["path"])
				targetFilePaths.append(targetFilePath)
				if useCommands:
					targetCommands.append(generateCLICommands(operation=CZFileOperationModeFull,target=targetFilePath,source=fileOperateSet["source"]["path"]))
					if CZFileOperationMode=="o":
						targetFileBackupPath=PurePath(r"S:\btdl\test") / targetFilePath.name
						backupCommands.append(generateCLICommands(operation="overwrite",target=targetFileBackupPath,source=targetFilePath,toNewFile=True))

		if CZFileOperationMode=="o":
			afsasaf="\n".join(str(fi) for fi in targetFilePaths)
			print(afsasaf)
		if useCommands:
			print("generated backup commands:")
			for c in backupCommands:
				print(c)
			print("generated commands:")
			for c in targetCommands:
				print(c)


			# if CZFileOperationMode == "t":
			# 	pass
			# elif CZFileOperationMode == "d":
			# 	CZFilesToBeDeleted.extend(CZFilesToOperatePerSet)
			# elif CZFileOperationMode == "o":
			# 	CZFilesToBeOverwritten.extend(CZFilesToOperatePerSet)
			# else:
			# 	print("Unknown file operation mode: ", CZFileOperationMode)
		# sys.exit()
	# print(CZJsonFilePath.name)
	# sys.exit()
	if args.i:
		CZJsonNew={}
		for duplicateSetKey in czkawkaJsonFromFile:
			# print(duplicateSetKey)
			if n2LevelInSets:
				duplicateSet = czkawkaJsonFromFile.get(str(duplicateSetKey))[0]
			else:
				duplicateSet = czkawkaJsonFromFile.get(str(duplicateSetKey))
			fileItemsCountLikelyExist = len(duplicateSet)
			CZFileIndexNum=0
			if duplicateSetKey not in CZJsonNew:
				CZJsonNew[duplicateSetKey]=[]
			for fileItem in duplicateSet:
				CZFileIndexNum+=1
				if fileItemsCountLikelyExist <= 1:
					print(
						"Only one file likely exists in this duplicate set, skipping further checks for this set."
					)
					if duplicateSetKey in CZJsonNew:
						del CZJsonNew[duplicateSetKey]
					# todo: check if biggest file missing.
					break
				filePathInSet = Path(fileItem["path"])
				# print("File path in the set:", filePathInSet)
				# sys.exit()
				if filePathInSet.is_file(): # todo: add premission detection
					print("File path in the set exists:", filePathInSet)
					CZJsonNew[duplicateSetKey].append(fileItem)
				else:
					print("File path in the set does not exist:", filePathInSet)
					fileItemsCountLikelyExist -= 1
		if CZJsonDestination:
			# writeToFile()
			writeToFile(
				str(CZJsonDestination / CZJsonFilePath.name),
				orjson.dumps(CZJsonNew, option=orjson.OPT_INDENT_2).decode('utf-8'),
				openmode='w',
				file_encoding='utf-8'
			)
		else:
			pprint(CZJsonNew)
		if CZJsonNew:
			CZJsoninput=CZJsonNew
		else:
			CZJsoninput=czkawkaJsonFromFile
		if args.cs:
			releasableSpace=0
			FirstKeyCZJsonInput = next(iter(CZJsoninput))
			# print("FirstKeyCZJsonInput: ", FirstKeyCZJsonInput)
			# print(type(CZJsoninput.get(FirstKeyCZJsonInput)[0]))
			if isinstance(
				CZJsoninput.get(FirstKeyCZJsonInput)[0], dict
			):
				n2LevelInSets = False
			elif isinstance(
				CZJsoninput.get(FirstKeyCZJsonInput)[0], list
			):
				if CZJsoninput.get(FirstKeyCZJsonInput
										)[0][0].get("path"):
					n2LevelInSets = True
				else:
					sys.exit("Unknown structure in czkawka json file.")
			else:
				sys.exit("Unknown structure in czkawka json file.")
			for duplicateSetKey in CZJsoninput:
				# print(duplicateSetKey)
				if n2LevelInSets:
					duplicateSet = CZJsoninput.get(str(duplicateSetKey))[0]
				else:
					duplicateSet = CZJsoninput.get(str(duplicateSetKey))
				# pprint(duplicateSet)
				duplicateSet.sort(key=lambda x: x['size'], reverse=True)
				for fi in duplicateSet[1:]:
					releasableSpace+=fi["size"]
				
			print(convert_size(releasableSpace))

if __name__ == "__main__":
	main()

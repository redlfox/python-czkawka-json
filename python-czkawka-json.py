# from mimetypes import init
# import time
import re
import sys

try:
	import orjson
except ImportError:
	import json as orjson
import argparse
import platform
from pathlib import Path, PurePath
from pprint import pprint

import pandas as pd
from core.cli_command import generateCLICommands
from core.files_info import convert_size, get_encoding

# import configparser
from utils_s import (  # noqa: F401
	getFileOperationMode,
	readFromFile,
	readFromFileE,
	writeToFile,
)

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
			sys.exit("Unknown structure in czkawka json file.")
	else:
		sys.exit("Unknown structure in czkawka json file.")
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

def main() -> None:

	# init()

	parser = argparse.ArgumentParser(description="Tool to process Czkawka JSON files.")
	parser.add_argument("input", nargs="?", default=None, help="Czkawka JSON file path to process.")
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
	    help="[Placeholder Option]Excluded directory paths in json that will be ignored. Separate multiple directories with comma."
	)
	parser.add_argument(
	    "-edf", "-excluded-dir-file", default=None,
	    help="[Placeholder Option]Excluded directory paths in json that will be ignored. Read directories from given file."
	)
	parser.add_argument("-r", "-read", action="store_true", help="Optional, test")
	parser.add_argument("-dry", action="store_true", help="[Placeholder Option]Do not perform any file operations.")
	parser.add_argument(
	    "-g", "-get-metadata", action="store_true", help="[Placeholder Option]Get file metadata by file type."
	)
	parser.add_argument(
	    "-m", "-mode", default=None, help="File operation mode. \"d\" for delete, \"t\" for trash, \"o\" for overwrite."
	)
	parser.add_argument(
	    "-nb", "-no-backup", action="store_true", help="[Placeholder Option]Do not create backup before overwrite files."
	)
	parser.add_argument(
	    "-s", "-skip-compare", action="store_true",
	    help="[Placeholder Option]Do not compare files in duplicate sets to filter files for operation."
	)
	parser.add_argument("-d", "-destination", default=None, help="Set destination for saving generated json files.")
	parser.add_argument("-bd", "-backup-destination", default=None, help="backup-destination.")
	parser.add_argument(
	    "-p", "-json-prefix", default=None, help="Optional, set prefix of filenames for generated json files to save."
	)
	parser.add_argument("-rs", "-real-sizes", action="store_true", help="Optional, use real file sizes.")
	parser.add_argument("-db", "-debug", action="store_true", help="[Placeholder Option]Show debug information.")
	parser.add_argument(
	    "-c", "-command", action="store_true", help="Give commands for file operations instead of using python."
	)
	parser.add_argument("-o", "-organize", action="store_true", help="Organize files from Czkawka json files.")
	parser.add_argument("-i", "-interact", action="store_true", help="Interact with Czkawka json files.")
	parser.add_argument(
	    "-cs", "-calculate-space", action="store_true", help="Calculate releasable space from Czkawka json files."
	)
	parser.add_argument("-ns", "-no-slc", action="store_true", help="Skip the set if all files be setted as targets.")
	args = parser.parse_args()
	if not args.input:
		parser.print_help()

	CZJsonFilePath: Path | None = Path(args.input) if args.input else None
	if CZJsonFilePath and CZJsonFilePath.is_file():
		print("Czkawka JSON file path from argument:", CZJsonFilePath)
	else:
		print("No valid Czkawka JSON file path provided.")
		sys.exit()
	
	cc1 = 0

	if args.o:
		cc1 += 1
	if args.i:
		cc1 += 1
	if cc1 > 1:
		sys.exit("Can not use mutiple mode at same time.")
	try:
		CZJsonFromFile = orjson.loads(readFromFileE(CZJsonFilePath, "utf-8"))
	except Exception as e:
		sys.exit(f"Failed to load json file. Error: {e}")
		return None
	isListJson, n2LevelInSets = detectJsonStructure(CZJsonFromFile)
	# sys.exit()
	# with open(CZJsonFilePath, "r", encoding=get_encoding(CZJsonFilePath)) as f:
	CZJsonDestination = PurePath()
	if args.d:
		CZJsonDestination = PurePath(args.d)
	skipCompare: bool = args.s
	if args.o:
		dirsToSetAsSource = []
		dirsToSetAsTarget = []
		excludedDirs = []
		forceSelectBiggestSource = False
		autoSelectSource = False
		useCommands = False
		if args.sd:
			try:
				dirsToSetAsSource = re.sub("\'|\"", "", args.sd).split(",")
			except Exception as e:
				print(f"Failed to parse source directories. Error: {e}")
				sys.exit()
				return None
		if dirsToSetAsSource:
			print("Source directories from argument: ")
			pprint(dirsToSetAsSource)
		if args.td:
			try:
				dirsToSetAsTarget = re.sub("\'|\"", "", args.td).split(",")
			except Exception as e:
				sys.exit(f"Failed to parse target directories. Error: {e}")
				return None
		if args.tdf:
			dirsToSetAsTarget.extend((readFromFile(args.tdf)).splitlines())
		if dirsToSetAsTarget:
			print("Target directories from argument: ")
			pprint(dirsToSetAsTarget)
		if args.ed:
			try:
				excludedDirs = args.ed.split(",")
			except Exception as e:
				print(f"Failed to parse excluded directories. Error: {e}")
				sys.exit()
				return None
		if args.edf:
			excludedDirs.extend((readFromFile(args.edf)).splitlines())
		if excludedDirs:
			print("Excluded directories from argument: ")
			pprint(excludedDirs)
		if args.c:
			useCommands = True
		# File operation mode.
		CZFileOperationMode: str | None = str(args.m) if args.input else None
		CZFileOperationModeFull = getFileOperationMode(CZFileOperationMode)

		# CZFilesToBeOverwritten = []
		# CZFilesToBeDeleted = []
		CZFilesToOperateMapping = []
		# Proccessing every duplicate set in czkawka json data
		for duplicateSetKey in CZJsonFromFile:
			# print(duplicateSetKey)
			if isListJson:
				duplicateSet = duplicateSetKey
			elif n2LevelInSets:
				duplicateSet = CZJsonFromFile.get(str(duplicateSetKey))[0]
			else:
				duplicateSet = CZJsonFromFile.get(str(duplicateSetKey))
			fileItemsCountLikelyExist = len(duplicateSet)
			CZFilesToOperatePerSet: list = []
			CZFilesToOperatePerSetMapping: dict = {}
			CZFilesSources = None
			CZFileIndexNum = 0
			CZFileExcludedFromTargets = []
			CZFilesToSetAsSource = []
			# print(dirsToSetAsTarget[0])
			# print(re.escape(dirsToSetAsTarget[0]))
			# print(rf"^{re.escape(re.sub(r"(\\|/)$","",dirsToSetAsTarget[0]))}(\\|/).+")
			# sys.exit()
			for fileItem in duplicateSet:
				CZFileIndexNum += 1
				targetMatched = False

				# print("File item:", fileItem, "type:", type(fileItem))
				filePathInSet = Path(fileItem['path'])
				# print("File path in the set:", filePathInSet)
				# sys.exit()
				if filePathInSet.is_file():  # TODO: add premission detection
					print("File path in the set exists:", filePathInSet)
				else:
					print("File path in the set does not exist:", filePathInSet)
					fileItemsCountLikelyExist -= 1
				if fileItemsCountLikelyExist <= 1:
					print("Only one file likely exists in this duplicate set, skipping further checks for this set.")
					# TODO: check if biggest file missing.
					break
				for dst in dirsToSetAsTarget:
					pattern = rf"^{re.escape(re.sub(r"(\\|/)$","",dst))}(\\|/).+"
					# TODO: Handle files with case conflict in a same directory.
					# Czkawka converts path to lowercase.
					if re.match(pattern, fileItem['path'], flags=re.IGNORECASE):
						print("File path in the set to be handle:", fileItem['path'])
						CZFilesToOperatePerSet.append(fileItem)
						targetMatched = True
						break
				if not targetMatched:
					CZFileExcludedFromTargets.append(fileItem)
				if len(CZFilesToOperatePerSet) == len(duplicateSet):
					if args.ns:
						print("All files in this duplicate set are to handle. Skipping this set.")
					else:
						print("All files in this duplicate set are to handle. Picking the largest file as source.")
						try:
							CZFilesSources, CZFilesToOperatePerSet = setFitSourceAndTargetFiles(CZFilesToOperatePerSet)
							CZFilesSources = CZFilesSources[0]
						except Exception as e:
							sys.exit(f"Failed to set biggest file as source. Error: {e}")
					break
				elif len(CZFilesToOperatePerSet) < len(duplicateSet) and CZFileIndexNum == len(duplicateSet):
					# print(len(duplicateSet))
					# print(f"CZFileExcludedFromTargets: {CZFileExcludedFromTargets}")
					#TODO: Force select biggest file.
					#TODO: Select biggest file in this duplicate set by default.
					if forceSelectBiggestSource:
						CZFilesToSetAsSource = CZFileExcludedFromTargets
					else:
						for fi in CZFileExcludedFromTargets:
							if dirsToSetAsSource:
								sourceMatched = False
								for dss in dirsToSetAsSource:
									pattern = rf"^{re.escape(re.sub(r"(\\|/)$","",dss))}(\\|/).+"
									if re.match(pattern, fi['path'], flags=re.IGNORECASE):
										print("File path in the set matched source pattern:", fi['path'])
										CZFilesToSetAsSource.append(fi)
										sourceMatched = True
										break
							else:
								if autoSelectSource:
									CZFilesToSetAsSource = CZFileExcludedFromTargets
								else:
									sys.exit(f"Exited. file path: {fi['path']}, index: {CZFileIndexNum}")
								#TODO: Add auto selecter.
					if not CZFilesSources:
						if not CZFilesToSetAsSource:
							print("Can't find any files to be set as source. Skipping this set.")
							# sys.exit("Can't find any files to be set as source.")
						else:
							CZFilesSources = getBiggestFile(
							    CZFilesToSetAsSource
							)  # TODO: add an option to select the file by real size.
							print(f"Source file: {CZFilesSources}")
							# sys.exit()
							# CZFilesSources=CZFilesSource
				elif len(CZFilesToOperatePerSet) > len(duplicateSet):
					sys.exit("WTF? Too many items!")
			# sys.exit()
			if not CZFilesSources:
				continue
			if CZFilesToOperatePerSet:
				fileItemsToHandlePaths = [fi['path'] for fi in CZFilesToOperatePerSet]
				print("Files to handle in this duplicate set:", fileItemsToHandlePaths)
				CZFilesToOperatePerSetMapping["source"] = CZFilesSources
				CZFilesToOperatePerSetMapping["target"] = CZFilesToOperatePerSet
				# pprint(fileItemsToHandleStructure)
				# print(CZFilesToOperatePerSetMapping)
				# sys.exit()
				CZFilesToOperateMapping.append(CZFilesToOperatePerSetMapping)
		# pprint(CZFilesToOperateMapping)
		pprint(CZFilesToOperateMapping)
		fileOperateSet: dict = {}
		targetCommands: list = []
		backupCommands: list = []
		targetFilePaths = []
		# sys.exit()

		for fileOperateSet in CZFilesToOperateMapping:
			for targetFile in fileOperateSet["target"]:
				targetFilePath = Path(targetFile['path'])
				targetFilePaths.append(targetFilePath)
				if useCommands:
					targetCommands.append(
					    generateCLICommands(
					        operation=CZFileOperationModeFull, target=targetFilePath,
					        source=fileOperateSet['source']['path']
					    )
					)
					if CZFileOperationMode == "o":
						if args.bd:
							targetFileBackupPath = PurePath(args.bd) / targetFilePath.name
							backupCommands.append(
							    generateCLICommands(
							        operation="overwrite", target=targetFileBackupPath, source=targetFilePath,
							        toNewFile=True
							    )
							)

		if useCommands:
			if backupCommands:
				print("generated backup commands:")
				for c in backupCommands:
					print(c)
			print("generated file commands:")
			for c in targetCommands:
				print(c)

	if args.i:
		if isListJson:
			CZJsonNew = []
		else:
			CZJsonNew = {}
		CZJsonFromFileItemIndex = 0
		for duplicateSetKey in CZJsonFromFile:
			# print(duplicateSetKey)
			# print(CZJsonFromFileItemIndex)
			if isListJson:
				duplicateSet = CZJsonFromFile[CZJsonFromFileItemIndex]
			elif n2LevelInSets:
				duplicateSet = CZJsonFromFile.get(str(duplicateSetKey))[0]
			else:
				duplicateSet = CZJsonFromFile.get(str(duplicateSetKey))
			
			fileItemsCountLikelyExist = len(duplicateSet)
			CZFileIndexNum = 0
			CZJsonSetTemp = []
			skipSet = False

			for fileItem in duplicateSet:
				CZFileIndexNum += 1
				filePathInSet = Path(fileItem['path'])
				# print("File path in the set:", filePathInSet)
				# sys.exit()
				if filePathInSet.is_file():  # TODO: add premission detection
					print("File path in the set exists:", filePathInSet)
					CZJsonSetTemp.append(fileItem)
				else:
					print("File path in the set does not exist:", filePathInSet)
					fileItemsCountLikelyExist -= 1
				if fileItemsCountLikelyExist <= 1:
					print("Only one file likely exists in this duplicate set, skipping further checks for this set.")
					# TODO: check if biggest file missing.
					skipSet = True
					break
			
			if not skipSet:
				if isListJson:
					CZJsonNew.append(CZJsonSetTemp)
				else:
					CZJsonNew[duplicateSetKey] = CZJsonSetTemp
			CZJsonFromFileItemIndex += 1
		if CZJsonDestination and not args.dry:
			writeToFile(
			    str(CZJsonDestination / CZJsonFilePath.name),
			    orjson.dumps(CZJsonNew, option=orjson.OPT_INDENT_2).decode('utf-8'), openmode='w', file_encoding='utf-8'
			)
		else:
			if args.dry:
				print("Dry test.")
			pprint(CZJsonNew)
		if CZJsonNew:
			CZJsonInput = CZJsonNew
		else:
			CZJsonInput = CZJsonFromFile
		if args.cs:
			releasableSpace = 0
			isListJson, n2LevelInSets = detectJsonStructure(CZJsonFromFile)
			CZJsonInputItemIndex = 0
			for duplicateSetKey in CZJsonInput:
				# print(duplicateSetKey)
				if isListJson:
					duplicateSet = CZJsonInput[CZJsonInputItemIndex]
				elif n2LevelInSets:
					duplicateSet = CZJsonInput.get(str(duplicateSetKey))[0]
				else:
					duplicateSet = CZJsonInput.get(str(duplicateSetKey))
				# pprint(duplicateSet)
				duplicateSet.sort(key=lambda x: x['size'], reverse=True)
				for fi in duplicateSet[1:]:
					releasableSpace += fi["size"]
				CZJsonInputItemIndex += 1

			print("Releasable space:", convert_size(releasableSpace))

if __name__ == "__main__":
	main()

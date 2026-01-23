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
from utils_s import get_encoding, writeToFile
import pandas as pd

# Set file with biggest size as source, if multiple files have same size, set the one with shortest path depth, if still multiple files, set the one with longest file name length as source
def setFitSourceAndTargetFiles(CZFileItems: list) -> None:
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
def generateSystemCLICommands(operation:str, source:Path, target:Path,forceExecute:bool) -> str:
	if operation == "delete":
		return f'del "{target}"'
	elif operation == "overwrite":
		return f'copy /Y "{source}" "{target}"'
	else:
		return ""
def main() -> None:

	init()

	parser = argparse.ArgumentParser(description="Tool to process Czkawka JSON files.")
	parser.add_argument("input", nargs="?", default=None, help="Czkawka JSON file path to process.")
	parser.add_argument("-td", "-target-dir", default=None, help="Optional, target directory path that will be processed. Separate multiple directories with comma.")
	parser.add_argument("-m", "-mode", default="t", help="Optional, file operation mode. \"d\" for delete, \"t\" for trash, \"o\" for overwrite. Default is trash.")
	args = parser.parse_args()

	CZJsonFilePath:Path|None=Path(args.input) if args.input else None
	if CZJsonFilePath and CZJsonFilePath.is_file():
		print("Czkawka JSON file path from argument: ", CZJsonFilePath)
	else:
		print("No valid Czkawka JSON file path provided.")
		sys.exit()
	dirsToSetAsTarget: str |None = args.td if args.td else None
	if dirsToSetAsTarget:
		try:
			dirsToSetAsTarget = dirsToSetAsTarget.split(",")
			print("Target directories from argument: ")
			pprint(dirsToSetAsTarget)
		except Exception as e:
			print(f"Failed to parse target directories. Error: {e}")
			sys.exit()
			return None
	# File operation mode, use trash mode if not provided or invalid
	CZFileOperationMode:str|None=str(args.m) if args.input else None
	if CZFileOperationMode and CZFileOperationMode in ["d", "t", "o"]:
		print("File operation mode from argument: ", CZFileOperationMode)
	else:
		print("No valid file operation mode provided, defaulting to trash.")
		CZFileOperationMode = "t"
	# print("File operation mode argument: ", CZFileOperationMode)
	with open(CZJsonFilePath, "r", encoding=get_encoding(CZJsonFilePath)) as f:
		try:
			czkawkaJsonFromFile = orjson.loads(f.read())
		except Exception as e:
			# handle_caught_exception(e, known=True)
			print(f"Failed to load json file. Error: {e}")
			sys.exit()
			return None            
	CZFilesToBeOverwritten = []
	CZFilesToBeDeleted = []
	CZFilesToOperateMapping = []
	FirstKeyCzkawkaJsonFromFile = next(iter(czkawkaJsonFromFile))
	                                                                                                   # print("FirstKeyCzkawkaJsonFromFile: ", FirstKeyCzkawkaJsonFromFile)
	# print(type(czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0]))
	if isinstance(czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0], dict):
		n2LevelInSets = False
	elif isinstance(czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0], list):
		if czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0][0].get("path"):
			n2LevelInSets = True
		else:
			print("Unknown structure in czkawka json file.")
			sys.exit()
	else:
		print("Unknown structure in czkawka json file.")
		sys.exit()
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
		for fileItem in duplicateSet:
			if fileItemsCountLikelyExist <= 1:
				print(
				    "Only one file likely exists in this duplicate set, skipping further checks for this set."
				)
				break
			                                                                                                   # fileItem=orjson.loads(orjson.dumps(fileItem))

# print("File item:", fileItem, "type:", type(fileItem))
			filePathInSet = Path(fileItem["path"])
			# print("File path in the set:", filePathInSet)
			# sys.exit()
			if filePathInSet.is_file():
				print("File path in the set exists:", filePathInSet)
			else:
				print("File path in the set does not exist:", filePathInSet)
				fileItemsCountLikelyExist -= 1
			for dirToSetAsTarget in dirsToSetAsTarget:
				pattern = re.sub(
				    r"\\\\\\\\", r"\\\\", rf"^{re.escape(dirToSetAsTarget)}.*"
				) # Fix broken backslashes in pattern
				if re.match(pattern, fileItem["path"]):
					print("File path in the set to be handle:", fileItem["path"])
					CZFilesToOperatePerSet.append(fileItem)
					if len(CZFilesToOperatePerSet) >= len(duplicateSet):
						print(
						    "All files in this duplicate set are to handle, picking the largest file as source."
						)
						try:
							CZFilesSources, CZFilesToOperatePerSet = setFitSourceAndTargetFiles(
							    CZFilesToOperatePerSet
							)
						except Exception as e:
							print(
							    f"Failed to set biggest file as source. Error: {e}"
							)
							sys.exit()
						break
					break
		if CZFilesToOperatePerSet:
			fileItemsToHandlePaths = [fi['path'] for fi in CZFilesToOperatePerSet]
			print(
			    "Files to handle in this duplicate set:", fileItemsToHandlePaths
			)
			# print("Files to handle in this duplicate set:", fileItemsToHandle)
			CZFilesToOperatePerSetMapping[duplicateSetKey] = {}
			CZFilesToOperatePerSetMapping[duplicateSetKey]["source"
			                                           ] = CZFilesSources
			CZFilesToOperatePerSetMapping[duplicateSetKey]["target"
			                                           ] = CZFilesToOperatePerSet
			# pprint(fileItemsToHandleStructure)
			# print(CZFilesToOperatePerSetMapping)
			# sys.exit()
			CZFilesToOperateMapping.append(CZFilesToOperatePerSetMapping)
	# pprint(CZFilesToOperateMapping)
	# pprint(CZFilesToOperateMapping)
	fileOperateSet:dict={}
	systemCLICommands:str=""
	for fileOperateSetKey in CZFilesToOperateMapping:
		fileOperateSet = CZFilesToOperateMapping.get(str(fileOperateSetKey))
		for targetFile in fileOperateSet["target"]:
			targetFilePath = Path(targetFile["path"])
		if CZFileOperationMode == "t":
			pass
		elif CZFileOperationMode == "d":
			CZFilesToBeDeleted.extend(CZFilesToOperatePerSet)
		elif CZFileOperationMode == "o":
			CZFilesToBeOverwritten.extend(CZFilesToOperatePerSet)
		else:
			print("Unknown file operation mode: ", CZFileOperationMode)
	# sys.exit()
	# writeToFile(rf"I:\pythontest\python-czkawka-json-test\New Folder", "ssss")

if __name__ == "__main__":
	main()

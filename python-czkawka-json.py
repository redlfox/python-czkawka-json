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
	pprint(CZFilesSizes)
	CZFilesEqualSizeSorted = []
	CZFilesSorted = []
	CZFilesSorting = []
	CZFilesSources = []
	CZFilesTargets = []
	CZFilesTargetsTemp = []
	while len(CZFilesSizes) > 0:
		CZFilesEqualSize = [
		    fi for fi in CZFileItems if fi["size"] == CZFilesSizes[0]
		]
		print("czkawkaFileItemsInASize:", CZFilesEqualSize)
		CZFilesEqualSizeSorted = []
		if len(CZFilesEqualSize) > 1:
			CZFilesEqualSize.sort(
			    key=lambda x: len(Path(x['path']).parts), reverse=False
			)
			CZFilesEqualSizePathDepths = [
			    len(Path(fi['path']).parts) for fi in CZFilesEqualSize
			]
			print(
			    "czkawkaFileItemsInASizePathLength:", CZFilesEqualSizePathDepths
			)
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
					print("czkawkaFileItemsInSameDepth:", CZFilesInSameDepth)
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

def main() -> None:
	jsonFile = Path(
	    rf"I:\codebase\python\pythontest\python-czkawka-json-test\results_duplicates_pretty.json"
	)
	with open(jsonFile, "r", encoding=get_encoding(jsonFile)) as f:
		try:
			czkawkaJsonFromFile = orjson.loads(f.read())
		except Exception as e:
			# handle_caught_exception(e, known=True)
			print(f"Failed to load json file. Error: {e}")
			sys.exit()
			return None
	dirsToOverwrite = [
	    r"I:\codebase\python\pythontest\python-czkawka-json-test\asffa",
	    r"I:\codebase\python\pythontest\python-czkawka-json-test\\"
	]
	fileOperationMode = "overwrite"                                                                   # overwrite or delete
	fileItemsToBeOverwritten = []
	fileItemsToBeDeleted = []
	FirstKeyCzkawkaJsonFromFile = next(iter(czkawkaJsonFromFile))
	                                                                                                   # print("FirstKeyCzkawkaJsonFromFile: ", FirstKeyCzkawkaJsonFromFile)
	if czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0] == dict:
		n2LevelInSets = False
	elif czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0][0].get("path"):
		n2LevelInSets = True
	else:
		print("Unknown structure in czkawka json file.")
		sys.exit()
	for duplicateSetKey in czkawkaJsonFromFile:
		print(duplicateSetKey)
		if n2LevelInSets:
			duplicateSet = czkawkaJsonFromFile.get(str(duplicateSetKey))[0]
		else:
			duplicateSet = czkawkaJsonFromFile.get(str(duplicateSetKey))
		fileItemsCountLikelyExist = len(duplicateSet)
		fileItemsToHandle: list = []
		fileItemsToHandleStructure: dict = {}
		largestFileItem = None
		for fileItem in duplicateSet:
			if fileItemsCountLikelyExist <= 1:
				print(
				    "Only one file likely exists in this duplicate set, skipping further checks for this set."
				)
				break
			                                                                                                   # fileItem=orjson.loads(orjson.dumps(fileItem))

# print("File item:", fileItem, "type:", type(fileItem))
			filePathInSet = Path(fileItem["path"])
			# print("File path in set:", filePathInSet)
			# sys.exit()
			if filePathInSet.is_file():
				print("File path in set exists:", filePathInSet)
			else:
				print("File path in set does not exist:", filePathInSet)
				fileItemsCountLikelyExist -= 1
			for dirToOverwrite in dirsToOverwrite:
				pattern = re.sub(
				    r"\\\\\\\\", r"\\\\", rf"^{re.escape(dirToOverwrite)}.*"
				)
				if re.match(pattern, fileItem["path"]):
					print("File path in set to be handle:", fileItem["path"])
					fileItemsToHandle.append(fileItem)
					if len(fileItemsToHandle) >= len(duplicateSet):
						print(
						    "All files in this duplicate set are to handle, picking the largest file as source."
						)
						try:
							largestFileItem, fileItemsToHandle = setFitSourceAndTargetFiles(
							    fileItemsToHandle
							)
						except Exception as e:
							print(
							    f"Failed to set biggest file as source. Error: {e}"
							)
							sys.exit()
						break
					break
		if fileItemsToHandle:
			fileItemsToHandlePaths = [fi['path'] for fi in fileItemsToHandle]
			print(
			    "Files to handle in this duplicate set:", fileItemsToHandlePaths
			)
			# print("Files to handle in this duplicate set:", fileItemsToHandle)
			fileItemsToHandleStructure[duplicateSetKey] = {}
			fileItemsToHandleStructure[duplicateSetKey]["source"
			                                           ] = largestFileItem
			fileItemsToHandleStructure[duplicateSetKey]["target"
			                                           ] = fileItemsToHandle
			# pprint(fileItemsToHandleStructure)
			# print(fileItemsToHandleStructure)
			sys.exit()
			if fileOperationMode == "overwrite":
				fileItemsToBeOverwritten.extend(fileItemsToHandle)
			elif fileOperationMode == "delete":
				fileItemsToBeDeleted.extend(fileItemsToHandle)
			else:
				print("Unknown file operation mode: ", fileOperationMode)
	sys.exit()
	print(list(czkawkaJsonFromFile)[0])
	print(type(czkawkaJsonFromFile))
	n1stElement = czkawkaJsonFromFile["4"]
	print(n1stElement)
	print(type(n1stElement))
	n1stElement1stFileInfo = n1stElement[0][0]
	print(n1stElement1stFileInfo)
	print(type(n1stElement1stFileInfo))
	print(n1stElement1stFileInfo["path"])
	czkawkaJsonFromFile["369"] = [[]]
	writeToFile(rf"I:\pythontest\python-czkawka-json-test\New Folder", "ssss")

if __name__ == "__main__":
	main()

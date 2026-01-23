import asyncio, jsonpickle, yaml, sys, os, time, re, argparse, random
try:
	import orjson
	import orjson as json
except ImportError:
	import json as orjson
from pprint import pprint
from pathlib import Path, PurePath
import argparse
import configparser
from utils_s import accelerator, get_encoding, writeToFile

def setBiggestFileAsSource(czkawkaFileItems:list)->None:
	if not czkawkaFileItems or len(czkawkaFileItems) == 0:
		return (None, [])
	if len(czkawkaFileItems) < 2:
		return (None, [])
	czkawkaFileItems.sort(key=lambda x: x['size'], reverse=True)
	# asfasfas=[]
	# for fff in czkawkaFileItems:
	#     asfasfas.append(fff['path'])
	asfasfas=[fff['size'] for fff in czkawkaFileItems]
	pprint(asfasfas)
	czkawkaFileItemsInASizeSorted=[]
	czkawkaFileItemsSorted=[]
	czkawkaFileItemsSorting=[]
	while len(asfasfas)>0:
		czkawkaFileItemsInASize=[fi for fi in czkawkaFileItems if fi["size"]==asfasfas[0]]
		print("czkawkaFileItemsInASize:", czkawkaFileItemsInASize)
		czkawkaFileItemsInASizeSorted=[]
		if len(czkawkaFileItemsInASize)>1:
			czkawkaFileItemsInASize.sort(key=lambda x: len(Path(x['path']).parts), reverse=False)
			czkawkaFileItemsInASizePathLength=[len(Path(fi['path']).parts) for fi in czkawkaFileItemsInASize]
			print("czkawkaFileItemsInASizePathLength:", czkawkaFileItemsInASizePathLength)
			while len(czkawkaFileItemsInASizePathLength)>0:
				czkawkaFileItemsInSameDepth=[fi for fi in czkawkaFileItemsInASize if len(Path(fi['path']).parts)==czkawkaFileItemsInASizePathLength[0]]
				if len(czkawkaFileItemsInSameDepth)>1:
					czkawkaFileItemsInSameDepth.sort(key=lambda x: len(PurePath(x['path']).name), reverse=True)
					print("czkawkaFileItemsInSameDepth:", czkawkaFileItemsInSameDepth)
				czkawkaFileItemsInASizePathLength=[pd for pd in czkawkaFileItemsInASizePathLength if pd!=czkawkaFileItemsInASizePathLength[0]]
				czkawkaFileItemsInASizeSorted.extend(czkawkaFileItemsInSameDepth)
			# print("czkawkaFileItemsInASizeSorted:", czkawkaFileItemsInASizeSorted)

				# if len(czkawkaFileItemsInASize)>1:

			# sys.exit()
			# czkawkaFileItemsInASize.sort(key=lambda x: len(PurePath(x['path']).name), reverse=True)
		else:
			czkawkaFileItemsInASizeSorted.extend(czkawkaFileItemsInASize)
		asfasfas=[sz for sz in asfasfas if sz!=asfasfas[0]]
		czkawkaFileItemsSorting.extend(czkawkaFileItemsInASizeSorted)
	czkawkaFileItemsSorted=czkawkaFileItemsSorting
	czkawkaFileItemsSorting=[]
	largestFileItem=czkawkaFileItemsSorted[0] if czkawkaFileItemsSorted else None
	if largestFileItem:
		print("Largest file to keep: ", largestFileItem)
		czkawkaFileItemstarget=[fi for fi in czkawkaFileItems if fi["path"]!=largestFileItem["path"]]
		return([largestFileItem],czkawkaFileItemstarget)
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
	dirsToOverwrite=[r"I:\codebase\python\pythontest\python-czkawka-json-test\asffa",r"I:\codebase\python\pythontest\python-czkawka-json-test\\"]
	fileOperationMode="overwrite"  # overwrite or delete
	fileItemsToBeOverwritten=[]
	fileItemsToBeDeleted=[]
	FirstKeyCzkawkaJsonFromFile=next(iter(czkawkaJsonFromFile))
	# print("FirstKeyCzkawkaJsonFromFile: ", FirstKeyCzkawkaJsonFromFile)
	if czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0]==dict:
		n2LevelInSets=False
	elif czkawkaJsonFromFile.get(FirstKeyCzkawkaJsonFromFile)[0][0].get("path"):
		n2LevelInSets=True
	else:
		print("Unknown structure in czkawka json file.")
		sys.exit()
	for duplicateSetKey in czkawkaJsonFromFile:
		print(duplicateSetKey)
		if n2LevelInSets:
			duplicateSet=czkawkaJsonFromFile.get(str(duplicateSetKey))[0]
		else:
			duplicateSet=czkawkaJsonFromFile.get(str(duplicateSetKey))
		fileItemsCountLikelyExist=len(duplicateSet)
		fileItemsToHandle:list=[]
		fileItemsToHandleStructure:dict={}
		largestFileItem=None
		for fileItem in duplicateSet:
			if fileItemsCountLikelyExist<=1:
				print("Only one file likely exists in this duplicate set, skipping further checks for this set.")
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
				fileItemsCountLikelyExist-=1
			for dirToOverwrite in dirsToOverwrite:
				pattern=re.sub(r"\\\\\\\\",r"\\\\",rf"^{re.escape(dirToOverwrite)}.*")
				# print(pattern)
				if re.match(pattern, fileItem["path"]):
					print("File path in set to be handle:", fileItem["path"])
					fileItemsToHandle.append(fileItem)
					if len(fileItemsToHandle)>=len(duplicateSet):
						print("All files in this duplicate set are to handle, skipping further checks for this set.")
						# print(fileItemsToHandle)
						# sys.exit()
						# fileItemsToHandle=[]
						largestFileItem,fileItemsToHandle=setBiggestFileAsSource(fileItemsToHandle)
						break
					break
		if fileItemsToHandle:
			print("Files to handle in this duplicate set:", fileItemsToHandle)
			fileItemsToHandleStructure[duplicateSetKey]={}
			fileItemsToHandleStructure[duplicateSetKey]["source"]=largestFileItem
			fileItemsToHandleStructure[duplicateSetKey]["target"]=fileItemsToHandle
			pprint(fileItemsToHandleStructure)
			print(fileItemsToHandleStructure)
			sys.exit()
			if fileOperationMode=="overwrite":
				fileItemsToBeOverwritten.extend(fileItemsToHandle)
			elif fileOperationMode=="delete":
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

from mimetypes import init
import sys
# import time
import re
try:
	import orjson
except ImportError:
	import json as orjson  # noqa: F401
from pprint import pprint
from pathlib import Path, PurePath
import argparse
# import configparser
from utils_s import writeToFile, readFromFile, readFromFileE, getFileOperationMode, getBatchFileExt
from core.files_info import get_encoding, convert_size  # noqa: F401
from core.cli_command import generateCLICommands
import pandas as pd

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
	if args.o:
		dirsToSetAsSource = []
		dirsToSetAsTarget = []
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

		targetCommands: list = []
		backupCommands: list = []
		targetFilePaths = []
		for targetPath in pathListInput:
			targetFilePath = Path(targetPath)
			# CZFilesToOperatePerSetMapping: dict = {}
			CZFilesSources = None
			CZFileIndexNum = 0
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

if __name__ == "__main__":
	main()

# Modified from https://github.com/Steamauto/Steamauto
import os

# import math
import platform
import random
import re
from pathlib import Path, PurePath

from core.files_info import get_encoding


def compare_version(ver1, ver2):
	version1_parts = ver1.split('.')
	version2_parts = ver2.split('.')

	for i in range(max(len(version1_parts), len(version2_parts))):
		v1 = int(version1_parts[i]) if i < len(version1_parts) else 0
		v2 = int(version2_parts[i]) if i < len(version2_parts) else 0

		if v1 < v2:
			return -1
		elif v1 > v2:
			return 1

	return 0

def is_subsequence(s, t):
	t_index = 0
	s_index = 0
	while t_index < len(t) and s_index < len(s):
		if s[s_index] == t[t_index]:
			s_index += 1
		t_index += 1
	return s_index == len(s)

def debugprint(printvar):  # wip
	print(f'{printvar}')
	for attr in dir(printvar):
		print('testasfa.%s = %r' % (attr, getattr(printvar, attr)))
	return

def writeToFile(file_path, writeContext, openmode: str = 'a', file_encoding: str = 'utf-8'):  # wip
	file_path = Path(file_path)
	if file_encoding == 'auto':
		file_encoding = get_encoding(file_path)
	file_path_dir = Path(PurePath(file_path).parent)
	print(os.path.dirname(file_path))
	if not Path(file_path).exists():
		if not Path(file_path_dir).exists():
			file_path_dir.mkdir()
		file_path.touch()
	elif not file_path.is_file():
		raise Exception('Targret is not a file.')
	with file_path.open(mode=openmode, encoding=file_encoding) as file:
		if openmode == 'a':
			file.write('\n' + str(writeContext))
		elif openmode == 'w':
			file.write(str(writeContext))

def readFromFile(file_path) -> str:
	file_path = Path(file_path)
	if not Path(file_path).exists():
		raise Exception('File not exist.')
	elif not file_path.is_file():
		raise Exception('Targret is not a file.')
	with file_path.open(mode='r', encoding=get_encoding(file_path)) as file:
		return file.read()

def readFromFileE(file_path, file_encoding) -> str:
	file_path = Path(file_path)
	if not Path(file_path).exists():
		raise Exception('File not exist.')
	elif not file_path.is_file():
		raise Exception('Targret is not a file.')
	with file_path.open(mode='r', encoding=file_encoding) as file:
		return file.read()

def getFileOperationMode(fileOperationMode):
	if fileOperationMode and fileOperationMode in ["d", "t", "o"]:
		if fileOperationMode == "d":
			fileOperationModeFull = "delete"
		if fileOperationMode == "t":
			fileOperationModeFull = "trash"
		if fileOperationMode == "o":
			fileOperationModeFull = "overwrite"
		print("File operation mode from argument:", fileOperationModeFull)
		return fileOperationModeFull
	else:
		print("No valid file operation mode provided, won't perform any file operations.")

def getBatchFileExt():
	SystemType = platform.system()
	if SystemType == "Linux" or SystemType == "Darwin":
		return "sh"
	elif SystemType == "Windows":
		return "bat"
	else:
		print("Unsupported system type for file operations:", SystemType)
		return ""

# Modified from https://github.com/Steamauto/Steamauto
import os
from pathlib import Path, PurePath
import random
import re

import chardet
import math
import platform

def convert_size(size_bytes):
	"""
    Converts a byte value into a human-readable string (B, KB, MB, etc.).
    """
	if size_bytes == 0:
		return "0B"
	size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
	# Calculate the appropriate unit index using logarithm
	i = int(math.floor(math.log(size_bytes, 1024)))
	# Ensure index is within the range of size_name
	i = min(i, len(size_name) - 1)
	# Calculate the converted value
	p = 1024**i
	return f"{round(size_bytes / p, 2)} {size_name[i]}"

# 用于解决读取文件时的编码问题
def get_encoding(file_path):
	if not os.path.exists(file_path):
		return 'utf-8'
	with open(file_path, 'rb') as f:
		data = f.read()
		charset = chardet.detect(data)['encoding']
	return charset

def calculate_sha256(file_path: str) -> str:
	import hashlib

	hash_sha256 = hashlib.sha256()
	with open(file_path, 'rb') as f:
		for chunk in iter(lambda: f.read(8192), b''):
			hash_sha256.update(chunk)
	return hash_sha256.hexdigest()

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

class accelerator:
	def __call__(self, r):
		domain_list = ['steamcommunity-a.akamaihd.net', ]
		match = re.search(r'(https?://)([^/\s]+)', r.url)
		if match:
			domain = match.group(2)
			r.headers['Host'] = domain
			r.url = re.sub(r'(https?://)([^/\s]+)(.*)', r'\1' + random.choice(domain_list) + r'\3', r.url, )
		return r

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

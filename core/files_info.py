import os
import chardet
import math
import hashlib

# 用于解决读取文件时的编码问题
def get_encoding(file_path):
	if not os.path.exists(file_path):
		return 'utf-8'
	with open(file_path, 'rb') as f:
		data = f.read()
		charset = chardet.detect(data)['encoding']
	return charset

def calculate_sha256(file_path: str) -> str:

	hash_sha256 = hashlib.sha256()
	with open(file_path, 'rb') as f:
		for chunk in iter(lambda: f.read(8192), b''):
			hash_sha256.update(chunk)
	return hash_sha256.hexdigest()

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

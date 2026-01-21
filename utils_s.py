#Modified from https://github.com/Steamauto/Steamauto
import os
from pathlib import Path,PurePath
import random
import re

import chardet
# 用于解决读取文件时的编码问题
def get_encoding(file_path):
    if not os.path.exists(file_path):
        return "utf-8"
    with open(file_path, "rb") as f:
        data = f.read()
        charset = chardet.detect(data)["encoding"]
    return charset


def calculate_sha256(file_path: str) -> str:
    import hashlib

    hash_sha256 = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_sha256.update(chunk)
    return hash_sha256.hexdigest()


def compare_version(ver1, ver2):
    version1_parts = ver1.split(".")
    version2_parts = ver2.split(".")

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
        domain_list = [
            "steamcommunity-a.akamaihd.net",
        ]
        match = re.search(r"(https?://)([^/\s]+)", r.url)
        if match:
            domain = match.group(2)
            r.headers["Host"] = domain
            r.url = re.sub(r"(https?://)([^/\s]+)(.*)", r"\1" + random.choice(domain_list) + r"\3", r.url)
        return r


def is_subsequence(s, t):
    t_index = 0
    s_index = 0
    while t_index < len(t) and s_index < len(s):
        if s[s_index] == t[t_index]:
            s_index += 1
        t_index += 1
    return s_index == len(s)

def debugprint(printvar): #wip
    print(f"{printvar}")
    for attr in dir(printvar):
        print("testasfa.%s = %r" % (attr, getattr(printvar, attr)))
    return

def writeToFile(file_path:Path,writeContext,openmode="a"): # wip
    file_path_dir = os.path.dirname(Path(file_path))
	if not Path(file_path).exists():
		os.mkdir(file_path_dir)
	with open(file_path, openmode, encoding='utf-8') as file:
		if openmode=="a":
			file.write("\n" + str(writeContext))
		elif openmode=="w":
			file.write(str(writeContext))
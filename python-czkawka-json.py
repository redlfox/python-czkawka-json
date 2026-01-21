import asyncio, orjson, jsonpickle, yaml, sys, os, time, re, argparse, random
from pathlib import Path, PurePath
import argparse
import configparser
from utils_s import accelerator, get_encoding,writeToFile
def main() -> None:
	config_file = Path(rf"I:\pythontest\python-czkawka-json-test\results_duplicates_pretty.json")
	with open(config_file, "r", encoding=get_encoding(config_file)) as f:
		try:
			czkawkaJsonFromFile = orjson.loads(f.read())
		except Exception as e:
			# handle_caught_exception(e, known=True)
			# logger.error("检测到" + STEAM_ACCOUNT_INFO_FILE_PATH + "格式错误, 请检查配置文件格式是否正确! ")
			print(f"Failed to load json file. Error: {e}")
			sys.exit()
			return None
	print(list(czkawkaJsonFromFile)[0])
	print(type(czkawkaJsonFromFile))
	n1stElement=czkawkaJsonFromFile["4"]
	print(n1stElement)
	print(type(n1stElement))
	n1stElement1stFileInfo=n1stElement[0][0]
	print(n1stElement1stFileInfo)
	print(type(n1stElement1stFileInfo))
	print(n1stElement1stFileInfo["path"])
	czkawkaJsonFromFile["369"]=[[]]
if __name__ == "__main__":
    main()
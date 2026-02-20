
import os
import platform
from pathlib import Path, PurePath

from core.files_info import getEncoding


def writeToFile(file_path, writeContext, openmode: str = 'a', file_encoding: str = 'utf-8'):  # wip
    file_path = Path(file_path)
    if file_encoding == 'auto':
        file_encoding = getEncoding(file_path)
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


def readFromFileE(file_path, file_encoding: str = None) -> str:
    file_path = Path(file_path)
    if not Path(file_path).exists():
        raise Exception('File not exist.')
    elif not file_path.is_file():
        raise Exception('Targret is not a file.')
    if not file_encoding:
        try:
            import chardet

            encoding = getEncoding(file_path)
        except ImportError:
            encoding = "utf-8"
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
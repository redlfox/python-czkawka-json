import platform
import re
from pathlib import Path, PurePath


def fixCliPath(PathStr: str):
    SystemType = platform.system()
    if SystemType == "Linux" or SystemType == "Darwin":
        if re.match(r".*([`'!]).*", PathStr):  # Also for cygwin and msys2
            pathStrCli = re.sub(r"([\s`'!()&])", r"\\\1", PathStr)
        else:
            pathStrCli = '"{}"'.format(PathStr)
    elif SystemType == "Windows":
        pathStrCli = '"{}"'.format(PathStr)
    else:
        pathStrCli = '"{}"'.format(PathStr)
    return pathStrCli


def generateCLICommands(
    operation: str,
    target: Path,
    source: Path = None,
    forceConfirm: bool = False,
    gioTrash: bool = False,
    toNewFile: bool = False,
) -> str:
    SystemType = platform.system()
    commandArguments = ""
    forceExecuteOption = ""
    newFileOption = ""
    if not target:
        raise  # TODO: Adding exception type
    targetStr = fixCliPath(str(target))
    if operation == "trash":
        if SystemType == "Linux" or SystemType == "Darwin":
            if not gioTrash:
                return f'trash-put {targetStr}'
            elif gioTrash:
                if forceConfirm:
                    forceExecuteOption = "-f "
                return f'gio trash {forceExecuteOption}{targetStr}'
        elif SystemType == "Windows":
            print("Windows trash operation is not implemented yet.")
            return f'{targetStr}'
    elif operation == "delete":
        if SystemType == "Linux" or SystemType == "Darwin":
            if not forceConfirm:
                commandArguments = "-i "
            else:
                commandArguments = "-f "
            return f'rm {commandArguments}{targetStr}'
        elif SystemType == "Windows":
            if not forceConfirm:
                return f'del /P {targetStr}'
            else:
                return f'del /F /Q {targetStr}'
    elif operation == "overwrite":
        if not source:
            raise  # TODO: Adding exception type
        if SystemType == "Linux" or SystemType == "Darwin":
            if not forceConfirm:
                return f'cp -i "{source}" {targetStr}'
            else:
                return f'cp -f "{source}" {targetStr}'
        elif SystemType == "Windows":
            if forceConfirm:
                forceExecuteOption = "/Y "
            if toNewFile:
                newFileOption = "echo f | "
            return f'{newFileOption}xcopy {forceExecuteOption}"{source}" {targetStr}'
    else:
        print("Unknown file operation:", operation)
        return ""
    if not (
        SystemType == "Linux"
        or SystemType == "Darwin"
        or SystemType == "Windows"
    ):
        print("Unsupported system type for file operations:", SystemType)
        return ""

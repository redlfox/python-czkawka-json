# Czkawka Json Tool

## About the project
The **Czkawka json tool** is a specialized utility designed to process and manage duplicate file information exported from [Czkawka](https://github.com/qarmin/czkawka). It allows users to filter, organize, and automate file operations (such as trashing, deleting, or overwriting) based on duplicate sets. The tool can intelligently select "source" and "target" files using customizable logic (e.g., file size, path depth) and generate CLI commands for safer bulk operations.

## Precautions
- **Dry Run:** Always use the `-dry` flag (if applicable) or the `-c` (command) mode to preview operations before execution.
- **Backups:** Ensure you have backups of important data. While the tool includes a "trash" mode, direct deletions are permanent.
- **Safety:** This project avoids unsafe practices like `eval()`. Use only the provided CLI arguments to interact with the logic.
- **Data Integrity:** The tool relies on the structure of the JSON exported by Czkawka. Modifications to the source JSON may cause unexpected behavior.

## Installation
1.  **Python:** Ensure Python 3.6+ is installed.
2.  **Dependencies:**
    ```bash
    pip install pandas orjson
    ```
    Alternatively, you can install python dependencies using `python3 -m pip install` command.

3.  **Formatting (Optional):**
    ```bash
    pip install ruff
    ```

## Usage
### Core Command
- python-czkawka-json.py
```text
usage: python-czkawka-json.py [-h] [-sd SOURCE_DIR] [-td TARGET_DIR] [-tdf TARGET_DIR_FILE] [-ed EXCLUDED_DIR] [-edf EXCLUDED_DIR_FILE] [-r] [--dry] [-e] [-g] [-m {d,t,o}] [-nb] [-s] [-d DESTINATION]
                              [-bd BACKUP_DESTINATION] [-p JSON_PREFIX] [-rs] [-db] [-c] [-o] [-i] [-cs] [-ns]
                              [input]

Advanced tool for processing Czkawka duplicate JSON exports.
Enables intelligent filtering, selection, and bulk management of duplicate file sets.
Supports generating CLI scripts for safe, external execution of file operations.
With the -o argument provided and other options satisfied, target files will be deleted, trashed or overwritten. Excluded items will be ignored and source items will become sources for overwritting.

positional arguments:
  input                 Path to the Czkawka JSON export file.

options:
  -h, --help            show this help message and exit
  -sd, --source-dir SOURCE_DIR
                        Comma-separated list of directories to treat as 'source' locations for json will be processed.
                        Files in these directories are prioritized as originals.
  -td, --target-dir TARGET_DIR
                        Comma-separated list of directories to treat as 'target' locations for json will be processed. Treat all files in duplicate sets as targets if no arguments of -td or -tdf given.
  -tdf, --target-dir-file TARGET_DIR_FILE
                        Path to a text file containing list of directories to treat as 'target' locations for json will be processed. Treat all files in duplicate sets as targets if no -arguments of -td or -tdf given. 
  -ed, --excluded-dir EXCLUDED_DIR
                        [Placeholder] Comma-separated list of directories to ignore during processing.
  -edf, --excluded-dir-file EXCLUDED_DIR_FILE
                        [Placeholder] Path to a text file containing list of directories to ignore during processing.
  -r, --read            Optional: test
  --dry                 [Placeholder] Dry run: Simulate operations without modifying the filesystem.
  -e, --encoding        Encoding to use when reading and writing files. (e.g., utf-8, ascii, gbk) Use utf-8 encoding by default.
  -g, --get-metadata    [Placeholder] Retrieve additional file metadata (e.g., bitrates, resolutions).
  -m, --mode {d,t,o}    Operation mode:
                          d: Delete files permanently
                          t: Move files to trash
                          o: Overwrite files with source
  -nb, --no-backup      [Placeholder]Disable automatic backup creation before 'overwrite' operations.
  -s, --skip-compare    Skip detailed file comparison within duplicate sets.
  -d, --destination DESTINATION
                        Directory to save the processed JSON output.
  -bd, --backup-destination BACKUP_DESTINATION
                        Directory for storing backup files during overwrites.
  -p, --json-prefix JSON_PREFIX
                        Prefix to add to the filenames of generated JSON files with this program.
  -rs, --real-sizes     Use actual file sizes instead of metadata from the JSON.
  -db, --debug          [Placeholder]Display verbose debug information during execution.
  -c, --command         Generate shell commands instead of performing actions directly via Python.
  -o, --organize        Run the organization mode to identify source and target files for every set and do file operations with them from Czkawka json files. Can't use along with -i flag.
  -i, --interact        Run the interactive to read info or filtering (e.g., verifying file existence) from Czkawka json files. Can't use along with -o flag.
  -cs, --calculate-space
                        Calculate the maxinum releasable space from Czkawka json files.
  -ns, --no-slc         Skip sets where all files are currently marked as targets (safety check).
```

### File Management Helper
- fmhelper.py
```text
usage: fmhelper.py [-h] [-sd SOURCE_DIR] [-td TARGET_DIR] [-tdf TARGET_DIR_FILE] [-ed EXCLUDED_DIR] [-edf EXCLUDED_DIR_FILE] [-r] [--dry] [-e] [-fe] [-ff] [-m MODE] [-nb] [-s] [-d DESTINATION]
                   [-bd BACKUP_DESTINATION] [-p JSON_PREFIX] [-rs] [-db] [-c] [-o] [-i] [-cs] [-ns]
                   [input]

Tool to process files.

positional arguments:
  input                 file path to process.

options:
  -h, --help            show this help message and exit
  -sd, --source-dir SOURCE_DIR
                        Comma-separated list of directories to treat as 'source' locations.
  -td, --target-dir TARGET_DIR
                        Comma-separated list of directories to treat as 'target' locations.
  -tdf, --target-dir-file TARGET_DIR_FILE
                        Optional: target directories in json that will be processed, treat all files in duplicate sets as targets if blank. Read directories from given file.
  -ed, --excluded-dir EXCLUDED_DIR
                        Optional: Comma-separated list of ignored directories.
  -edf, --excluded-dir-file EXCLUDED_DIR_FILE
                        [Placeholder] Path to a text file containing list of directories to ignore.
  -r, -read             Optional: test
  --dry                 [Placeholder] Dry run: Simulate operations without modifying the filesystem.
  -e, --encoding        Encoding to use when reading and writing files. (e.g., utf-8, ascii, gbk) Use utf-8 encoding by default.
  -fe, --filter-exist   Filter to include existing files and folders.
  -ff, --filter-file    Filter to include existing files.
  -m, --mode MODE       Optional: file operation mode. "d" for delete, "t" for trash, "o" for overwrite.
  -nb, --no-backup      Optional: do not create backup before overwrite files.
  -s, --skip-compare    Optional: do not compare files in duplicate sets to filter files for operation.
  -d, --destination DESTINATION
                        Optional: set destination for saving generated json files.
  -bd, --backup-destination BACKUP_DESTINATION
                        backup-destination.
  -p, --json-prefix JSON_PREFIX
                        Optional: set prefix of filenames for generated json files to save.
  -rs, --real-sizes     Optional: use real file sizes.
  -db, --debug          Optional: show debug information.
  -c, --command         Optional: give commands for file operations instead of using python.
  -o, --organize        Organize files from files.
  -i, --interact        Interact with files.
  -cs, --calculate-space
                        Calculate releasable space from files.
  -ns, --no-slc         test.
```

### Examples
- **Preview Operations:** Generate a batch script to trash files instead of deleting them directly.
  ```bash
  python python-czkawka-json.py -sd "/path/to/source" -td "/path/to/target" -o -m t -c duplicates.json
  ```
- **Space Calculation:** Calculate how much space can be released from a duplicate set.
  ```bash
  python python-czkawka-json.py -i -cs duplicates.json
  ```
```bash
# Generate commands to trash matched target files in the given json if atleast one source file matched.
python3 python-czkawka-json.py -sd [source_path_string] -td [target_path_string] -ns -o -m t -c [json_file]

# Generate a new json and save to [FileDestination] with same filename. And calculate releasable space from the new json.
python3 python-czkawka-json.py -i -cs -d [FileDestination] [json_file]
```

## Technologies
- Python 3
- Pandas (for data processing)
- orjson (for high-performance JSON parsing)

## Project Structure
<details>
<summary>Project Repository Tree</summary>

```text
.
├── core/                       # Core domain logic
│   ├── cli_command.py          # CLI command generation logic
│   ├── files_info.py           # File metadata and encoding helpers
│   ├── files_op.py             # File operations (delete, trash, overwrite)
│   ├── simple_snippets.py      # Snippet management
│   └── __init__.py
├── fmhelper.py                 # File management entry point
├── GEMINI.md                   # Project mandates and coding standards
├── python-czkawka-json.py      # Main entry point for JSON processing
├── ruff.toml                   # RUFF linting and formatting config
├── README.md                   # Project documentation
├── LICENSE                     # MIT License
└── .gitignore                  # Git ignore rules
```
</details>

## Troubleshooting
- **`ImportError: No module named 'orjson'`**: The tool prefers `orjson` for performance but can fall back to the standard `json` library. Install it via `pip install orjson` for best results.
- **`Unknown structure in czkawka json file`**: Ensure your JSON was exported from a compatible version of Czkawka.
- **Permission Denied**: Run the script with necessary permissions if operating on system-protected directories.
- Create a issue if there's something wrong.

## Collaborating
This project follows strict coding and naming conventions. Before contributing, please review **`GEMINI.md`**.
- **Naming:** Follow the `[Type]Subject[Attributes]` lowerCamelCase rule.
- **Formatting:** Code must be formatted using RUFF.
- **Commit Style:** Ensure commit messages are concise and explain the "why" behind changes.

## Tools Used
Gemini

## License
Czkawka Json Tool is licensed under the [MIT License](LICENSE)

Copyright © 2026 Redlfox

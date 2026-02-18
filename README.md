# python-czkawka-json
## python-czkawka-json.py
Useage:
```
Tool to process Czkawka JSON files.

positional arguments:
  input                 Czkawka JSON file path to process.

options:
  -h, --help            show this help message and exit
  -sd, -source-dir SD   Set source directories and match source items in them for json will be processed. Separate
                        multiple directories with comma.
  -td, -target-dir TD   Set target directories and match target items in them for json will be processed. Treat all
                        files in duplicate sets as targets if blank. Separate multiple directories with comma.
  -tdf, -target-dir-file TDF
                        Read target directories from each line of a plain text file and match target items in them for
                        json will be processed. Treat all files in duplicate sets as targets if blank. Read
                        directories from the given file.
  -ed, -excluded-dir ED
                        [Placeholder Option]Excluded directories will be ignored for json will be processed. Separate
                        multiple directories with comma.
  -edf, -excluded-dir-file EDF
                        [Placeholder Option]Excluded directories will be ignored for json will be processed. Read
                        directories from the given file.
  -r, -read             Optional, test
  -dry                  [Placeholder Option]Do not perform any file operations.
  -g, -get-metadata     [Placeholder Option]Get file metadata by file type.
  -m, -mode M           File operation mode. "d" for delete, "t" for trash, "o" for overwrite.
  -nb, -no-backup       [Placeholder Option]Do not create backup before overwrite files.
  -s, -skip-compare     [Placeholder Option]Do not compare files in duplicate sets to filter files for operation.
  -d, -destination D    Set destination for saving generated json files.
  -bd, -backup-destination BD
                        backup-destination.
  -p, -json-prefix P    Set prefix of filenames for generated json files to save.
  -rs, -real-sizes      Optional, use real file sizes.
  -db, -debug           [Placeholder Option]Show debug information.
  -c, -command          Give commands for file operations instead of using python.
  -o, -organize         Organize files from Czkawka json files.
  -i, -interact         Interact with Czkawka json files.
  -cs, -calculate-space
                        Calculate releasable space from Czkawka json files.
  -ns, -no-slc          Skip the set if all files be setted as targets.
```
Example:
```
# Generate commands to trash matched target files in the given json if atleast one source file matched.
python3 python-czkawka-json.py -sd [source_path_string] -td [target_path_string] -ns -o -mode t -c [json_file]

# Generate a new json and save to [FileDestination] with same filename. And calculate releasable space from the new json.
python3 python-czkawka-json.py -i -cs -d [FileDestination] [json_file]
```
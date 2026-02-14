# python-czkawka-json
Tool to process Czkawka JSON files.

positional arguments:
  input                 Czkawka JSON file path to process.

options:
  -h, --help            show this help message and exit
  -sd, -source-dir SD   Set source directory paths in json that will be processed. Separate multiple directories with
                        comma.
  -td, -target-dir TD   Optional, set target directory paths in json that will be processed, treat all files in
                        duplicate sets as targets if blank. Separate multiple directories with comma.
  -tdf, -target-dir-file TDF
                        Optional, target directory paths in json that will be processed, treat all files in duplicate
                        sets as targets if blank. Read directories from given file.
  -ed, -excluded-dir ED
                        Optional, excluded directory paths in json that will be ignored. Separate multiple directories
                        with comma.
  -edf, -excluded-dir-file EDF
                        Optional, excluded directory paths in json that will be ignored. Read directories from given
                        file.
  -r, -read             Optional, test
  -dry                  Optional, do not perform any file operations.
  -g, -get-metadata     Optional, get file metadata by file type.
  -m, -mode M           Optional, file operation mode. "d" for delete, "t" for trash, "o" for overwrite.
  -nb, -no-backup       Optional, do not create backup before overwrite files.
  -s, -skip-compare     Optional, do not compare files in duplicate sets to filter files for operation.
  -d, -destination D    Optional, set destination for saving generated json files.
  -bd, -backup-destination BD
                        backup-destination.
  -p, -json-prefix P    Optional, set prefix of filenames for generated json files to save.
  -rs, -real-sizes      Optional, use real file sizes.
  -db, -debug           Optional, show debug information.
  -c, -command          Optional, give commands for file operations instead of using python.
  -o, -organize         Organize files from Czkawka json files.
  -i, -interact         Interact with Czkawka json files.
  -cs, -calculate-space
                        Calculate releasable space from Czkawka json files.
  -ns, -no-slc          test.

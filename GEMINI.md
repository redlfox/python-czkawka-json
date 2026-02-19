# Project: Czkawka json tool

## Role
I am a senior software engineer and collaborative peer programmer dedicated to the **Czkawka json tool**. My mission is to ensure high-quality, maintainable, and idiomatic Python code by strictly adhering to the project's unique naming conventions and structural integrity. I provide expert guidance on refactoring, feature implementation, and architectural consistency while prioritizing safety and performance.

## Repository Structure Rules
- **Entry Points:** Primary execution logic is contained in `python-czkawka-json.py` and `fmhelper.py`.
- **Core Logic (`core/`):** All domain-specific, reusable logic must be organized within the `core/` directory. Each module must have a clear, singular responsibility (e.g., `cli_command.py` for CLI generation, `files_info.py` for file metadata).
- **Organization over Convenience:** 
    - NEVER add generic `utils.py` or similar unorganized modules.
    - `utils_s.py` is reserved for shared, low-level internal helpers. If logic becomes specialized, move it to a appropriate module in `core/`.
    - Avoid adding new files to the root directory unless they are primary entry points or essential project configurations.
- **Naming Files:** Use `snake_case` for all file and directory names.

## General Instructions
- **Safety First:** Avoid unsafe code execution methods like `eval()` or `exec()`.
- **Namespace Integrity:** Avoid variable or module name collisions with the Python Standard Library (e.g., `math`, `json`, `os`) or generic terms (e.g., `data`, `info`).
- **Dependency Management:** Verify existing library usage (e.g., `orjson`, `pandas`) before introducing new dependencies.

## Coding Style & Guidelines

### Code Formatting
- **Standard:** Strictly follow the RUFF formatting standard defined in `ruff.toml`.
- **Imports:** Use RUFF for automated import sorting and linting.
- **Typing:** Use type hints for all function signatures and complex variable declarations to ensure clarity and safety.

### Naming Conventions
- **Variable Names:** 
    - Structure: `[Type]Subject[Attributes]` in `lowerCamelCase`.
    - Logic: Put words describing the subject's type *before* the subject, and attributes describing the subject *after* the subject based on their correlation.
    - Example: "I like this cake" -> `cakeThisILike`; "A new JSON string" -> `jsonStringNew`.
    - Articles: "a", "an", and "the" should be removed.
- **The 'CZ' Prefix Exception:**
    - If a variable starts with the identifier `CZ` followed by a capitalized word (e.g., `Files`), the first three characters (e.g., `CZF`) must remain uppercased to form a unified, indivisible word unit (e.g., `CZFiles`).
    - This unit is treated as a single word and its casing is preserved even at the beginning of a name, overriding standard `lowerCamelCase`.
- **Function Names:** 
    - Use **normal word order** in `lowerCamelCase` (e.g., `detectJsonStructure`, `getBiggestFile`).

### Error Handling & Validation
- **Explicit Exceptions:** Always use explicit exception types; avoid bare `except:`.
- **Pre-emptive Checks:** Always verify file existence, permissions, and directory validity before performing filesystem operations.
- **Reproducibility:** For bug fixes, create a reproduction script or test case before applying the fix.

## README Output

### Rules
- **Outline:** Always include "About the project", "Precautions", "Installation", "Usage", "Structure", "Troubleshooting", "Collaborating", and "License".
- **Code Blocks:** Do not modify or remove existing code blocks in the README (e.g., CLI usage outputs).
- **Structure Visualization:** Use a folded `<details>` tree for the project structure. If the file level is > 5 or there are > 15 files (excluding the main directory), ensure deep nesting is minimized or folded.

### Template

Use README.template as the template for README.md

### Repository Structure Reference
```text
.
├── core/                       # Core domain logic
│   ├── cli_command.py          # CLI command generation logic
│   ├── files_info.py           # File metadata and encoding helpers
│   ├── snippet_files.py        # Snippet management
│   └── __init__.py
├── fmhelper.py                 # File management entry point
├── GEMINI.md                   # Project mandates and coding standards
├── python-czkawka-json.py      # Main entry point for JSON processing
├── ruff.toml                   # RUFF linting and formatting config
├── utils_s.py                  # Shared internal utility helpers
├── README.md                   # Project documentation
└── .gitignore                  # Git ignore rules
```


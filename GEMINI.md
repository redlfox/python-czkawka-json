# Project: Czkawka json tool
<!-- Help me improve GEMINI.md for this repository. Generate your role for this repository. Make repository structure rules based on the files. Give detailed development guidelines for this repository. -->
## General Instructions
- Follow the existing coding style.
- Avoid not safe code. E.g. "eval()"
- Avoid name Collisions. E.g. "math", "data"
- Avoid putting function in a not unorganized module. E.g. "utils.py"
## Coding Style
### Code Formatting
- Follow the RUFF formatting standard defined in ruff.toml.
- Follow the RUFF formatting standard defined for sorting imports.
### Naming
- Use lowerCamelCase. In a variable name, put words describe the subject's type before the subject and put words describe the subject's attributes by the correlation with the subject after the subject. E.g. "jsonStringNew", "I like this cake" -> "cakeThisILike".
- In a variable name, "a"，"an"，"the" can be removed.
- In a function name, use normal word order.
<!-- - From the beginning of a common name, if one single character and the next character is not uppercased, it shouldn't treat as a single word until the next character is uppercased. This rule is above the basic name parsing rule. -->
- If a variable name starts with the identifier 'CZ' followed by a capitalized word (e.g., 'Files'), the first three characters ('CZF') must remain uppercased to form a unified, indivisible word unit (e.g., 'CZFiles'). This specific unit is treated as a single word and its casing is preserved even at the beginning of a name, overriding standard lowerCamelCase.

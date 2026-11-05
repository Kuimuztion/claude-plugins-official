# Code Simplifier Plugin

Simplifies and refines code for clarity, consistency, and maintainability
while preserving exact functionality.

## Overview

The `code-simplifier` plugin provides a specialized agent that analyzes
recently modified code and applies structural refinements without altering
runtime behavior.

## Key Principles

1. **Preserve Functionality**: Never change what the code does, only how it
   is structured.
2. **Apply Project Standards**: Follow established coding conventions from
   `CLAUDE.md` and the existing codebase.
3. **Enhance Clarity**: Reduce unnecessary nesting, eliminate redundancy,
   and avoid nested ternary operators.
4. **Maintain Balance**: Prefer readable, explicit code over overly compact
   one-liners.

## Installation

```bash
/plugin install code-simplifier@claude-plugins-official
```

## License

Apache License 2.0

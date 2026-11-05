# Session Report Plugin

Generate a self-contained, explorable HTML report of Claude Code session usage
from local `~/.claude/projects` transcripts.

## Overview

The `session-report` skill analyzes local session transcripts and produces an
interactive HTML report covering:

- Token consumption and cost breakdown by project
- Prompt cache hit rates and cache break diagnostics
- Subagent and skill invocation metrics
- Top most expensive prompts and optimization callouts

## Usage

Invoke the skill in Claude Code:

```bash
/session-report
```

You can also specify a time window (default is `7d`), such as `24h`, `30d`, or
`all`.

## Installation

```bash
/plugin install session-report@claude-plugins-official
```

## License

Apache License 2.0

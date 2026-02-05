# ClawHub Submission Package

## Skill Information

| Field | Value |
|-------|-------|
| **Name** | swarm-janitor |
| **Display Name** | Swarm Janitor |
| **Description** | Enterprise-grade cleanup tool for orphaned OpenClaw subagent processes with SuperMemory archival |
| **Version** | 1.0.0 |
| **Author** | OpenClawdad (Redclay) |
| **License** | MIT |
| **Homepage** | https://github.com/LvcidPsyche/swarm-janitor |
| **Repository** | https://github.com/LvcidPsyche/swarm-janitor |

## Category

**Maintenance & Operations**

## Tags

- maintenance
- cleanup
- subagents
- memory-management
- enterprise
- archival
- safety

## Requirements

- Python 3.8+
- OpenClaw 2026.2.0+
- SuperMemory skill (optional, for archival)

## Features

✅ Dry-run mode (preview before action)
✅ SuperMemory archival before deletion
✅ Configurable retention policies
✅ Active process detection
✅ Detailed logging and reporting
✅ Cron-friendly for automation
✅ JSON output for monitoring

## Installation

```bash
# Via ClawHub
openclaw skills install swarm-janitor

# Via GitHub
openclaw skills install https://github.com/LvcidPsyche/swarm-janitor
```

## Quick Start

```bash
# Preview what would be cleaned
python3 ~/.openclaw/workspace/skills/swarm-janitor/scripts/swarm_janitor.py --dry-run

# Archive and clean
python3 ~/.openclaw/workspace/skills/swarm-janitor/scripts/swarm_janitor.py --archive --clean
```

## Safety Certifications

- ✅ Never deletes active sessions
- ✅ Archives before deletion
- ✅ Confirmation prompts for bulk deletes
- ✅ Dry-run by default

## Support

- Issues: https://github.com/LvcidPsyche/swarm-janitor/issues
- Documentation: See SKILL.md in repository

## Changelog

### v1.0.0 (2026-02-05)
- Initial release
- Session scanning and classification
- SuperMemory archival support
- Configurable retention policies
- Enterprise safety features

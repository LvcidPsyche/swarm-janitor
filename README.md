# 🧹 Swarm Janitor

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-blue.svg)](https://openclaw.ai)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

Enterprise-grade cleanup tool for OpenClaw subagent management. Automatically identifies and cleans up orphaned subagent sessions while preserving important work through archival.

## ✨ Features

- 🔍 **Smart Detection** — Identifies orphaned sessions by age and process status
- 💾 **Safe Archival** — Backs up transcripts before deletion
- 🛡️ **Multiple Safety Layers** — Dry-run mode, confirmation prompts, active process checks
- ⚙️ **Configurable** — YAML-based retention policies
- 📊 **Detailed Reporting** — JSON/text output with metrics
- 🔧 **Enterprise Ready** — Logging, audit trails, cron integration

## 🚀 Quick Start

```bash
# Preview what would be cleaned (dry-run)
python3 scripts/swarm_janitor.py --dry-run

# Archive old sessions, then clean
python3 scripts/swarm_janitor.py --archive --clean

# Custom retention (7 days)
python3 scripts/swarm_janitor.py --retention-days 7 --clean
```

## 📦 Installation

### As OpenClaw Skill

```bash
# Clone to your OpenClaw skills directory
cd ~/.openclaw/workspace/skills
git clone https://github.com/openclawdad/swarm-janitor.git

# Run first scan
python3 swarm-janitor/scripts/swarm_janitor.py --dry-run
```

### Standalone

```bash
# Clone repository
git clone https://github.com/openclawdad/swarm-janitor.git
cd swarm-janitor

# Install dependencies (none required, pure Python)
python3 scripts/swarm_janitor.py --help
```

## ⚙️ Configuration

Create `~/.swarm-janitor.yaml`:

```yaml
retention:
  days: 3                    # Delete sessions older than 3 days
  min_keep: 10              # Always keep 10 most recent
  
archive:
  enabled: true             # Archive before deletion
  destination: local        # Or: supermemory, s3
  
safety:
  dry_run_default: true     # Default to preview mode
  check_processes: true     # Never delete active sessions
```

## 🛡️ Safety First

| Safety Check | Description |
|--------------|-------------|
| **Dry-Run Default** | Preview mode is default — explicit `--clean` required |
| **Process Check** | Verifies no active process owns session |
| **Age Verification** | Only processes sessions older than threshold |
| **Archive First** | Backs up to SuperMemory/local before deletion |
| **Confirmation** | Prompts before large deletions |

## 📊 Usage Examples

### Daily Maintenance (Cron)

```cron
# Daily at 3 AM
0 3 * * * python3 ~/.openclaw/workspace/skills/swarm-janitor/scripts/swarm_janitor.py --clean --retention-days 3
```

### Manual Cleanup

```bash
# See what would be deleted
python3 scripts/swarm_janitor.py --dry-run --verbose

# Archive only (no deletion)
python3 scripts/swarm_janitor.py --archive

# Aggressive cleanup
python3 scripts/swarm_janitor.py --clean --retention-days 1 --force

# JSON output for monitoring
python3 scripts/swarm_janitor.py --report --output json
```

### With n8n

Create an n8n workflow node:
```json
{
  "parameters": {
    "command": "python3 ~/.openclaw/workspace/skills/swarm-janitor/scripts/swarm_janitor.py --clean --output json"
  }
}
```

## 🏗️ Architecture

```
swarm-janitor/
├── SKILL.md                    # OpenClaw skill documentation
├── scripts/
│   └── swarm_janitor.py       # Main Python implementation
├── references/
│   ├── config.yaml            # Configuration template
│   └── advanced.md            # Advanced usage guide
├── README.md                  # This file
└── LICENSE                    # MIT License
```

### Core Components

- **SessionAnalyzer** — Scans and classifies session files
- **SuperMemoryArchiver** — Archives transcripts before deletion
- **SwarmJanitor** — Main orchestrator with safety checks

## 🔍 How It Works

1. **Discovery** — Scans `~/.openclaw/agents/main/sessions/`
2. **Analysis** — Determines age, activity status, size
3. **Classification** — Identifies orphaned vs active
4. **Archival** — Saves to SuperMemory/local
5. **Cleanup** — Safely removes orphaned files
6. **Reporting** — Generates summary

## 📝 License

MIT License — Created by [OpenClawdad](https://github.com/openclawdad) for the OpenClaw community.

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 🔗 Links

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [ClawHub Skill Store](https://clawhub.com)
- [Issue Tracker](https://github.com/openclawdad/swarm-janitor/issues)

---

**Made with 🦞 by OpenClawdad for the agent community.**

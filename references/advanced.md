# Advanced Usage Guide

## Custom Retention Policies

### Development Environment
Short retention for active development:
```yaml
retention:
  days: 1
  min_keep: 5
```

### Production Environment
Conservative retention for safety:
```yaml
retention:
  days: 7
  min_keep: 20
  max_size_mb: 50
```

## Integration Examples

### With n8n
Create an n8n workflow that triggers Swarm Janitor:
```json
{
  "nodes": [
    {
      "parameters": {
        "command": "python3 ~/.openclaw/workspace/skills/swarm-janitor/scripts/swarm_janitor.py --clean --retention-days 3"
      },
      "name": "Swarm Janitor",
      "type": "n8n-nodes-base.executeCommand"
    }
  ]
}
```

### With cron
Daily automated cleanup:
```cron
0 3 * * * /usr/bin/python3 ~/.openclaw/workspace/skills/swarm-janitor/scripts/swarm_janitor.py --clean --retention-days 3 >> /var/log/swarm-janitor.log 2>&1
```

### With monitoring
JSON output for monitoring systems:
```bash
python3 swarm_janitor.py --clean --output json | jq '.space_reclaimed_bytes'
```

## Troubleshooting

### Sessions not detected
Check permissions:
```bash
ls -la ~/.openclaw/agents/main/sessions/
```

### Archive failures
Verify archive directory exists:
```bash
mkdir -p ~/.openclaw/archives/swarm-janitor
```

### Disk space still low
Check for other large directories:
```bash
du -sh ~/.openclaw/* | sort -hr | head -10
```

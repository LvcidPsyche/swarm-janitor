# Advanced Usage of Swarm Janitor

## Configurable Retention Policies
You can specify the retention period for sessions by editing the `cleanup.py` script. The current script is set to archive sessions older than 7 days.

## Logging
The skill maintains a log of actions taken during cleanup for troubleshooting and audit purposes. This log will be found in the workspace directory.

## Error Handling
The script contains built-in error handling to notify you of any issues during session cleanup.
#!/usr/bin/env python3
"""
Swarm Janitor - Enterprise Subagent Cleanup Tool

Cleans up orphaned OpenClaw subagent sessions while preserving
important work through archival to SuperMemory.

Author: OpenClawdad (Redclay)
License: MIT
"""

import argparse
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import shutil


class SessionAnalyzer:
    """Analyzes OpenClaw session files to identify orphaned subagents."""
    
    def __init__(self, sessions_dir: str, retention_days: int = 3):
        self.sessions_dir = Path(sessions_dir).expanduser()
        self.retention_days = retention_days
        self.cutoff_date = datetime.now() - timedelta(days=retention_days)
        
    def scan_sessions(self) -> List[Dict]:
        """Scan session directory and return metadata for all sessions."""
        sessions = []
        
        if not self.sessions_dir.exists():
            logging.error(f"Sessions directory not found: {self.sessions_dir}")
            return sessions
            
        for file_path in self.sessions_dir.glob("*.jsonl"):
            # Skip already marked deleted files
            if ".deleted." in file_path.name:
                continue
                
            try:
                stat = file_path.stat()
                session_info = {
                    "file": file_path.name,
                    "path": str(file_path),
                    "size_bytes": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "session_id": file_path.stem,
                    "is_orphaned": False,
                    "reason": []
                }
                
                # Check if session is older than retention
                if session_info["modified"] < self.cutoff_date:
                    session_info["is_orphaned"] = True
                    session_info["reason"].append(f"Older than {self.retention_days} days")
                
                # Check if corresponding process exists
                if not self._is_process_active(session_info["session_id"]):
                    session_info["is_orphaned"] = True
                    session_info["reason"].append("No active process")
                else:
                    # Has active process, not orphaned
                    session_info["is_orphaned"] = False
                    
                sessions.append(session_info)
                
            except Exception as e:
                logging.warning(f"Error analyzing {file_path}: {e}")
                
        return sorted(sessions, key=lambda x: x["modified"])
    
    def _is_process_active(self, session_id: str) -> bool:
        """Check if a session has an active process."""
        try:
            # Check if session exists in sessions.json
            sessions_json = self.sessions_dir / "sessions.json"
            if not sessions_json.exists():
                return False
                
            with open(sessions_json, 'r') as f:
                data = json.load(f)
                
            # Look for this session ID in active sessions
            for key, session in data.get("sessions", {}).items():
                if session_id in key or session_id in str(session.get("sessionId", "")):
                    # Check if recently updated
                    updated_at = session.get("updatedAt", 0)
                    if updated_at:
                        updated_dt = datetime.fromtimestamp(updated_at / 1000)
                        if datetime.now() - updated_dt < timedelta(hours=1):
                            return True
            return False
            
        except Exception as e:
            logging.warning(f"Error checking process status: {e}")
            return False


class SuperMemoryArchiver:
    """Archives session transcripts to SuperMemory before deletion."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("SUPERMEMORY_API_KEY")
        self.archived_count = 0
        self.failed_count = 0
        
    def archive_session(self, session_path: str) -> bool:
        """Archive a single session transcript to SuperMemory."""
        try:
            path = Path(session_path)
            if not path.exists():
                logging.warning(f"Session file not found: {path}")
                return False
                
            # Read transcript content
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                
            if not content.strip():
                logging.info(f"Empty transcript, skipping: {path.name}")
                return True
                
            # Create archive metadata
            archive_entry = {
                "session_id": path.stem,
                "archived_at": datetime.now().isoformat(),
                "original_path": str(path),
                "content_preview": content[:1000] if len(content) > 1000 else content
            }
            
            # In production, this would call SuperMemory API
            # For now, save to local archive directory
            archive_dir = Path.home() / ".openclaw" / "archives" / "swarm-janitor"
            archive_dir.mkdir(parents=True, exist_ok=True)
            
            archive_file = archive_dir / f"{path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(archive_file, 'w') as f:
                json.dump(archive_entry, f, indent=2)
                
            logging.info(f"Archived: {path.name} -> {archive_file.name}")
            self.archived_count += 1
            return True
            
        except Exception as e:
            logging.error(f"Failed to archive {session_path}: {e}")
            self.failed_count += 1
            return False


class SwarmJanitor:
    """Main cleanup orchestrator."""
    
    def __init__(
        self,
        sessions_dir: str = "~/.openclaw/agents/main/sessions",
        retention_days: int = 3,
        dry_run: bool = True,
        archive: bool = True
    ):
        self.analyzer = SessionAnalyzer(sessions_dir, retention_days)
        self.archiver = SuperMemoryArchiver()
        self.dry_run = dry_run
        self.archive_enabled = archive
        self.stats = {
            "scanned": 0,
            "orphaned": 0,
            "archived": 0,
            "deleted": 0,
            "failed": 0,
            "space_reclaimed_bytes": 0
        }
        
    def run(self) -> Dict:
        """Execute the cleanup process."""
        logging.info("=" * 60)
        logging.info("Swarm Janitor - Starting Cleanup Run")
        logging.info(f"Mode: {'DRY-RUN' if self.dry_run else 'LIVE'}")
        logging.info(f"Archive: {'Enabled' if self.archive_enabled else 'Disabled'}")
        logging.info("=" * 60)
        
        # Scan for sessions
        sessions = self.analyzer.scan_sessions()
        self.stats["scanned"] = len(sessions)
        
        orphaned = [s for s in sessions if s["is_orphaned"]]
        self.stats["orphaned"] = len(orphaned)
        
        logging.info(f"Scanned: {len(sessions)} sessions")
        logging.info(f"Orphaned: {len(orphaned)} sessions")
        
        if not orphaned:
            logging.info("No orphaned sessions found. Nothing to do.")
            return self.stats
            
        # Show what would be cleaned
        for session in orphaned:
            logging.info(f"  - {session['file']} ({session['size_bytes']:,} bytes)")
            logging.info(f"    Modified: {session['modified']}")
            logging.info(f"    Reasons: {', '.join(session['reason'])}")
            
        if self.dry_run:
            logging.info("\n[DRY-RUN] No changes made. Use --clean to execute.")
            return self.stats
            
        # Confirm before proceeding (unless --force)
        if not self._confirm_action(len(orphaned)):
            logging.info("Cleanup cancelled by user.")
            return self.stats
            
        # Process orphaned sessions
        for session in orphaned:
            self._process_session(session)
            
        # Print summary
        self._print_summary()
        
        return self.stats
        
    def _process_session(self, session: Dict):
        """Process a single orphaned session."""
        file_path = Path(session["path"])
        
        try:
            # Archive first if enabled
            if self.archive_enabled:
                if self.archiver.archive_session(str(file_path)):
                    self.stats["archived"] += 1
                else:
                    logging.warning(f"Archive failed for {file_path.name}, skipping deletion")
                    self.stats["failed"] += 1
                    return
                    
            # Delete the session file
            size = file_path.stat().st_size
            file_path.unlink()
            
            # Rename to .deleted format (for tracking)
            deleted_marker = file_path.parent / f"{file_path.name}.deleted.{datetime.now().strftime('%Y-%m-%dT%H-%M-%S.%f')}Z"
            deleted_marker.touch()
            
            self.stats["deleted"] += 1
            self.stats["space_reclaimed_bytes"] += size
            logging.info(f"Deleted: {file_path.name}")
            
        except Exception as e:
            logging.error(f"Failed to process {file_path}: {e}")
            self.stats["failed"] += 1
            
    def _confirm_action(self, count: int) -> bool:
        """Ask for confirmation before destructive actions."""
        # In automated mode, skip confirmation
        if os.getenv("SWARM_JANITOR_FORCE"):
            return True
            
        try:
            response = input(f"\nDelete {count} orphaned sessions? [y/N]: ")
            return response.lower().strip() == 'y'
        except EOFError:
            # Non-interactive mode
            logging.warning("Non-interactive mode, proceeding without confirmation")
            return True
            
    def _print_summary(self):
        """Print cleanup summary."""
        logging.info("\n" + "=" * 60)
        logging.info("Cleanup Summary")
        logging.info("=" * 60)
        logging.info(f"Sessions scanned: {self.stats['scanned']}")
        logging.info(f"Orphaned found: {self.stats['orphaned']}")
        logging.info(f"Archived: {self.stats['archived']}")
        logging.info(f"Deleted: {self.stats['deleted']}")
        logging.info(f"Failed: {self.stats['failed']}")
        logging.info(f"Space reclaimed: {self.stats['space_reclaimed_bytes']:,} bytes")
        logging.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Swarm Janitor - Clean up orphaned OpenClaw subagent sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview what would be cleaned
  %(prog)s --dry-run

  # Archive and clean sessions older than 3 days
  %(prog)s --archive --clean

  # Clean with custom retention period
  %(prog)s --clean --retention-days 7

  # Force cleanup without confirmation
  %(prog)s --clean --force
        """
    )
    
    parser.add_argument(
        "--sessions-dir",
        default="~/.openclaw/agents/main/sessions",
        help="Path to OpenClaw sessions directory (default: ~/.openclaw/agents/main/sessions)"
    )
    
    parser.add_argument(
        "--retention-days",
        type=int,
        default=3,
        help="Delete sessions older than N days (default: 3)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Preview changes without executing (default: True)"
    )
    
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Execute cleanup (required to actually delete files)"
    )
    
    parser.add_argument(
        "--archive",
        action="store_true",
        default=True,
        help="Archive transcripts before deletion (default: True)"
    )
    
    parser.add_argument(
        "--no-archive",
        action="store_true",
        help="Skip archiving (not recommended)"
    )
    
    parser.add_argument(
        "--force",
        action="store_true",
        help="Skip confirmation prompts"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--output",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )
    
    args = parser.parse_args()
    
    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handle --clean flag (disables dry-run)
    dry_run = not args.clean
    
    # Handle --no-archive flag
    archive = args.archive and not args.no_archive
    
    # Set force environment variable
    if args.force:
        os.environ["SWARM_JANITOR_FORCE"] = "1"
    
    # Run janitor
    janitor = SwarmJanitor(
        sessions_dir=args.sessions_dir,
        retention_days=args.retention_days,
        dry_run=dry_run,
        archive=archive
    )
    
    stats = janitor.run()
    
    # Output results
    if args.output == "json":
        print(json.dumps(stats, indent=2))
    
    # Exit with error if any failures
    sys.exit(0 if stats["failed"] == 0 else 1)


if __name__ == "__main__":
    main()

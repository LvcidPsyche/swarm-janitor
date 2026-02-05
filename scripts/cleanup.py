import os
import json
import datetime

def cleanup_sessions(session_directory, archive_directory):
    orphaned_sessions = []
    active_sessions = []

    for filename in os.listdir(session_directory):
        if filename.endswith('.jsonl'):
            filepath = os.path.join(session_directory, filename)
            creation_time = os.path.getctime(filepath)
            creation_date = datetime.datetime.fromtimestamp(creation_time)
            if (datetime.datetime.now() - creation_date).days > 7:  # Example criteria for older sessions
                orphaned_sessions.append(filepath)
            else:
                active_sessions.append(filepath)

    for session in orphaned_sessions:
        archive_session(session, archive_directory)
        os.remove(session)

def archive_session(session_path, archive_directory):
    session_name = os.path.basename(session_path)
    archive_path = os.path.join(archive_directory, f'archived_{session_name}')
    os.rename(session_path, archive_path)

if __name__ == '__main__':
    cleanup_sessions('/home/botuser/.openclaw/agents/main/sessions/', '/path_to_supermemory_archive/')
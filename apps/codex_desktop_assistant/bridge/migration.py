"""Consistent pre-migration backups; never delete history, files or credentials."""
import sqlite3
import time
from contextlib import closing
from pathlib import Path


def backup_state(directory):
    directory=Path(directory);backup=directory/'state-backups'/'before-computer-bridge'
    if (backup/'complete').exists():return backup
    backup.mkdir(parents=True,exist_ok=True)
    for relative in ('assistant.sqlite3','projects/queue.sqlite3'):
        source=directory/relative
        if not source.is_file():continue
        target=backup/(relative.replace('/','-'))
        with closing(sqlite3.connect(source.as_uri()+'?mode=ro',uri=True)) as src,closing(sqlite3.connect(target)) as dst:src.backup(dst)
    (backup/'complete').write_text(time.strftime('%Y-%m-%d %H:%M:%S'),encoding='utf-8')
    return backup


def migrate_projects(queue,owner):
    """One local Windows owner, new official controller; retain original history.

    Legacy chat isolation is retired with the duplicate chat UI. Publication scopes
    are revoked rather than inherited, and running legacy work is paused.
    """
    with queue.lock:
        legacy=queue.rows('SELECT id,conversation,state FROM projects WHERE conversation!=?',(owner,))
        if not legacy:return 0
        folder=queue.root.parent/'state-backups'/'before-bridge-project-migration';folder.mkdir(parents=True,exist_ok=True)
        target=folder/('projects-'+time.strftime('%Y%m%d-%H%M%S')+'.sqlite3')
        with closing(sqlite3.connect(target)) as backup:queue.db.backup(backup)
        for project in legacy:
            queue.db.execute("UPDATE projects SET conversation=?,state=CASE WHEN state='running' THEN 'paused' ELSE state END WHERE id=?",(owner,project['id']))
            queue.db.execute('UPDATE scopes SET revoked=1 WHERE project=?',(project['id'],))
            queue.event(project['id'],None,'official_controller_migration',{'previous_conversation':project['conversation'],'new_conversation':owner,'publication_scopes_revoked':True})
        queue.db.commit();return len(legacy)

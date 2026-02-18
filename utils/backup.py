import os
import subprocess
import datetime
import gzip
import shutil
from pathlib import Path
from database.connection import get_db_connection
import logging

logger = logging.getLogger(__name__)

class BackupManager:
    def __init__(self, db_config, backup_dir='backups'):
        """
        db_config: dict with keys host, port, user, password, database
        backup_dir: root directory for backups
        """
        self.db_config = db_config
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.today = datetime.datetime.now()
        self.year_dir = self.backup_dir / str(self.today.year)
        self.month_dir = self.year_dir / f"{self.today.month:02d}"
        self.month_dir.mkdir(parents=True, exist_ok=True)

    def create_backup(self, backup_type='manual', user_id=None, comment=''):
        """
        Create a database backup.
        Returns backup info dict or None on failure.
        """
        timestamp = self.today.strftime('%Y%m%d_%H%M%S')
        filename = f"backup_{timestamp}.sql"
        filepath = self.month_dir / filename

        dump_cmd = [
            'pg_dump',
            '-h', self.db_config['host'],
            '-p', str(self.db_config['port']),
            '-U', self.db_config['user'],
            '-d', self.db_config['database'],
            '--clean',
            '--if-exists',
            '-f', str(filepath)
        ]

        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']

        try:
            logger.info(f"Creating backup: {filename}")
            result = subprocess.run(dump_cmd, env=env, capture_output=True, text=True, timeout=300)
            if result.returncode != 0:
                raise Exception(f"pg_dump error: {result.stderr}")

            # Compress
            compressed_path = self._compress_file(filepath)
            filesize = compressed_path.stat().st_size

            # Save record in DB
            backup_id = self._save_backup_record(
                filename=compressed_path.name,
                filepath=str(compressed_path.relative_to(self.backup_dir.parent)),
                filesize=filesize,
                backup_type=backup_type,
                user_id=user_id,
                comment=comment
            )

            logger.info(f"Backup created: {compressed_path}, size: {filesize} bytes")
            return {
                'id': backup_id,
                'filename': compressed_path.name,
                'filepath': str(compressed_path),
                'filesize': filesize,
                'created_at': self.today
            }
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            self._save_backup_record(
                filename=filename,
                filepath=str(filepath),
                status='failed',
                comment=str(e)
            )
            return None

    def _compress_file(self, filepath):
        """Compress a file with gzip and remove original."""
        compressed_path = filepath.with_suffix('.sql.gz')
        with open(filepath, 'rb') as f_in:
            with gzip.open(compressed_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        filepath.unlink()
        return compressed_path

    def _save_backup_record(self, filename, filepath, filesize=None, backup_type='manual',
                            user_id=None, status='completed', comment=''):
        """Insert backup record into database."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO backups (filename, filepath, filesize, type, status, created_by, comment)
            VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
        """, (filename, filepath, filesize, backup_type, status, user_id, comment))
        backup_id = cur.fetchone()[0]
        conn.commit()
        cur.close()
        conn.close()
        return backup_id

    def restore_backup(self, backup_id, user_id=None):
        """Restore database from a backup."""
        # Get backup file path
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT filepath FROM backups WHERE id = %s", (backup_id,))
        row = cur.fetchone()
        cur.close()
        conn.close()
        if not row:
            raise Exception(f"Backup {backup_id} not found")

        backup_path = Path(row[0])
        if not backup_path.exists():
            backup_path = self.backup_dir.parent / row[0]
            if not backup_path.exists():
                raise Exception(f"Backup file not found: {backup_path}")

        # Decompress if needed
        if backup_path.suffix == '.gz':
            import gzip
            temp_path = backup_path.with_suffix('.sql.tmp')
            with gzip.open(backup_path, 'rb') as f_in:
                with open(temp_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            restore_file = temp_path
        else:
            restore_file = backup_path

        # Restore command
        restore_cmd = [
            'psql',
            '-h', self.db_config['host'],
            '-p', str(self.db_config['port']),
            '-U', self.db_config['user'],
            '-d', self.db_config['database'],
            '-f', str(restore_file)
        ]

        env = os.environ.copy()
        env['PGPASSWORD'] = self.db_config['password']

        try:
            logger.info(f"Restoring backup {backup_id}")
            result = subprocess.run(restore_cmd, env=env, capture_output=True, text=True, timeout=600)
            if result.returncode != 0:
                raise Exception(f"Restore error: {result.stderr}")

            # Update record
            conn = get_db_connection()
            cur = conn.cursor()
            cur.execute("UPDATE backups SET restored_at = NOW(), restored_by = %s WHERE id = %s",
                        (user_id, backup_id))
            conn.commit()
            cur.close()
            conn.close()
            logger.info(f"Backup {backup_id} restored successfully")
            return True
        except Exception as e:
            logger.error(f"Restore failed: {e}")
            raise
        finally:
            if backup_path.suffix == '.gz' and temp_path.exists():
                temp_path.unlink()

    def list_backups(self, limit=50):
        """List backups from database."""
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, filename, filesize, type, status, created_at, comment, restored_at, restored_by
            FROM backups ORDER BY created_at DESC LIMIT %s
        """, (limit,))
        rows = cur.fetchall()
        cur.close()
        conn.close()
        return [{
            'id': r[0],
            'filename': r[1],
            'filesize': self._format_size(r[2]),
            'type': r[3],
            'status': r[4],
            'created_at': r[5],
            'comment': r[6],
            'restored_at': r[7],
            'restored_by': r[8]
        } for r in rows]

    def _format_size(self, size):
        if size is None:
            return 'N/A'
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"

    def cleanup_old_backups(self, keep_days=30):
        """Delete backups older than keep_days and not restored."""
        cutoff = datetime.datetime.now() - datetime.timedelta(days=keep_days)
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, filepath FROM backups WHERE created_at < %s AND restored_at IS NULL", (cutoff,))
        old_backups = cur.fetchall()
        for backup_id, filepath in old_backups:
            try:
                path = Path(filepath)
                if path.exists():
                    path.unlink()
                cur.execute("DELETE FROM backups WHERE id = %s", (backup_id,))
                logger.info(f"Deleted old backup ID {backup_id}")
            except Exception as e:
                logger.error(f"Error deleting backup {backup_id}: {e}")
        conn.commit()
        cur.close()
        conn.close()
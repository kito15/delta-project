import os
from datetime import datetime
import json
from flask import current_app, g
from app import get_db

class Analysis:
    """Analysis results model"""
    
    def __init__(self, id=None, user_id=None, filename=None, file_size=None,
                 file_path=None, total_rows=None, total_columns=None, 
                 quality_score=None, results_json=None, created_at=None):
        self.id = id
        self.user_id = user_id
        self.filename = filename
        self.file_size = file_size
        self.file_path = file_path
        self.total_rows = total_rows
        self.total_columns = total_columns
        self.quality_score = quality_score
        self.results_json = results_json
        self.created_at = created_at

    def set_results(self, results_dict):
        """Store results dictionary as JSON"""
        self.results_json = json.dumps(results_dict)

    def get_results(self):
        """Retrieve results dictionary from JSON"""
        if self.results_json:
            return json.loads(self.results_json)
        return {}

    def save(self):
        """Save analysis to database (INSERT or UPDATE)"""
        db = get_db()
        cursor = db.cursor()
        
        try:
            if self.id is None:
                # INSERT new analysis
                cursor.execute("""
                    INSERT INTO analyses 
                    (user_id, filename, file_size, file_path, total_rows, 
                     total_columns, quality_score, results_json, created_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (self.user_id, self.filename, self.file_size, self.file_path,
                      self.total_rows, self.total_columns, self.quality_score,
                      self.results_json, datetime.utcnow()))
                self.id = cursor.lastrowid
            else:
                # UPDATE existing analysis
                cursor.execute("""
                    UPDATE analyses 
                    SET user_id = %s, filename = %s, file_size = %s, file_path = %s,
                        total_rows = %s, total_columns = %s, quality_score = %s,
                        results_json = %s
                    WHERE id = %s
                """, (self.user_id, self.filename, self.file_size, self.file_path,
                      self.total_rows, self.total_columns, self.quality_score,
                      self.results_json, self.id))
            
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    def delete(self):
        """Delete analysis from database"""
        if self.id is None:
            return False
        
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute("DELETE FROM analyses WHERE id = %s", (self.id,))
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise e
        finally:
            cursor.close()

    @classmethod
    def get_by_id(cls, analysis_id, user_id=None):
        """Get analysis by ID, optionally filtered by user_id"""
        db = get_db()
        cursor = db.cursor()
        
        try:
            if user_id is not None:
                cursor.execute("""
                    SELECT id, user_id, filename, file_size, file_path, 
                           total_rows, total_columns, quality_score, 
                           results_json, created_at
                    FROM analyses WHERE id = %s AND user_id = %s
                """, (analysis_id, user_id))
            else:
                cursor.execute("""
                    SELECT id, user_id, filename, file_size, file_path, 
                           total_rows, total_columns, quality_score, 
                           results_json, created_at
                    FROM analyses WHERE id = %s
                """, (analysis_id,))
            
            row = cursor.fetchone()
            
            if row:
                return cls(
                    id=row['id'],
                    user_id=row['user_id'],
                    filename=row['filename'],
                    file_size=row['file_size'],
                    file_path=row['file_path'],
                    total_rows=row['total_rows'],
                    total_columns=row['total_columns'],
                    quality_score=row['quality_score'],
                    results_json=row['results_json'],
                    created_at=row['created_at']
                )
            return None
        finally:
            cursor.close()

    @classmethod
    def get_by_user_id(cls, user_id, limit=20):
        """Get analyses by user_id, ordered by created_at DESC"""
        db = get_db()
        cursor = db.cursor()
        
        try:
            cursor.execute("""
                SELECT id, user_id, filename, file_size, file_path, 
                       total_rows, total_columns, quality_score, 
                       results_json, created_at
                FROM analyses 
                WHERE user_id = %s
                ORDER BY created_at DESC
                LIMIT %s
            """, (user_id, limit))
            
            rows = cursor.fetchall()
            analyses = []
            
            for row in rows:
                analyses.append(cls(
                    id=row['id'],
                    user_id=row['user_id'],
                    filename=row['filename'],
                    file_size=row['file_size'],
                    file_path=row['file_path'],
                    total_rows=row['total_rows'],
                    total_columns=row['total_columns'],
                    quality_score=row['quality_score'],
                    results_json=row['results_json'],
                    created_at=row['created_at']
                ))
            
            return analyses
        finally:
            cursor.close()

    @classmethod
    def delete_all_for_user(cls, user_id):
        """Delete all analyses and associated files for a user.

        Returns:
            int: Number of analyses deleted.
        """
        db = get_db()
        cursor = db.cursor()

        try:
            cursor.execute(
                "SELECT file_path FROM analyses WHERE user_id = %s",
                (user_id,)
            )
            rows = cursor.fetchall()

            file_paths = [row.get('file_path') for row in rows if row.get('file_path')]

            for path in file_paths:
                try:
                    if path and os.path.exists(path):
                        os.remove(path)
                except OSError as exc:
                    try:
                        current_app.logger.warning(
                            'Failed to remove analysis file %s: %s', path, exc
                        )
                    except Exception:
                        pass

            cursor.execute("DELETE FROM analyses WHERE user_id = %s", (user_id,))
            deleted_count = cursor.rowcount
            db.commit()
            return deleted_count
        except Exception as exc:
            db.rollback()
            raise exc
        finally:
            cursor.close()

    def to_dict(self, include_results=False):
        """Convert analysis to dictionary"""
        data = {
            'id': self.id,
            'filename': self.filename,
            'file_size': self.file_size,
            'total_rows': self.total_rows,
            'total_columns': self.total_columns,
            'quality_score': self.quality_score,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'timestamp': self.created_at.isoformat() if self.created_at else None
        }

        if include_results:
            data['results'] = self.get_results()

        return data

    def __repr__(self):
        return f'<Analysis {self.id}: {self.filename}>'

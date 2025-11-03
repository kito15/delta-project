from datetime import datetime
import json
from app import db

class Analysis(db.Model):
    """Analysis results model"""
    __tablename__ = 'analyses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)
    file_path = db.Column(db.String(500))

    # Analysis metrics
    total_rows = db.Column(db.Integer)
    total_columns = db.Column(db.Integer)
    quality_score = db.Column(db.Integer)

    # Full results stored as JSON
    results_json = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def set_results(self, results_dict):
        """Store results dictionary as JSON"""
        self.results_json = json.dumps(results_dict)

    def get_results(self):
        """Retrieve results dictionary from JSON"""
        if self.results_json:
            return json.loads(self.results_json)
        return {}

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


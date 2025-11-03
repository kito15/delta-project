import os
import uuid
from werkzeug.utils import secure_filename

class FileService:
    """Service for handling file operations"""

    @staticmethod
    def allowed_file(filename, allowed_extensions):
        """Check if file extension is allowed"""
        return '.' in filename and \
            filename.rsplit('.', 1)[1].lower() in allowed_extensions

    @staticmethod
    def validate_file(file, config):
        """Validate uploaded file"""
        # Check if file exists
        if not file:
            return {'valid': False, 'message': 'No file provided'}

        # Check filename
        if file.filename == '':
            return {'valid': False, 'message': 'No file selected'}

        # Check file extension
        if not FileService.allowed_file(file.filename, config['ALLOWED_EXTENSIONS']):
            return {'valid': False, 'message': 'Only CSV files are allowed'}

        # Check file size
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)  # Reset file pointer

        if file_size > config['MAX_FILE_SIZE']:
            return {'valid': False, 'message': f'File size exceeds {config["MAX_FILE_SIZE"] // (1024*1024)}MB limit'}

        if file_size == 0:
            return {'valid': False, 'message': 'File is empty'}

        return {'valid': True, 'message': 'File is valid'}

    @staticmethod
    def save_file(file, upload_folder, user_id):
        """Save uploaded file with unique name"""
        # Generate unique filename
        original_filename = secure_filename(file.filename)
        file_extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{user_id}_{uuid.uuid4().hex}.{file_extension}"

        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # Get file size
        file_size = os.path.getsize(file_path)

        return {
            'file_id': unique_filename,
            'filename': original_filename,
            'file_path': file_path,
            'file_size': file_size
        }

    @staticmethod
    def format_file_size(bytes_size):
        """Format file size in human-readable format"""
        if bytes_size == 0:
            return '0 B'

        sizes = ['B', 'KB', 'MB', 'GB']
        k = 1024
        i = 0

        while bytes_size >= k and i < len(sizes) - 1:
            bytes_size /= k
            i += 1

        return f"{round(bytes_size, 2)} {sizes[i]}"


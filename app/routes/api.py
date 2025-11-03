import os
from flask import Blueprint, request, jsonify, current_app, send_file
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from app.models.analysis import Analysis
from app.services.file_service import FileService
from app.services.analysis_service import AnalysisService
from app.services.gemini_service import GeminiService

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/upload', methods=['POST'])
@login_required
def upload_file():
    """Handle CSV file upload"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': 'No file provided'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'success': False, 'message': 'No file selected'}), 400

    validation_result = FileService.validate_file(file, current_app.config)

    if not validation_result['valid']:
        return jsonify({'success': False, 'message': validation_result['message']}), 400

    try:
        file_info = FileService.save_file(file, current_app.config['UPLOAD_FOLDER'], current_user.id)

        return jsonify({
            'success': True,
            'file_id': file_info['file_id'],
            'filename': file_info['filename'],
            'file_size': file_info['file_size'],
            'message': 'File uploaded successfully'
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

@bp.route('/analyze', methods=['POST'])
@login_required
def analyze_file():
    """Analyze uploaded CSV file"""
    data = request.get_json()

    if not data or 'file_id' not in data:
        return jsonify({'success': False, 'message': 'File ID required'}), 400

    file_id = data['file_id']

    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file_id)

    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': 'File not found'}), 404

    try:
        results = AnalysisService.analyze_csv(file_path)

        analysis = Analysis(
            user_id=current_user.id,
            filename=results['filename'],
            file_size=results.get('fileSizeBytes', os.path.getsize(file_path)),
            file_path=file_path,
            total_rows=results['totalRows'],
            total_columns=results['totalColumns'],
            quality_score=results['qualityScore']
        )
        analysis.set_results(results)
        analysis.save()

        response_data = results.copy()
        response_data['analysis_id'] = analysis.id

        return jsonify({
            'success': True,
            'data': response_data
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'message': f'Analysis failed: {str(e)}'}), 500

@bp.route('/history', methods=['GET'])
@login_required
def get_history():
    """Get analysis history for current user"""
    analyses = Analysis.get_by_user_id(current_user.id, limit=20)

    history = []
    for analysis in analyses:
        results = analysis.get_results()
        history.append({
            'id': analysis.id,
            'filename': analysis.filename,
            'qualityScore': analysis.quality_score,
            'timestamp': analysis.created_at.isoformat(),
            'totalRows': analysis.total_rows,
            'totalColumns': analysis.total_columns,
            'issuesCount': len(results.get('issues', []))
        })

    return jsonify({
        'success': True,
        'history': history
    }), 200

@bp.route('/results/<int:analysis_id>', methods=['GET'])
@login_required
def get_results(analysis_id):
    """Get specific analysis results"""
    analysis = Analysis.get_by_id(analysis_id, user_id=current_user.id)

    if not analysis:
        return jsonify({'success': False, 'message': 'Analysis not found'}), 404

    results = analysis.get_results()
    results['analysis_id'] = analysis.id

    return jsonify({
        'success': True,
        'data': results
    }), 200

@bp.route('/export/<int:analysis_id>', methods=['GET'])
@login_required
def export_results(analysis_id):
    """Export analysis results as JSON file"""
    analysis = Analysis.get_by_id(analysis_id, user_id=current_user.id)

    if not analysis:
        return jsonify({'success': False, 'message': 'Analysis not found'}), 404

    results = analysis.get_results()

    import json
    import tempfile

    temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
    json.dump(results, temp_file, indent=2)
    temp_file.close()

    return send_file(
        temp_file.name,
        as_attachment=True,
        download_name=f'quality-report-{analysis_id}.json',
        mimetype='application/json'
    )

@bp.route('/analysis/<int:analysis_id>/affected-rows', methods=['GET'])
@login_required
def get_affected_rows(analysis_id):
    """Get rows affected by a specific issue"""
    analysis = Analysis.get_by_id(analysis_id, user_id=current_user.id)

    if not analysis:
        return jsonify({'success': False, 'message': 'Analysis not found'}), 404

    issue_type = request.args.get('issue_type')
    column_name = request.args.get('column')
    limit = int(request.args.get('limit', 50))
    offset = int(request.args.get('offset', 0))

    if not issue_type:
        return jsonify({'success': False, 'message': 'issue_type parameter required'}), 400

    if not analysis.file_path or not os.path.exists(analysis.file_path):
        return jsonify({'success': False, 'message': 'Data file not found'}), 404

    try:
        result = AnalysisService.get_affected_rows(
            analysis.file_path,
            issue_type,
            column_name,
            limit,
            offset
        )

        if 'error' in result:
            return jsonify({
                'success': False,
                'message': f'Failed to retrieve affected rows: {result["error"]}'
            }), 500

        return jsonify({
            'success': True,
            'data': result
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error retrieving affected rows: {str(e)}'
        }), 500

@bp.route('/analysis/<int:analysis_id>/generate-issue-analysis', methods=['POST'])
@login_required
def generate_issue_analysis(analysis_id):
    """Generate AI-powered analysis for any detected issue using Gemini"""
    analysis = Analysis.get_by_id(analysis_id, user_id=current_user.id)

    if not analysis:
        return jsonify({'success': False, 'message': 'Analysis not found'}), 404

    request_data = request.get_json() or {}
    issue_type = request_data.get('issue_type')

    if not issue_type:
        return jsonify({'success': False, 'message': 'Issue type is required'}), 400

    analysis_results = analysis.get_results()
    if not analysis_results:
        return jsonify({'success': False, 'message': 'Analysis results unavailable'}), 400

    issues = analysis_results.get('issues', [])
    column_name = request_data.get('column')

    def normalize(value):
        return (value or '').strip().lower()

    matched_issue = None
    for issue in issues:
        if issue.get('type') != issue_type:
            continue

        issue_column = issue.get('column')
        if column_name is None and issue_column is None:
            matched_issue = issue
            break

        if normalize(issue_column) == normalize(column_name):
            matched_issue = issue
            break

    if not matched_issue:
        return jsonify({'success': False, 'message': 'Issue details not found'}), 404

    column_name = matched_issue.get('column')
    count = int(matched_issue.get('count', request_data.get('count') or 0))
    severity = matched_issue.get('severity') or request_data.get('severity')
    description = matched_issue.get('description') or request_data.get('description')

    total_rows = analysis_results.get('totalRows') or 0
    total_columns = analysis_results.get('totalColumns') or 0
    quality_score = analysis_results.get('qualityScore')
    file_size = analysis_results.get('fileSize')

    percentage = request_data.get('percentage')
    if percentage is None:
        percentage = float(round((count / total_rows) * 100, 2)) if total_rows else None

    column_details = None
    if column_name:
        columns = analysis_results.get('columns', [])
        column_details = next((col for col in columns if col.get('name') == column_name), None)

    issue_payload = {
        'type': issue_type,
        'column': column_name,
        'severity': severity,
        'count': count,
        'percentage': percentage,
        'description': description,
        'dataset': {
            'filename': analysis_results.get('filename') or analysis.filename,
            'total_rows': total_rows,
            'total_columns': total_columns,
            'quality_score': quality_score,
            'file_size': file_size
        }
    }

    if column_details:
        issue_payload['column_details'] = column_details

    try:
        if issue_type == 'Statistical Outlier':
            if not column_name:
                return jsonify({'success': False, 'message': 'Column name required for outlier analysis'}), 400

            if not analysis.file_path or not os.path.exists(analysis.file_path):
                return jsonify({'success': False, 'message': 'Data file not found'}), 404

            import pandas as pd

            df = pd.read_csv(analysis.file_path)
            series = pd.to_numeric(df[column_name], errors='coerce')

            mean = series.mean()
            std = series.std()

            if std == 0 or std is None or pd.isna(std):
                return jsonify({
                    'success': False,
                    'message': 'Cannot generate analysis for column with zero standard deviation'
                }), 400

            outlier_mask = ((series - mean).abs() > 3 * std) & series.notna()
            outlier_values = series[outlier_mask]

            if len(outlier_values) == 0:
                return jsonify({
                    'success': False,
                    'message': 'No outliers found in this column'
                }), 400

            issue_payload['outlier_stats'] = {
                'column_name': column_name,
                'mean': float(mean),
                'std_dev': float(std),
                'count': int(len(outlier_values)),
                'total_records': int(len(series)),
                'percentage': float((len(outlier_values) / len(series)) * 100),
                'sample_values': [float(v) for v in outlier_values.head(15).tolist()],
                'min_outlier': float(outlier_values.min()),
                'max_outlier': float(outlier_values.max())
            }

        analysis_text = GeminiService.generate_issue_analysis(issue_payload)

        return jsonify({
            'success': True,
            'analysis': analysis_text
        }), 200

    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Failed to generate analysis: {str(e)}'
        }), 500

@bp.route('/delete/<int:analysis_id>', methods=['DELETE'])
@login_required
def delete_analysis(analysis_id):
    """Delete analysis and associated file"""
    analysis = Analysis.get_by_id(analysis_id, user_id=current_user.id)

    if not analysis:
        return jsonify({'success': False, 'message': 'Analysis not found'}), 404

    if analysis.file_path and os.path.exists(analysis.file_path):
        try:
            os.remove(analysis.file_path)
        except:
            pass  # File already deleted or inaccessible

    analysis.delete()

    return jsonify({
        'success': True,
        'message': 'Analysis deleted successfully'
    }), 200

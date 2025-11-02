"""
Export API routes
"""
import logging
import os
from datetime import datetime
from flask import request, jsonify, send_file, current_app
from app.api import api_bp
from app.models import SearchJob, SearchResult
from app.services.excel_service import ExcelService

logger = logging.getLogger(__name__)


@api_bp.route('/export/excel/<int:job_id>', methods=['POST'])
def export_to_excel(job_id):
    """Export search results to Excel tracker"""
    try:
        # Get search job
        job = SearchJob.query.get_or_404(job_id)
        
        # Get all results for this job
        results = SearchResult.query.filter_by(search_job_id=job_id).all()
        
        if not results:
            return jsonify({
                'success': False,
                'error': 'No results found for this search job'
            }), 404
        
        # Prepare data for Excel export
        export_data = []
        for result in results:
            export_data.append({
                **result.to_dict(include_relations=True),
                'search_date': job.created_at.strftime('%Y-%m-%d'),
                'date_from': job.date_from.strftime('%Y-%m-%d') if job.date_from else '',
                'date_to': job.date_to.strftime('%Y-%m-%d') if job.date_to else '',
            })
        
        # Generate Excel file
        excel_service = ExcelService()
        
        # Determine week number
        data = request.get_json() or {}
        week_number = data.get('week_number', datetime.now().strftime('%W'))
        
        # Generate filename
        filename = f"Literature_Tracker_Week{week_number}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        output_path = os.path.join(current_app.config['EXPORTS_DIR'], filename)
        
        # Generate Excel
        excel_service.generate_tracker(
            search_results=export_data,
            output_path=output_path,
            week_number=week_number
        )
        
        logger.info(f"Excel export generated: {filename}")
        
        # Return file
        return send_file(
            output_path,
            as_attachment=True,
            download_name=filename,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        logger.error(f"Error exporting to Excel: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/export/jobs', methods=['GET'])
def list_exports():
    """List available export files"""
    try:
        exports_dir = current_app.config['EXPORTS_DIR']
        files = []
        
        if os.path.exists(exports_dir):
            for filename in os.listdir(exports_dir):
                if filename.endswith('.xlsx'):
                    filepath = os.path.join(exports_dir, filename)
                    stat = os.stat(filepath)
                    files.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    })
        
        # Sort by creation time, newest first
        files.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'success': True,
            'data': files,
            'count': len(files)
        })
        
    except Exception as e:
        logger.error(f"Error listing exports: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


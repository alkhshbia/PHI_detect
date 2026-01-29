from flask import Blueprint, request, jsonify
import logging
import os

logger = logging.getLogger("logs_routes")

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs/recent', methods=['GET'])
def get_recent_logs():
    """
    Get recent logs from memory buffer.

    Query parameters:
        level: Filter by log level (INFO, WARNING, ERROR, DEBUG)
        logger: Filter by logger name
        limit: Number of logs to return (default 100, max 1000)
        offset: Pagination offset (default 0)
    """
    try:
        from src.services.log_manager import get_memory_handler
        handler = get_memory_handler()

        if not handler:
            return jsonify({
                'success': False,
                'message': 'Log handler not initialized'
            }), 500

        # Get query parameters
        level = request.args.get('level', None)
        logger_name = request.args.get('logger', None)
        limit = min(int(request.args.get('limit', 100)), 1000)
        offset = int(request.args.get('offset', 0))

        # Get filtered logs
        logs = handler.get_logs(level=level, logger_name=logger_name)

        # Apply pagination
        total = len(logs)
        logs = logs[offset:offset+limit]

        return jsonify({
            'success': True,
            'logs': logs,
            'total': total,
            'offset': offset,
            'limit': limit
        })

    except Exception as e:
        logger.error(f"Error retrieving logs: {e}")
        return jsonify({
            'success': False,
            'message': f'Error retrieving logs: {str(e)}'
        }), 500

@logs_bp.route('/logs/loggers', methods=['GET'])
def get_logger_names():
    """Get list of active logger names."""
    try:
        from src.services.log_manager import get_memory_handler
        handler = get_memory_handler()

        if not handler:
            return jsonify({
                'success': False,
                'message': 'Log handler not initialized'
            }), 500

        logs = handler.get_logs()
        loggers = sorted(set(log['logger'] for log in logs))

        return jsonify({
            'success': True,
            'loggers': loggers
        })

    except Exception as e:
        logger.error(f"Error retrieving logger names: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@logs_bp.route('/logs/clear', methods=['POST'])
def clear_logs():
    """Clear in-memory logs (admin function)."""
    try:
        from src.services.log_manager import get_memory_handler
        handler = get_memory_handler()

        if not handler:
            return jsonify({
                'success': False,
                'message': 'Log handler not initialized'
            }), 500

        handler.clear_logs()

        return jsonify({
            'success': True,
            'message': 'Logs cleared successfully'
        })

    except Exception as e:
        logger.error(f"Error clearing logs: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

@logs_bp.route('/logs/file', methods=['GET'])
def get_log_file():
    """
    Read logs from file (for older logs not in memory).

    Query parameters:
        lines: Number of lines to read from end (default 500, max 5000)
    """
    try:
        lines_to_read = min(int(request.args.get('lines', 500)), 5000)

        log_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'logs', 'app.log'
        )

        if not os.path.exists(log_file):
            return jsonify({
                'success': False,
                'message': 'Log file not found'
            }), 404

        # Read last N lines efficiently
        with open(log_file, 'r') as f:
            lines = f.readlines()[-lines_to_read:]

        return jsonify({
            'success': True,
            'logs': lines,
            'total_lines': len(lines)
        })

    except Exception as e:
        logger.error(f"Error reading log file: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        }), 500

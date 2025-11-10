"""
SpiceWork Database API
RESTful API for managing spice inventory
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
from database import SpiceWorkDB

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Initialize database
db_path = os.getenv('DATABASE_PATH', 'spicework.db')
db = SpiceWorkDB(db_path)


@app.route('/', methods=['GET'])
def index():
    """API root endpoint with information"""
    return jsonify({
        'name': 'SpiceWork Database API',
        'version': '1.0.0',
        'description': 'API access to SpiceWork Database for managing spice inventory',
        'endpoints': {
            'GET /': 'API information',
            'GET /health': 'Health check',
            'GET /spices': 'Get all spices',
            'GET /spices/<id>': 'Get spice by ID',
            'POST /spices': 'Create a new spice',
            'PUT /spices/<id>': 'Update a spice',
            'DELETE /spices/<id>': 'Delete a spice',
            'GET /spices/search?q=<query>': 'Search spices'
        }
    }), 200


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'database': 'connected'
    }), 200


@app.route('/spices', methods=['GET'])
def get_spices():
    """Get all spices"""
    try:
        spices = db.get_all_spices()
        return jsonify({
            'success': True,
            'count': len(spices),
            'data': spices
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/spices/<int:spice_id>', methods=['GET'])
def get_spice(spice_id):
    """Get a specific spice by ID"""
    try:
        spice = db.get_spice_by_id(spice_id)
        if spice:
            return jsonify({
                'success': True,
                'data': spice
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Spice not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/spices', methods=['POST'])
def create_spice():
    """Create a new spice"""
    try:
        data = request.get_json()
        
        if not data or 'name' not in data:
            return jsonify({
                'success': False,
                'error': 'Name is required'
            }), 400
        
        spice_id = db.create_spice(
            name=data['name'],
            origin=data.get('origin'),
            heat_level=data.get('heat_level'),
            quantity=data.get('quantity'),
            unit=data.get('unit'),
            description=data.get('description')
        )
        
        spice = db.get_spice_by_id(spice_id)
        return jsonify({
            'success': True,
            'message': 'Spice created successfully',
            'data': spice
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/spices/<int:spice_id>', methods=['PUT'])
def update_spice(spice_id):
    """Update an existing spice"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'No data provided'
            }), 400
        
        success = db.update_spice(
            spice_id=spice_id,
            name=data.get('name'),
            origin=data.get('origin'),
            heat_level=data.get('heat_level'),
            quantity=data.get('quantity'),
            unit=data.get('unit'),
            description=data.get('description')
        )
        
        if success:
            spice = db.get_spice_by_id(spice_id)
            return jsonify({
                'success': True,
                'message': 'Spice updated successfully',
                'data': spice
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Spice not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/spices/<int:spice_id>', methods=['DELETE'])
def delete_spice(spice_id):
    """Delete a spice"""
    try:
        success = db.delete_spice(spice_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Spice deleted successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Spice not found'
            }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/spices/search', methods=['GET'])
def search_spices():
    """Search spices by name or description"""
    try:
        query = request.args.get('q', '')
        
        if not query:
            return jsonify({
                'success': False,
                'error': 'Query parameter "q" is required'
            }), 400
        
        spices = db.search_spices(query)
        return jsonify({
            'success': True,
            'count': len(spices),
            'data': spices
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


if __name__ == '__main__':
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"Starting SpiceWork Database API on {host}:{port}")
    app.run(host=host, port=port, debug=debug)

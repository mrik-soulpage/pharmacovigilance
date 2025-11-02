"""
Products API routes
"""
import logging
from flask import request, jsonify, current_app
from app.api import api_bp
from app.models import db, Product

logger = logging.getLogger(__name__)


@api_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products"""
    try:
        products = Product.query.all()
        return jsonify({
            'success': True,
            'data': [p.to_dict() for p in products],
            'count': len(products)
        })
    except Exception as e:
        logger.error(f"Error fetching products: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a single product by ID"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify({
            'success': True,
            'data': product.to_dict()
        })
    except Exception as e:
        logger.error(f"Error fetching product {product_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 404


@api_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if not data.get('inn') or not data.get('search_strategy'):
            return jsonify({
                'success': False,
                'error': 'INN and search_strategy are required'
            }), 400
        
        # Check if product already exists
        existing = Product.query.filter_by(inn=data['inn']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': f'Product with INN "{data["inn"]}" already exists'
            }), 409
        
        product = Product(
            inn=data['inn'],
            search_strategy=data['search_strategy'],
            is_eu_product=data.get('is_eu_product', False),
            territories=data.get('territories', []),
            dosage_forms=data.get('dosage_forms', []),
            routes_of_administration=data.get('routes_of_administration', []),
            marketing_status=data.get('marketing_status', 'Active')
        )
        
        db.session.add(product)
        db.session.commit()
        
        logger.info(f"Created product: {product.inn}")
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': 'Product created successfully'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating product: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Update fields
        if 'inn' in data:
            product.inn = data['inn']
        if 'search_strategy' in data:
            product.search_strategy = data['search_strategy']
        if 'is_eu_product' in data:
            product.is_eu_product = data['is_eu_product']
        if 'territories' in data:
            product.territories = data['territories']
        if 'dosage_forms' in data:
            product.dosage_forms = data['dosage_forms']
        if 'routes_of_administration' in data:
            product.routes_of_administration = data['routes_of_administration']
        if 'marketing_status' in data:
            product.marketing_status = data['marketing_status']
        
        db.session.commit()
        
        logger.info(f"Updated product: {product.inn}")
        
        return jsonify({
            'success': True,
            'data': product.to_dict(),
            'message': 'Product updated successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating product {product_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get_or_404(product_id)
        inn = product.inn
        
        db.session.delete(product)
        db.session.commit()
        
        logger.info(f"Deleted product: {inn}")
        
        return jsonify({
            'success': True,
            'message': f'Product "{inn}" deleted successfully'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting product {product_id}: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


@api_bp.route('/products/import', methods=['POST'])
def import_products():
    """Import products from JSON array"""
    try:
        data = request.get_json()
        
        if not isinstance(data, list):
            return jsonify({
                'success': False,
                'error': 'Expected a JSON array of products'
            }), 400
        
        imported = 0
        skipped = 0
        errors = []
        
        for item in data:
            try:
                # Check if product already exists
                existing = Product.query.filter_by(inn=item.get('inn')).first()
                if existing:
                    skipped += 1
                    continue
                
                product = Product(
                    inn=item['inn'],
                    search_strategy=item['search_strategy'],
                    is_eu_product=item.get('is_eu_product', False),
                    territories=item.get('territories', []),
                    dosage_forms=item.get('dosage_forms', []),
                    routes_of_administration=item.get('routes', []),
                    marketing_status=item.get('marketing_status', 'Active')
                )
                
                db.session.add(product)
                imported += 1
                
            except Exception as e:
                errors.append(f"Error importing {item.get('inn', 'unknown')}: {str(e)}")
        
        db.session.commit()
        
        logger.info(f"Imported {imported} products, skipped {skipped}")
        
        return jsonify({
            'success': True,
            'imported': imported,
            'skipped': skipped,
            'errors': errors,
            'message': f'Successfully imported {imported} products'
        })
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error importing products: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


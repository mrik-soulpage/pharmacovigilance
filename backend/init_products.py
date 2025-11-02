"""
Initialize database with products from JSON file
"""
import json
import logging
from pathlib import Path
from app import create_app
from app.models import db, Product

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_products_from_json(json_file_path):
    """Load products from JSON file"""
    try:
        with open(json_file_path, 'r', encoding='utf-8') as f:
            products_data = json.load(f)
        return products_data
    except FileNotFoundError:
        logger.error(f"Products file not found: {json_file_path}")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing JSON file: {e}")
        return []


def import_products(products_data):
    """Import products into database"""
    app = create_app()
    
    with app.app_context():
        imported = 0
        skipped = 0
        errors = []
        
        for product_data in products_data:
            try:
                inn = product_data.get('inn')
                
                # Check if product already exists
                existing = Product.query.filter_by(inn=inn).first()
                if existing:
                    logger.info(f"Product '{inn}' already exists, skipping...")
                    skipped += 1
                    continue
                
                # Create new product
                # Map 'routes' to 'routes_of_administration'
                routes = product_data.get('routes', [])
                
                product = Product(
                    inn=inn,
                    search_strategy=product_data.get('search_strategy', ''),
                    is_eu_product=product_data.get('is_eu_product', False),
                    territories=product_data.get('territories', []),
                    dosage_forms=product_data.get('dosage_forms', []),
                    routes_of_administration=routes,
                    marketing_status=product_data.get('marketing_status', 'Active')
                )
                
                db.session.add(product)
                imported += 1
                logger.info(f"Added product: {inn}")
                
            except Exception as e:
                errors.append(f"Error importing {product_data.get('inn', 'unknown')}: {str(e)}")
                logger.error(f"Error importing product: {e}")
        
        try:
            db.session.commit()
            logger.info(f"✅ Successfully imported {imported} products, skipped {skipped}")
            
            if errors:
                logger.warning(f"Errors encountered: {len(errors)}")
                for error in errors:
                    logger.warning(f"  - {error}")
                    
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error committing to database: {e}")
            raise


def main():
    """Main function"""
    logger.info("=" * 80)
    logger.info("Starting product import process...")
    logger.info("=" * 80)
    
    # Path to products JSON file
    json_file = Path(__file__).parent.parent / 'synthetic_data' / 'products.json'
    
    if not json_file.exists():
        logger.error(f"Products file not found at: {json_file}")
        logger.info("Please ensure synthetic_data/products.json exists")
        return
    
    logger.info(f"Loading products from: {json_file}")
    products_data = load_products_from_json(json_file)
    
    if not products_data:
        logger.error("No products loaded from JSON file")
        return
    
    logger.info(f"Found {len(products_data)} products in JSON file")
    
    # Import products
    import_products(products_data)
    
    logger.info("=" * 80)
    logger.info("Product import completed!")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()


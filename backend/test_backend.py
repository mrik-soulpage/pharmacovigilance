"""
Backend validation test script
"""
import sys
import os

# Add backend to path
sys.path.insert(0, '/home/ubuntu/pharma_pv_poc/backend')

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    try:
        from app import create_app
        from app.models import db, Product, SearchJob, Article, SearchResult
        from app.services.pubmed_service import PubMedService
        from app.services.ai_service import AIService
        from app.services.excel_service import ExcelService
        print("✓ All imports successful")
        return True
    except Exception as e:
        print(f"✗ Import error: {e}")
        return False

def test_app_creation():
    """Test Flask app creation"""
    print("\nTesting Flask app creation...")
    try:
        from app import create_app
        app = create_app('testing')
        print(f"✓ Flask app created successfully")
        print(f"  - Config: {app.config['TESTING']}")
        return True
    except Exception as e:
        print(f"✗ App creation error: {e}")
        return False

def test_database():
    """Test database models"""
    print("\nTesting database models...")
    try:
        from app import create_app
        from app.models import db, Product
        
        app = create_app('testing')
        with app.app_context():
            db.create_all()
            
            # Test product creation
            product = Product(
                inn="Test Product",
                search_strategy="test AND strategy",
                is_eu_product=False,
                territories=["US", "UK"],
                dosage_forms=["Tablet"],
                routes_of_administration=["Oral"],
                marketing_status="Active"
            )
            db.session.add(product)
            db.session.commit()
            
            # Query product
            retrieved = Product.query.filter_by(inn="Test Product").first()
            assert retrieved is not None
            assert retrieved.inn == "Test Product"
            
            print("✓ Database models working correctly")
            return True
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_services():
    """Test service initialization"""
    print("\nTesting services...")
    try:
        from app.services.pubmed_service import PubMedService
        from app.services.ai_service import AIService
        from app.services.excel_service import ExcelService
        
        # Test PubMed service
        pubmed = PubMedService(email="test@example.com")
        print("✓ PubMed service initialized")
        
        # Test AI service (without API key)
        ai = AIService(api_key=None)
        print("✓ AI service initialized")
        
        # Test Excel service
        excel = ExcelService()
        print("✓ Excel service initialized")
        
        return True
    except Exception as e:
        print(f"✗ Service error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("Backend Validation Tests")
    print("=" * 60)
    
    results = []
    results.append(("Imports", test_imports()))
    results.append(("App Creation", test_app_creation()))
    results.append(("Database", test_database()))
    results.append(("Services", test_services()))
    
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    for name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{name}: {status}")
    
    all_passed = all(result for _, result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())

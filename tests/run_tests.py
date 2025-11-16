import pytest
import sys
import os

if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    exit_code = pytest.main([
        "-v",
        "--tb=short", 
        "--cov=main",           
        "--cov=test_manager",   
        "--cov-report=term-missing",
        "--cov-report=html",
        "tests/"
    ])
    
    print(f"\nТесты завершены с кодом: {exit_code}")
    sys.exit(exit_code)
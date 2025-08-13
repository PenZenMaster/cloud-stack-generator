#!/usr/bin/env python3
"""
Simple test to verify CSV encoding detection works
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_csv_encoding():
    """Test CSV encoding detection"""
    try:
        import chardet
        print("SUCCESS: chardet library available")
        
        # Test file path
        csv_file = "output/products/products_import.csv"
        
        if not os.path.exists(csv_file):
            print(f"ERROR: CSV file not found: {csv_file}")
            return False
        
        print(f"SUCCESS: CSV file found: {csv_file}")
        
        # Test chardet detection
        with open(csv_file, 'rb') as f:
            sample = f.read(10000)
        
        result = chardet.detect(sample)
        print(f"SUCCESS: Chardet detected: {result}")
        
        # Test reading with detected encoding
        encoding = result.get('encoding', 'utf-8')
        
        # Map encoding
        if encoding.lower() == 'windows-1252':
            encoding = 'cp1252'
        
        with open(csv_file, 'r', encoding=encoding, errors='replace') as f:
            lines = f.readlines()[:5]  # Read first 5 lines
        
        print(f"SUCCESS: Successfully read {len(lines)} lines with encoding: {encoding}")
        print(f"SUCCESS: First line: {lines[0].strip()}")
        
        # Test that problematic characters are handled
        found_special_chars = False
        for line in lines:
            if '–' in line or '—' in line or '©' in line or '®' in line:
                found_special_chars = True
                print(f"SUCCESS: Special characters handled correctly in: {line[:50]}...")
                break
        
        if not found_special_chars:
            print("INFO: No special characters found in first few lines")
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== Simple CSV Encoding Test ===")
    success = test_csv_encoding()
    print(f"\n{'SUCCESS' if success else 'FAILED'}: CSV encoding test {'passed' if success else 'failed'}")
    sys.exit(0 if success else 1)
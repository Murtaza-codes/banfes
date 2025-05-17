#!/usr/bin/env python
import os
import sys
import polib

def compile_po_files(locale_dir='locale'):
    """
    Compile all .po files in locale directory to .mo files
    """
    print(f"Searching for PO files in {locale_dir}...")
    print(f"Current working directory: {os.getcwd()}")
    
    count = 0
    po_files_found = []
    
    # First, find all .po files
    for root, dirs, files in os.walk(locale_dir):
        for file in files:
            if file.endswith('.po'):
                po_path = os.path.join(root, file)
                po_files_found.append(po_path)
    
    if not po_files_found:
        print(f"No .po files found in {locale_dir}")
        print("Directory structure:")
        for root, dirs, files in os.walk(locale_dir):
            print(f"  {root}")
            for file in files:
                print(f"    - {file}")
        return
    
    print(f"Found {len(po_files_found)} .po files:")
    for po_path in po_files_found:
        print(f"  {po_path}")
        
    # Now compile each .po file
    for po_path in po_files_found:
        mo_path = po_path.replace('.po', '.mo')
        
        try:
            print(f"Compiling: {po_path} -> {mo_path}")
            po = polib.pofile(po_path)
            po.save_as_mofile(mo_path)
            count += 1
            print(f"✅ Successfully compiled {po_path}")
            print(f"   - Contains {len(po)} translated strings")
        except Exception as e:
            print(f"❌ Error compiling {po_path}: {e}")
    
    print(f"Compilation completed. {count} files compiled.")

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)  # Change to script directory
    
    locale_dir = 'locale'
    if len(sys.argv) > 1:
        locale_dir = sys.argv[1]
        
    compile_po_files(locale_dir) 
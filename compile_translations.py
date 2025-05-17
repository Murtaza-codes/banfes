#!/usr/bin/env python
import os
import polib

def compile_po_files():
    """Compile .po files to .mo files using polib"""
    locale_dir = 'locale'
    
    # Walk through locale directory
    for root, dirs, files in os.walk(locale_dir):
        for file in files:
            if file.endswith('.po'):
                po_path = os.path.join(root, file)
                mo_path = po_path.replace('.po', '.mo')
                print(f"Compiling {po_path} to {mo_path}...")
                
                try:
                    po = polib.pofile(po_path)
                    po.save_as_mofile(mo_path)
                    print(f"✅ Successfully compiled {mo_path}")
                except Exception as e:
                    print(f"❌ Error compiling {po_path}: {e}")
    
    print("\nCompilation complete!")

if __name__ == "__main__":
    compile_po_files() 
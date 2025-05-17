#!/usr/bin/env python
import os
import sys
import gettext
import pprint

def verify_mo_file(mo_file_path):
    """Verify a .mo file by loading it with gettext"""
    print(f"Attempting to open MO file: {mo_file_path}")
    
    try:
        mo_dir = os.path.dirname(mo_file_path)
        domain = os.path.basename(mo_file_path).replace('.mo', '')
        lang = os.path.basename(os.path.dirname(os.path.dirname(mo_file_path)))
        
        print(f"Language: {lang}, Domain: {domain}, Directory: {mo_dir}")
        
        # Try to open the .mo file using gettext
        translation = gettext.translation(domain, os.path.dirname(os.path.dirname(os.path.dirname(mo_file_path))), 
                                         languages=[lang])
        translation.install()
        
        # Get some sample translations
        _ = translation.gettext
        catalog = translation._catalog
        
        # Print a sample of translations (first 5)
        print(f"Successfully loaded {len(catalog)} translations")
        print("Sample translations:")
        sample = list(catalog.items())[:5]
        for msgid, msgstr in sample:
            print(f"  '{msgid}' => '{msgstr}'")
            
        return True
    except Exception as e:
        print(f"Error verifying .mo file: {e}")
        return False

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    mo_file_path = os.path.join(script_dir, 'locale', 'fa', 'LC_MESSAGES', 'django.mo')
    
    if os.path.exists(mo_file_path):
        print(f"Found MO file: {mo_file_path}")
        success = verify_mo_file(mo_file_path)
        if success:
            print("MO file verification successful!")
        else:
            print("MO file verification failed.")
    else:
        print(f"MO file not found: {mo_file_path}")

if __name__ == "__main__":
    main() 
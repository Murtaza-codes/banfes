#!/usr/bin/env python
import os
import sys
import gettext

def test_translations(lang='fa'):
    """Test translation functionality for a specific language"""
    # Set up translation for a specific language
    print(f"Testing translations for language: {lang}")
    locale_dir = os.path.join(os.path.dirname(__file__), 'locale')
    print(f"Locale directory: {locale_dir}")
    lang_dir = os.path.join(locale_dir, lang, 'LC_MESSAGES')
    print(f"Language directory: {lang_dir}")
    mo_file = os.path.join(lang_dir, 'django.mo')
    print(f"MO file exists: {os.path.exists(mo_file)}")
    
    try:
        t = gettext.translation('django', locale_dir, languages=[lang])
        _ = t.gettext
        print(f"Translation object created successfully.")
        
        # Student dashboard entries we want to test
        dashboard_entries = [
            'Student Dashboard',
            'My Profile',
            'My Courses',
            'Assignments',
            'Quizzes & Tests',
            'Results & Grades',
            'Learning Materials',
            'Course Registration',
            'Calendar & Schedule',
            'Attendance',
            'View Profile',
            'View Courses',
            'View Assignments',
            'Take Quizzes',
            'View Results',
            'View Materials',
            'Register',
            'View Schedule',
            'View Attendance',
        ]
        
        # Test translations
        print(f"\nTranslations for {lang}:")
        print("-" * 40)
        max_len = max(len(entry) for entry in dashboard_entries)
        
        for entry in dashboard_entries:
            translation = _(entry)
            translated = translation != entry
            status = "✅" if translated else "❌"
            print(f"{status} {entry:{max_len}} => {translation}")
            
        return True
    except Exception as e:
        print(f"Error testing translations: {e}")
        return False

if __name__ == "__main__":
    # Get language from command line argument or default to Persian
    lang = 'fa'
    if len(sys.argv) > 1:
        lang = sys.argv[1]
        
    test_translations(lang) 
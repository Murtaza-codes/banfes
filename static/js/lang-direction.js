// Language direction handler
document.addEventListener('DOMContentLoaded', function() {
    // Get current language from HTML tag
    const htmlElement = document.documentElement;
    const currentLang = htmlElement.getAttribute('lang');
    
    // Array of RTL languages
    const rtlLanguages = ['fa', 'ar', 'he', 'ur'];
    
    // Set direction based on language
    if (rtlLanguages.includes(currentLang)) {
        htmlElement.setAttribute('dir', 'rtl');
        // Add RTL specific stylesheet if needed
        document.body.classList.add('rtl-active');
    } else {
        htmlElement.setAttribute('dir', 'ltr');
        document.body.classList.remove('rtl-active');
    }
    
    // Monitor language changes
    const languageForms = document.querySelectorAll('form[action*="set_language"]');
    languageForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const langInput = this.querySelector('input[name="language"]');
            if (langInput) {
                // Store that we're switching languages
                const newDirection = rtlLanguages.includes(langInput.value) ? 'rtl' : 'ltr';
                sessionStorage.setItem('direction_change', newDirection);
                // Let the form submit and reload the page
            }
        });
    });
    
    // Check if we just switched directions
    const directionChange = sessionStorage.getItem('direction_change');
    if (directionChange) {
        // Clear the flag
        sessionStorage.removeItem('direction_change');
        // Force reload if direction doesn't match what we expect
        const currentDir = htmlElement.getAttribute('dir');
        if ((directionChange === 'rtl' && currentDir !== 'rtl') || 
            (directionChange === 'ltr' && currentDir !== 'ltr')) {
            window.location.reload(true); // Force reload from server
        }
    }
}); 
/* PixelGroomer Web - Application JavaScript
 * Minimal JS for functionality that can't be done with HTMX
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize keyboard navigation for image viewer
  initImageNavigation();
  
  // Initialize theme persistence
  initTheme();
});

/**
 * Image viewer keyboard navigation
 */
function initImageNavigation() {
  document.addEventListener('keydown', function(e) {
    // Only handle if we're on the album page
    const imageViewer = document.querySelector('.image-viewer');
    if (!imageViewer) return;
    
    // Don't handle if user is typing in an input
    if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
    
    const prevBtn = document.querySelector('[data-nav="prev"]');
    const nextBtn = document.querySelector('[data-nav="next"]');
    
    switch (e.key) {
      case 'ArrowLeft':
        if (prevBtn) prevBtn.click();
        e.preventDefault();
        break;
      case 'ArrowRight':
        if (nextBtn) nextBtn.click();
        e.preventDefault();
        break;
      case '1':
      case '2':
      case '3':
      case '4':
      case '5':
        // Quick rating with number keys
        const ratingBtn = document.querySelector(`.rating-star[data-rating="${e.key}"]`);
        if (ratingBtn) ratingBtn.click();
        break;
      case '0':
        // Clear rating
        const clearRatingBtn = document.querySelector('.rating-star[data-rating="0"]');
        if (clearRatingBtn) clearRatingBtn.click();
        break;
    }
  });
}

/**
 * Theme initialization and persistence
 */
function initTheme() {
  // Get saved theme from localStorage
  const savedTheme = localStorage.getItem('pixelgroomer-theme');
  
  if (savedTheme) {
    setTheme(savedTheme);
  }
  
  // Listen for theme changes
  const themeSelect = document.querySelector('#theme-select');
  if (themeSelect) {
    themeSelect.addEventListener('change', function() {
      const theme = this.value;
      setTheme(theme);
      localStorage.setItem('pixelgroomer-theme', theme);
    });
  }
}

/**
 * Set the current theme
 */
function setTheme(theme) {
  const themeLink = document.getElementById('theme-css');
  if (themeLink) {
    themeLink.href = `/static/css/themes/${theme}.css`;
  }
  
  // Update the select if it exists
  const themeSelect = document.querySelector('#theme-select');
  if (themeSelect) {
    themeSelect.value = theme;
  }
}

/**
 * HTMX event handlers
 */

// After HTMX swaps content, reinitialize any necessary JS
document.body.addEventListener('htmx:afterSwap', function(e) {
  // Reinitialize components if needed
});

// Show loading indicator
document.body.addEventListener('htmx:beforeRequest', function(e) {
  const indicator = e.target.querySelector('.htmx-indicator');
  if (indicator) {
    indicator.style.opacity = '1';
  }
});

// Hide loading indicator
document.body.addEventListener('htmx:afterRequest', function(e) {
  const indicator = e.target.querySelector('.htmx-indicator');
  if (indicator) {
    indicator.style.opacity = '0';
  }
});

/* PixelGroomer Web - Application JavaScript
 * Minimal JS for functionality that can't be done with HTMX
 */

document.addEventListener('DOMContentLoaded', function() {
  // Initialize keyboard navigation for image viewer
  initImageNavigation();
  
  // Initialize theme persistence
  initTheme();
  
  // Initialize form persistence for tab switching
  initFormPersistence();
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
    setTheme(savedTheme, false); // Don't save again, just apply
  }
  
  // Listen for theme changes
  const themeSelect = document.querySelector('#theme-select');
  if (themeSelect) {
    themeSelect.addEventListener('change', function() {
      const theme = this.value;
      setTheme(theme, true);
    });
  }
}

/**
 * Set the current theme
 * Loads new CSS first, then removes old one to prevent flash of white
 */
function setTheme(theme, save) {
  const oldLink = document.getElementById('theme-css');
  if (!oldLink) return;
  
  const newHref = `/static/css/themes/${theme}.css`;
  
  // If same theme, do nothing
  if (oldLink.href.endsWith(newHref)) return;
  
  // Create new link element
  const newLink = document.createElement('link');
  newLink.rel = 'stylesheet';
  newLink.id = 'theme-css-new';
  newLink.href = newHref;
  
  // Wait for new CSS to load before removing old one
  newLink.onload = function() {
    // Swap IDs
    oldLink.remove();
    newLink.id = 'theme-css';
    
    // Save to localStorage and server
    if (save) {
      localStorage.setItem('pixelgroomer-theme', theme);
      
      // Also save to server session
      fetch('/api/theme', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: 'theme=' + encodeURIComponent(theme)
      });
    }
  };
  
  // Insert new link after old one
  oldLink.parentNode.insertBefore(newLink, oldLink.nextSibling);
  
  // Update the select if it exists
  const themeSelect = document.querySelector('#theme-select');
  if (themeSelect) {
    themeSelect.value = theme;
  }
}

/**
 * Form persistence for tab switching
 * Saves form data to sessionStorage before HTMX swaps content
 */
function initFormPersistence() {
  // Storage key prefix
  const STORAGE_PREFIX = 'pg-form-';
  
  /**
   * Get all form data from a container
   */
  function getFormData(container) {
    const data = {};
    const inputs = container.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
      if (!input.name || input.type === 'hidden') return;
      
      if (input.type === 'checkbox') {
        data[input.name] = input.checked;
      } else if (input.type === 'radio') {
        if (input.checked) {
          data[input.name] = input.value;
        }
      } else {
        data[input.name] = input.value;
      }
    });
    
    return data;
  }
  
  /**
   * Restore form data to a container
   */
  function restoreFormData(container, data) {
    if (!data || Object.keys(data).length === 0) return;
    
    Object.entries(data).forEach(([name, value]) => {
      const input = container.querySelector(`[name="${name}"]`);
      if (!input) return;
      
      if (input.type === 'checkbox') {
        input.checked = value === true || value === 'true';
      } else if (input.type === 'radio') {
        if (input.value === value) {
          input.checked = true;
        }
      } else {
        input.value = value;
      }
    });
  }
  
  /**
   * Get current module ID from active tab or form
   */
  function getCurrentModuleId() {
    const activeTab = document.querySelector('.tabs .tab.active');
    if (activeTab) {
      return activeTab.dataset.moduleId;
    }
    const hiddenInput = document.querySelector('#module-form-container input[name="module_id"]');
    if (hiddenInput) {
      return hiddenInput.value;
    }
    return null;
  }
  
  /**
   * Save current form data before tab switch
   */
  function saveCurrentForm() {
    const container = document.querySelector('#module-form-container');
    if (!container) return;
    
    const moduleId = getCurrentModuleId();
    if (!moduleId) return;
    
    const data = getFormData(container);
    if (Object.keys(data).length > 0) {
      sessionStorage.setItem(STORAGE_PREFIX + moduleId, JSON.stringify(data));
    }
  }
  
  // Save form data before HTMX request (tab switch)
  document.body.addEventListener('htmx:beforeRequest', function(e) {
    // Only save for tab switches targeting the module form container
    if (e.detail.target && e.detail.target.id === 'module-form-container') {
      saveCurrentForm();
    }
  });
  
  // Restore form data after HTMX swap
  document.body.addEventListener('htmx:afterSwap', function(e) {
    // Only restore for module form container swaps
    if (e.detail.target && e.detail.target.id === 'module-form-container') {
      const container = e.detail.target;
      const moduleId = getCurrentModuleId();
      
      if (moduleId) {
        const savedData = sessionStorage.getItem(STORAGE_PREFIX + moduleId);
        if (savedData) {
          try {
            restoreFormData(container, JSON.parse(savedData));
          } catch (err) {
            console.warn('Failed to restore form data:', err);
          }
        }
      }
    }
  });
  
  // Also save form data periodically while user is editing
  document.body.addEventListener('input', function(e) {
    const container = document.querySelector('#module-form-container');
    if (container && container.contains(e.target)) {
      // Debounce save
      clearTimeout(window._formSaveTimeout);
      window._formSaveTimeout = setTimeout(saveCurrentForm, 500);
    }
  });
}

/**
 * HTMX event handlers
 */

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

/**
 * Album popup functions
 */

function toggleAlbumPopup(button) {
  const container = button.closest('.album-multi-select');
  const popup = container.querySelector('.album-popup');
  
  if (popup.classList.contains('hidden')) {
    // Close any other open popups
    document.querySelectorAll('.album-popup').forEach(p => p.classList.add('hidden'));
    popup.classList.remove('hidden');
    
    // Close on click outside
    setTimeout(() => {
      document.addEventListener('click', closeAlbumPopupOnClickOutside);
    }, 0);
  } else {
    popup.classList.add('hidden');
  }
}

function closeAlbumPopupOnClickOutside(e) {
  const popup = document.querySelector('.album-popup:not(.hidden)');
  if (popup && !popup.contains(e.target) && !e.target.closest('.album-multi-select')) {
    popup.classList.add('hidden');
    document.removeEventListener('click', closeAlbumPopupOnClickOutside);
  }
}

// Close popup after HTMX swap
document.body.addEventListener('htmx:afterSwap', function(e) {
  if (e.detail.target && e.detail.target.id === 'album-checkboxes') {
    document.querySelectorAll('.album-popup').forEach(p => p.classList.add('hidden'));
  }
});

/**
 * Path picker functions
 */

/**
 * Select a path and put it in the target input
 */
function selectPath(targetInputId, path) {
  const input = document.getElementById(targetInputId);
  if (input) {
    input.value = path;
    // Trigger input event for form persistence
    input.dispatchEvent(new Event('input', { bubbles: true }));
  }
  // Close modal
  const modal = document.getElementById('path-picker-modal');
  if (modal) {
    modal.close();
  }
}

/**
 * Open path picker for a specific input
 */
function openPathPicker(targetInputId, mode) {
  mode = mode || 'directory';
  const modal = document.getElementById('path-picker-modal');
  const content = document.getElementById('path-picker-modal-content');
  
  if (!modal || !content) return;
  
  // Get current value from input to start browsing there
  const input = document.getElementById(targetInputId);
  const currentPath = input ? input.value : '';
  
  // Load browser content via HTMX
  htmx.ajax('GET', '/api/filesystem/browse', {
    target: content,
    swap: 'innerHTML',
    values: {
      path: currentPath,
      target: targetInputId,
      mode: mode
    }
  });
  
  modal.showModal();
}

/**
 * Browse to a path entered in the path input
 */
function browsePath(targetInputId, mode) {
  const pathInput = document.getElementById('path-browser-current-path');
  const content = document.getElementById('path-picker-modal-content');
  
  if (!pathInput || !content) return;
  
  htmx.ajax('GET', '/api/filesystem/browse', {
    target: content,
    swap: 'innerHTML',
    values: {
      path: pathInput.value,
      target: targetInputId,
      mode: mode
    }
  });
}

/**
 * Show new folder input
 */
function showNewFolderInput(basePath, targetInputId, mode) {
  const container = document.getElementById('new-folder-input');
  const input = document.getElementById('new-folder-name');
  
  if (container) {
    container.classList.remove('hidden');
    if (input) {
      input.value = '';
      input.focus();
    }
  }
}

/**
 * Hide new folder input
 */
function hideNewFolderInput() {
  const container = document.getElementById('new-folder-input');
  if (container) {
    container.classList.add('hidden');
  }
}

/**
 * Create a new folder
 */
function createNewFolder(basePath, targetInputId, mode) {
  const nameInput = document.getElementById('new-folder-name');
  const content = document.getElementById('path-picker-modal-content');
  
  if (!nameInput || !nameInput.value.trim()) {
    alert('Please enter a folder name');
    return;
  }
  
  const folderName = nameInput.value.trim();
  
  // Create folder via API
  fetch('/api/filesystem/mkdir', {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: `path=${encodeURIComponent(basePath)}&name=${encodeURIComponent(folderName)}`
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      // Browse to the new folder
      htmx.ajax('GET', '/api/filesystem/browse', {
        target: content,
        swap: 'innerHTML',
        values: {
          path: data.path,
          target: targetInputId,
          mode: mode
        }
      });
    } else {
      alert('Error: ' + (data.error || 'Could not create folder'));
    }
  })
  .catch(err => {
    alert('Error creating folder: ' + err);
  });
}

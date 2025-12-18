/**
 * Report UI Functionality
 * Common JavaScript for all report pages (accessibility, image, landing hub, etc.)
 */

/**
 * Toggle a dropdown menu open/closed
 * @param {string} dropdownId - ID of the dropdown to toggle
 */
function toggleDropdown(dropdownId) {
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;

    const allDropdowns = document.querySelectorAll('.nav-dropdown');

    // Close all other dropdowns
    allDropdowns.forEach(d => {
        if (d.id !== dropdownId) {
            d.classList.remove('open');
            const button = d.querySelector('.nav-dropdown-toggle');
            if (button) button.setAttribute('aria-expanded', 'false');
        }
    });

    // Toggle current dropdown
    dropdown.classList.toggle('open');
    const button = dropdown.querySelector('.nav-dropdown-toggle');
    const isOpen = dropdown.classList.contains('open');
    button.setAttribute('aria-expanded', isOpen);

    // Focus on search input if dropdown opened
    if (isOpen) {
        const searchInput = dropdown.querySelector('.nav-dropdown-search input');
        if (searchInput) {
            setTimeout(() => searchInput.focus(), 100);
        }
    }
}

/**
 * Filter dropdown items by search query
 * @param {string} dropdownId - ID of the dropdown
 * @param {string} query - Search query
 */
function filterDropdownItems(dropdownId, query) {
    const dropdown = document.getElementById(dropdownId);
    if (!dropdown) return;

    const items = dropdown.querySelectorAll('.nav-dropdown-item');
    const searchTerm = query.toLowerCase().trim();

    let visibleCount = 0;

    items.forEach(item => {
        const text = item.textContent.toLowerCase();
        const isVisible = text.includes(searchTerm);
        item.style.display = isVisible ? '' : 'none';
        if (isVisible) visibleCount++;
    });

    // Show "no results" message if needed
    const itemsContainer = dropdown.querySelector('.nav-dropdown-items');
    let emptyState = itemsContainer.querySelector('.nav-dropdown-empty');

    if (visibleCount === 0 && searchTerm.length > 0) {
        if (!emptyState) {
            emptyState = document.createElement('div');
            emptyState.className = 'nav-dropdown-empty';
            emptyState.innerHTML = '<div class="nav-dropdown-empty-icon">🔍</div><div>No matches found</div>';
            itemsContainer.appendChild(emptyState);
        }
    } else if (emptyState) {
        emptyState.remove();
    }
}

/**
 * Initialize dropdown event listeners
 */
function initializeDropdownListeners() {
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
        const isDropdownClick = event.target.closest('.nav-dropdown');
        if (!isDropdownClick) {
            document.querySelectorAll('.nav-dropdown').forEach(dropdown => {
                dropdown.classList.remove('open');
                const button = dropdown.querySelector('.nav-dropdown-toggle');
                if (button) button.setAttribute('aria-expanded', 'false');
            });
        }
    });

    // Keyboard navigation for dropdowns
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Escape') {
            document.querySelectorAll('.nav-dropdown').forEach(dropdown => {
                dropdown.classList.remove('open');
                const button = dropdown.querySelector('.nav-dropdown-toggle');
                if (button) {
                    button.setAttribute('aria-expanded', 'false');
                    button.focus();
                }
            });
        }
    });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeDropdownListeners);
} else {
    initializeDropdownListeners();
}

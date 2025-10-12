class MultiSelect {
    constructor(container) {
        this.container = container;
        this.name = container.dataset.name;
        this.selectedItems = new Map();

        // Parse options from data attribute
        try {
            this.options = JSON.parse(container.dataset.options || '[]');
        } catch (e) {
            console.error('Failed to parse multiselect options:', e);
            this.options = [];
        }

        this.selectedItemsContainer = container.querySelector('.selected-items');
        this.input = container.querySelector('.multiselect-input');
        this.dropdown = container.querySelector('.multiselect-dropdown');
        this.menu = container.querySelector('.multiselect-dropdown ul');

        this.init();
    }

    init() {
        this.renderOptions();
        this.attachEventListeners();
    }

    renderOptions() {
        this.menu.innerHTML = '';

        this.options.forEach(option => {
            const li = document.createElement('li');
            li.innerHTML = `<a>${option.label}</a>`;
            li.dataset.id = option.id;
            li.dataset.value = option.value;
            li.dataset.label = option.label;

            if (this.selectedItems.has(option.id)) {
                li.classList.add('selected');
            }

            li.addEventListener('click', () => this.toggleOption(option));
            this.menu.appendChild(li);
        });
    }

    attachEventListeners() {
        // Show dropdown on focus
        this.input.addEventListener('focus', () => {
            this.dropdown.classList.remove('hidden');
        });

        // Search functionality
        this.input.addEventListener('input', (e) => {
            const searchTerm = e.target.value.toLowerCase();
            const items = this.menu.querySelectorAll('li');

            items.forEach(item => {
                const label = item.dataset.label.toLowerCase();
                if (label.includes(searchTerm)) {
                    item.classList.remove('hidden');
                } else {
                    item.classList.add('hidden');
                }
            });

            this.dropdown.classList.remove('hidden');
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!this.container.contains(e.target)) {
                this.dropdown.classList.add('hidden');
            }
        });
    }

    toggleOption(option) {
        if (this.selectedItems.has(option.id)) {
            this.removeItem(option.id);
        } else {
            this.addItem(option);
        }

        this.updateDropdownState();
        this.clearSearch();
    }

    addItem(option) {
        this.selectedItems.set(option.id, option);
        this.renderSelectedItems();
        this.input.value = '';
        this.input.focus();
    }

    removeItem(id) {
        this.selectedItems.delete(id);
        this.renderSelectedItems();
        this.updateDropdownState();
    }

    clearSearch() {
        this.input.value = '';
        const items = this.menu.querySelectorAll('li');
        items.forEach(item => {
            item.classList.remove('hidden');
        });
    }

    renderSelectedItems() {
        this.selectedItemsContainer.innerHTML = '';

        this.selectedItems.forEach(option => {
            const badge = document.createElement('div');
            badge.className = 'selected-item';
            badge.innerHTML = `
                <span>${option.label}</span>
                <button type="button" aria-label="Remove ${option.label}">×</button>
                <input type="hidden" name="${this.name}" value="${option.value}" />
            `;

            const removeBtn = badge.querySelector('button');
            removeBtn.addEventListener('click', () => this.removeItem(option.id));

            this.selectedItemsContainer.appendChild(badge);
        });
    }

    updateDropdownState() {
        const items = this.menu.querySelectorAll('li');
        items.forEach(item => {
            const id = parseInt(item.dataset.id);
            if (this.selectedItems.has(id)) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }
}

// Observe existing containers
// Initialize multiselect with Intersection Observer
const initMultiselect = (container) => {
    // Check if already initialized
    if (container.dataset.multiselectInitialized === 'true') {
        return;
    }

    container.dataset.multiselectInitialized = 'true';
    new MultiSelect(container);
};

// Create Intersection Observer (at module level)
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            initMultiselect(entry.target);
        }
    });
}, {
    root: null,
    rootMargin: '50px',
    threshold: 0.1
});

// Observe existing containers (at module level)
const observeMultiselects = () => {
    const containers = document.querySelectorAll('.multiselect-container:not([data-multiselect-initialized])');
    containers.forEach(container => {
        observer.observe(container);
        // Also initialize immediately if already visible
        // This helps with Alpine AJAX loaded content that's immediately visible
        const rect = container.getBoundingClientRect();
        if (rect.top < window.innerHeight && rect.bottom > 0) {
            initMultiselect(container);
        }
    });
};

// Initial observation on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', observeMultiselects);
} else {
    observeMultiselects();
}

// Re-observe when new content is added via Alpine AJAX
document.addEventListener('alpine-ajax:after-request', () => {
    // Add a small delay to ensure DOM is updated
    setTimeout(observeMultiselects, 10);
});

// Also observe on Alpine's morph events (if using Alpine Morph)
document.addEventListener('alpine:morph', () => {
    setTimeout(observeMultiselects, 10);
});

// Listen for custom Alpine events that might add content
document.addEventListener('alpine:initialized', () => {
    observeMultiselects();
});

// Use MutationObserver as a fallback to catch any dynamically added containers
const setupMutationObserver = () => {
    if (!document.body) {
        return;
    }

    const mutationObserver = new MutationObserver((mutations) => {
        let shouldObserve = false;
        mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
                if (node.nodeType === 1) { // Element node
                    if (node.classList && node.classList.contains('multiselect-container')) {
                        shouldObserve = true;
                    } else if (node.querySelector) {
                        const containers = node.querySelectorAll('.multiselect-container');
                        if (containers.length > 0) {
                            shouldObserve = true;
                        }
                    }
                }
            });
        });
        if (shouldObserve) {
            observeMultiselects();
        }
    });

    // Start observing the document for changes
    mutationObserver.observe(document.body, {
        childList: true,
        subtree: true
    });
};

// Setup MutationObserver when ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', setupMutationObserver);
} else {
    setupMutationObserver();
}
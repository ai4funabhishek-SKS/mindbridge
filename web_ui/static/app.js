// mindbridge Web UI - Frontend JavaScript

// Global utilities
window.mindbridge = {
    // Toast notifications
    toast: function(type, title, message = '') {
        const container = document.getElementById('toast-container') || this.createToastContainer();
        const toast = document.createElement('div');
        toast.className = `toast toast-${type} animate-slide-in`;
        const icons = {
            success: 'fa-check-circle text-green-500',
            error: 'fa-times-circle text-red-500',
            warning: 'fa-exclamation-triangle text-yellow-500',
            info: 'fa-info-circle text-blue-500'
        };
        toast.innerHTML = `
            <div class="flex items-start">
                <i class="fas ${icons[type]} mt-0.5 mr-3"></i>
                <div>
                    <p class="font-medium">${title}</p>
                    ${message ? `<p class="text-sm text-gray-600">${message}</p>` : ''}
                </div>
            </div>
        `;
        container.appendChild(toast);
        setTimeout(() => toast.remove(), 5000);
    },
    
    createToastContainer: function() {
        const container = document.createElement('div');
        container.id = 'toast-container';
        container.className = 'fixed bottom-4 right-4 z-50 space-y-2';
        document.body.appendChild(container);
        return container;
    },
    
    // API helper
    api: async function(endpoint, options = {}) {
        const response = await fetch(endpoint, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        return response.json();
    },
    
    // Config helpers
    config: {
        load: async function() {
            return mindbridge.api('/api/config');
        },
        save: async function(config) {
            return mindbridge.api('/api/config', {
                method: 'POST',
                body: JSON.stringify({ config })
            });
        }
    },
    
    // LLM testing
    testProvider: async function(provider, model, apiKey, baseUrl) {
        return mindbridge.api('/api/test/llm', {
            method: 'POST',
            body: JSON.stringify({ provider, model, api_key: apiKey, base_url: baseUrl })
        });
    },
    
    // Folder testing
    testFolders: async function(folders) {
        return mindbridge.api('/api/test/folders', {
            method: 'POST',
            body: JSON.stringify({ watch_folders: folders })
        });
    },
    
    // Run tests
    runTests: async function() {
        return mindbridge.api('/api/test/run', { method: 'POST' });
    },
    
    // Run ingestion
    runIngestion: async function() {
        return mindbridge.api('/api/ingest/run', { method: 'POST' });
    },
    
    // Status check
    getStatus: async function() {
        return mindbridge.api('/api/status');
    },
    
    // Config management
    config: {
        get: async function() {
            return mindbridge.api('/api/config');
        },
        save: async function(config) {
            return mindbridge.api('/api/config', {
                method: 'POST',
                body: JSON.stringify({ config })
            });
        }
    },
    
    // Auto-rules
    autoRules: {
        get: async function() {
            return mindbridge.api('/api/auto-rules');
        },
        save: async function(rules) {
            return mindbridge.api('/api/auto-rules', {
                method: 'POST',
                body: JSON.stringify(rules)
            });
        }
    },
    
    // Utility functions
    utils: {
        formatBytes: function(bytes) {
            if (bytes === 0) return '0 Bytes';
            const k = 1024;
            const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
            const i = Math.floor(Math.log(bytes) / Math.log(k));
            return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
        },
        
        formatDate: function(date) {
            return new Date(date).toLocaleString();
        },
        
        formatDuration: function(ms) {
            if (ms < 1000) return `${ms}ms`;
            if (ms < 60000) return `${(ms / 1000).toFixed(1)}s`;
            if (ms < 3600000) return `${(ms / 60000).toFixed(1)}m`;
            return `${(ms / 3600000).toFixed(1)}h`;
        },
        
        debounce: function(func, wait) {
            let timeout;
            return function(...args) {
                clearTimeout(timeout);
                timeout = setTimeout(() => func.apply(this, args), wait);
            };
        },
        
        throttle: function(func, limit) {
            let inThrottle;
            return function(...args) {
                if (!inThrottle) {
                    func.apply(this, args);
                    inThrottle = true;
                    setTimeout(() => inThrottle = false, limit);
                }
            };
        },
        
        copyToClipboard: async function(text) {
            try {
                await navigator.clipboard.writeText(text);
                return true;
            } catch (err) {
                return false;
            }
        },
        
        downloadFile: function(content, filename, type = 'text/plain') {
            const blob = new Blob([content], { type });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = filename;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        }
    }
};

// Auto-initialize on DOM ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    document.querySelectorAll('[data-tooltip]').forEach(el => {
        el.addEventListener('mouseenter', function() {
            const tooltip = document.createElement('div');
            tooltip.className = 'absolute z-50 px-2 py-1 text-xs bg-gray-900 text-white rounded shadow-lg';
            tooltip.textContent = this.dataset.tooltip;
            document.body.appendChild(tooltip);
            
            const rect = this.getBoundingClientRect();
            tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
            tooltip.style.top = rect.top - tooltip.offsetHeight - 8 + 'px';
            
            this._tooltip = tooltip;
        });
        
        el.addEventListener('mouseleave', function() {
            if (this._tooltip) {
                this._tooltip.remove();
            }
        });
    });
    
    // Add smooth scroll to all anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
    
    // Add copy button to code blocks
    document.querySelectorAll('pre code').forEach(block => {
        const wrapper = block.parentElement;
        if (!wrapper.classList.contains('code-wrapper')) {
            const wrapper = document.createElement('div');
            wrapper.className = 'code-wrapper relative';
            block.parentNode.insertBefore(wrapper, block);
            wrapper.appendChild(block);
            
            const btn = document.createElement('button');
            btn.className = 'absolute top-2 right-2 px-2 py-1 text-xs bg-gray-800 text-white rounded opacity-0 hover:opacity-100 transition-opacity';
            btn.innerHTML = '<i class="fas fa-copy mr-1"></i>Copy';
            btn.onclick = async () => {
                await navigator.clipboard.writeText(block.textContent);
                mindbridge.toast('success', 'Copied!');
            };
            wrapper.style.position = 'relative';
            wrapper.appendChild(btn);
        }
    });
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = mindbridge;
}
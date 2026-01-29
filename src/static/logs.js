class LogViewer {
    constructor() {
        this.logs = [];
        this.autoRefreshInterval = null;
        this.init();
    }

    async init() {
        this.bindEvents();
        await this.loadLoggers();
        await this.loadLogs();
    }

    bindEvents() {
        document.getElementById('refreshBtn').addEventListener('click', () => this.loadLogs());
        document.getElementById('clearBtn').addEventListener('click', () => this.clearLogs());
        document.getElementById('levelFilter').addEventListener('change', () => this.loadLogs());
        document.getElementById('loggerFilter').addEventListener('change', () => this.loadLogs());
        document.getElementById('limitFilter').addEventListener('change', () => this.loadLogs());
        document.getElementById('autoRefresh').addEventListener('change', (e) => this.toggleAutoRefresh(e.target.checked));
    }

    async loadLoggers() {
        try {
            const response = await fetch('/api/logs/loggers');
            const data = await response.json();

            if (data.success) {
                const select = document.getElementById('loggerFilter');
                data.loggers.forEach(logger => {
                    const option = document.createElement('option');
                    option.value = logger;
                    option.textContent = logger;
                    select.appendChild(option);
                });
            }
        } catch (error) {
            console.error('Error loading loggers:', error);
        }
    }

    async loadLogs() {
        try {
            const level = document.getElementById('levelFilter').value;
            const logger = document.getElementById('loggerFilter').value;
            const limit = document.getElementById('limitFilter').value;

            const params = new URLSearchParams();
            if (level) params.append('level', level);
            if (logger) params.append('logger', logger);
            params.append('limit', limit);

            const response = await fetch(`/api/logs/recent?${params}`);
            const data = await response.json();

            if (data.success) {
                this.logs = data.logs;
                this.renderLogs();
                document.getElementById('logCount').textContent = `${data.total} entries`;
            } else {
                console.error('Error loading logs:', data.message);
                this.showError(data.message);
            }
        } catch (error) {
            console.error('Error loading logs:', error);
            this.showError('Failed to load logs. Please try again.');
        }
    }

    renderLogs() {
        const container = document.getElementById('logEntries');

        if (this.logs.length === 0) {
            container.innerHTML = '<div class="text-gray-400 text-center py-8">No logs found</div>';
            return;
        }

        container.innerHTML = this.logs.map(log => `
            <div class="log-entry">
                <span class="text-gray-400">${new Date(log.timestamp * 1000).toLocaleString()}</span>
                <span class="log-level-${log.level} font-bold ml-2">[${log.level}]</span>
                <span class="text-blue-400 ml-2">${this.escapeHtml(log.logger)}</span>
                <span class="ml-2">${this.escapeHtml(log.raw)}</span>
            </div>
        `).join('');

        // Auto-scroll to bottom
        const logContainer = document.getElementById('logContainer');
        logContainer.scrollTop = logContainer.scrollHeight;
    }

    async clearLogs() {
        if (!confirm('Are you sure you want to clear all in-memory logs?')) {
            return;
        }

        try {
            const response = await fetch('/api/logs/clear', { method: 'POST' });
            const data = await response.json();

            if (data.success) {
                await this.loadLogs();
            } else {
                console.error('Error clearing logs:', data.message);
                alert('Failed to clear logs: ' + data.message);
            }
        } catch (error) {
            console.error('Error clearing logs:', error);
            alert('Failed to clear logs. Please try again.');
        }
    }

    toggleAutoRefresh(enabled) {
        if (enabled) {
            this.autoRefreshInterval = setInterval(() => this.loadLogs(), 5000);
        } else {
            if (this.autoRefreshInterval) {
                clearInterval(this.autoRefreshInterval);
                this.autoRefreshInterval = null;
            }
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showError(message) {
        const container = document.getElementById('logEntries');
        container.innerHTML = `<div class="text-red-400 text-center py-8"><i class="fas fa-exclamation-triangle mr-2"></i>${this.escapeHtml(message)}</div>`;
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    new LogViewer();
});

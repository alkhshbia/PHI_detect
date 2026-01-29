// dashboard.js
// Fetch trends and populate dashboard with charts

let dailyTrendChart = null;
let topCountriesChart = null;
let topHazardsChart = null;

document.addEventListener('DOMContentLoaded', () => {
    loadTrends();
});

async function loadTrends() {
    try {
        const response = await fetch('/api/signals/trends');
        const result = await response.json();

        if (!result.success) {
            console.error('Failed to load trends:', result.message);
            return;
        }

        const { daily_counts, top_countries, top_hazards, cutoff_info } = result;

        // Update cutoff info
        if (cutoff_info) {
            const cutoffEl = document.getElementById('cutoffInfo');
            if (cutoffEl) {
                const periodEnd = new Date(cutoff_info.current_period_end);
                cutoffEl.textContent = `(Current period ends: ${periodEnd.toLocaleString()})`;
            }
        }

        // Render charts
        renderDailyTrendChart(daily_counts);
        renderTopCountriesChart(top_countries);
        renderTopHazardsChart(top_hazards);

        // Render text lists
        renderTopList('topCountriesList', top_countries, 'country');
        renderTopList('topHazardsList', top_hazards, 'hazard');

    } catch (error) {
        console.error('Error loading trends:', error);
    }
}

function renderDailyTrendChart(dailyCounts) {
    const ctx = document.getElementById('dailyTrendChart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (dailyTrendChart) {
        dailyTrendChart.destroy();
    }

    const labels = dailyCounts.map(d => {
        const date = new Date(d.date);
        return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    });
    const totalCounts = dailyCounts.map(d => d.count);
    const trueSignalCounts = dailyCounts.map(d => d.true_signals);

    dailyTrendChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Total Articles',
                    data: totalCounts,
                    backgroundColor: 'rgba(147, 51, 234, 0.7)',
                    borderColor: 'rgba(147, 51, 234, 1)',
                    borderWidth: 1
                },
                {
                    label: 'Potential Signals',
                    data: trueSignalCounts,
                    backgroundColor: 'rgba(34, 197, 94, 0.7)',
                    borderColor: 'rgba(34, 197, 94, 1)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'top',
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function renderTopCountriesChart(topCountries) {
    const ctx = document.getElementById('topCountriesChart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (topCountriesChart) {
        topCountriesChart.destroy();
    }

    if (!topCountries || topCountries.length === 0) {
        ctx.parentElement.innerHTML = '<div class="flex items-center justify-center h-full text-gray-500">No data available</div>';
        return;
    }

    const labels = topCountries.map(c => c.country);
    const counts = topCountries.map(c => c.count);

    const colors = [
        'rgba(34, 197, 94, 0.7)',
        'rgba(59, 130, 246, 0.7)',
        'rgba(249, 115, 22, 0.7)',
        'rgba(168, 85, 247, 0.7)',
        'rgba(236, 72, 153, 0.7)'
    ];

    const borderColors = [
        'rgba(34, 197, 94, 1)',
        'rgba(59, 130, 246, 1)',
        'rgba(249, 115, 22, 1)',
        'rgba(168, 85, 247, 1)',
        'rgba(236, 72, 153, 1)'
    ];

    topCountriesChart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: counts,
                backgroundColor: colors.slice(0, topCountries.length),
                borderColor: borderColors.slice(0, topCountries.length),
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                }
            }
        }
    });
}

function renderTopHazardsChart(topHazards) {
    const ctx = document.getElementById('topHazardsChart');
    if (!ctx) return;

    // Destroy existing chart if it exists
    if (topHazardsChart) {
        topHazardsChart.destroy();
    }

    if (!topHazards || topHazards.length === 0) {
        ctx.parentElement.innerHTML = '<div class="flex items-center justify-center h-full text-gray-500">No data available</div>';
        return;
    }

    const labels = topHazards.map(h => h.hazard);
    const counts = topHazards.map(h => h.count);

    topHazardsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Count',
                data: counts,
                backgroundColor: 'rgba(239, 68, 68, 0.7)',
                borderColor: 'rgba(239, 68, 68, 1)',
                borderWidth: 1
            }]
        },
        options: {
            indexAxis: 'y',
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function renderTopList(elementId, items, fieldName) {
    const listEl = document.getElementById(elementId);
    if (!listEl) return;

    if (!Array.isArray(items) || items.length === 0) {
        listEl.innerHTML = '<li class="text-gray-500">No data available</li>';
        return;
    }

    listEl.innerHTML = items.map((item, index) => {
        const label = item[fieldName] || 'Unknown';
        const count = item.count || 0;

        // Create link to articles page with filter
        const params = new URLSearchParams();
        if (fieldName === 'country') {
            params.append('countries', label);
        } else if (fieldName === 'hazard') {
            params.append('hazards', label);
        }
        const href = `index.html?${params.toString()}`;

        return `
            <li class="flex justify-between items-center py-2 px-3 rounded ${index % 2 === 0 ? 'bg-gray-50' : ''}">
                <a href="${href}" class="text-blue-600 hover:underline flex-1">${label}</a>
                <span class="font-semibold bg-gray-200 px-2 py-1 rounded text-sm">${count}</span>
            </li>
        `;
    }).join('');
}

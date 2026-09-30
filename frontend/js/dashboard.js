document.addEventListener('DOMContentLoaded', () => {
    fetchDashboardData();
});

let sentimentChartInstance = null;

function fetchDashboardData() {
    fetch('/api/dashboard')
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success' && res.data) {
                renderDashboard(res.data);
            }
        })
        .catch(err => {
            console.error("Failed to load dashboard data:", err);
        });
}

function renderDashboard(data) {
    // 1. KPIs
    if (data.total_feedback) {
        document.getElementById('kpiTotal').textContent = data.total_feedback.toLocaleString();
    }
    if (data.positive_percentage !== undefined) {
        document.getElementById('kpiPosPct').textContent = `${data.positive_percentage}%`;
    }
    if (data.top_topics) {
        document.getElementById('kpiThemes').textContent = data.top_topics.length;
    }
    if (data.emerging_issues) {
        document.getElementById('kpiEmerging').textContent = data.emerging_issues.length;
    }
    if (data.date_range) {
        document.getElementById('dateRangeText').textContent = `${data.date_range.start} - ${data.date_range.end}`;
    }

    // 2. Chart.js Sentiment Chart
    const ctx = document.getElementById('sentimentChart').getContext('2d');
    const sot = data.sentiment_over_time || {
        labels: ['Jan 2026', 'Feb 2026', 'Mar 2026'],
        positive: [55, 60, 65],
        neutral: [20, 18, 15],
        negative: [25, 22, 20]
    };

    if (sentimentChartInstance) {
        sentimentChartInstance.destroy();
    }

    sentimentChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: sot.labels,
            datasets: [
                {
                    label: 'Positive',
                    data: sot.positive,
                    borderColor: '#4D8B63',
                    backgroundColor: 'rgba(77, 139, 99, 0.1)',
                    borderWidth: 3,
                    fill: true,
                    tension: 0.4
                },
                {
                    label: 'Neutral',
                    data: sot.neutral,
                    borderColor: '#C9784B',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.4
                },
                {
                    label: 'Negative',
                    data: sot.negative,
                    borderColor: '#73508D',
                    backgroundColor: 'transparent',
                    borderWidth: 2,
                    tension: 0.4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                x: {
                    grid: { display: false }
                },
                y: {
                    min: 0,
                    max: 100,
                    ticks: {
                        callback: function(val) { return val + '%'; }
                    },
                    grid: { color: '#E4D8C8' }
                }
            }
        }
    });

    // 3. Top Customer Issues Progress Bars
    const topIssuesList = document.getElementById('topIssuesList');
    if (topIssuesList && data.top_topics) {
        topIssuesList.innerHTML = '';
        data.top_topics.forEach((item, index) => {
            const row = document.createElement('div');
            row.className = 'issue-item';
            row.innerHTML = `
                <div class="issue-row">
                    <span>${index + 1}. ${item.name}</span>
                    <span>${item.percentage}%</span>
                </div>
                <div class="issue-bar-bg">
                    <div class="issue-bar-fill" style="width: ${item.percentage}%;"></div>
                </div>
            `;
            topIssuesList.appendChild(row);
        });
    }

    // 4. Emerging Issues Cards
    const emergingGrid = document.getElementById('emergingGrid');
    if (emergingGrid && data.emerging_issues) {
        emergingGrid.innerHTML = '';
        data.emerging_issues.forEach(item => {
            const card = document.createElement('div');
            card.className = 'emerging-card';
            
            const isUp = item.is_increasing;
            const arrow = isUp ? '↑' : '↓';
            const badgeClass = isUp ? 'badge-orange' : 'badge-green';

            card.innerHTML = `
                <div style="font-weight: 700; font-size: 0.95rem;">${item.name}</div>
                <span class="badge ${badgeClass}">${arrow} ${Math.abs(item.change_pct)}%</span>
            `;
            emergingGrid.appendChild(card);
        });
    }
}

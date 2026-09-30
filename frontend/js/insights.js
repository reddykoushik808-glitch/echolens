document.addEventListener('DOMContentLoaded', () => {
    fetch('/api/insights')
        .then(res => res.json())
        .then(res => {
            if (res.status === 'success' && res.insights && res.insights.length > 0) {
                renderInsights(res.insights);
            }
        })
        .catch(err => console.error("Error fetching insights:", err));
});

function renderInsights(insights) {
    const container = document.getElementById('insightsContainer');
    if (!container) return;

    container.innerHTML = '';
    insights.forEach(item => {
        const card = document.createElement('div');
        card.className = 'insight-card';

        let badgeClass = 'badge-green';
        let icon = '🛒';
        let iconBg = 'var(--green-light)';
        let iconColor = 'var(--green-accent)';

        if (item.metric_type === 'warning') {
            badgeClass = 'badge-orange';
            icon = '💳';
            iconBg = 'var(--orange-light)';
            iconColor = 'var(--orange-accent)';
        } else if (item.metric_type === 'purple') {
            badgeClass = 'badge-purple';
            icon = '📱';
            iconBg = 'var(--purple-light)';
            iconColor = 'var(--purple-accent)';
        }

        card.innerHTML = `
            <div class="insight-left">
                <div class="insight-icon-box" style="background-color: ${iconBg}; color: ${iconColor};">${icon}</div>
                <div>
                    <div class="insight-title">${item.title}</div>
                    <div class="insight-desc">${item.description}</div>
                </div>
            </div>
            <div class="insight-badge-box">
                <span class="badge ${badgeClass}" style="font-size: 0.95rem; padding: 6px 14px;">${item.metric_label}</span>
            </div>
        `;
        container.appendChild(card);
    });
}

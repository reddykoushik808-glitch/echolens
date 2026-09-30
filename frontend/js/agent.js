document.addEventListener('DOMContentLoaded', () => {
    if (window.location.hash === '#memory') {
        scrollToMemorySection();
    }
});

function scrollToMemorySection() {
    const memEl = document.getElementById('memory');
    if (memEl) {
        memEl.scrollIntoView({ behavior: 'smooth' });
        const bodyEl = document.getElementById('accMemories');
        if (bodyEl) bodyEl.style.display = 'flex';
    }
}

function toggleAccordion(id) {
    const el = document.getElementById(id);
    if (el) {
        el.style.display = el.style.display === 'none' ? 'flex' : 'none';
    }
}

function handleKeyPress(e) {
    if (e.key === 'Enter') {
        sendQuestion();
    }
}

function askPresetQuestion(text) {
    document.getElementById('agentInput').value = text;
    sendQuestion();
}

function sendQuestion() {
    const input = document.getElementById('agentInput');
    const question = input.value.trim();
    if (!question) return;

    input.value = '';

    const chatBox = document.getElementById('chatBox');
    
    // Append User Bubble
    const userBubble = document.createElement('div');
    userBubble.className = 'user-bubble';
    userBubble.textContent = question;
    chatBox.appendChild(userBubble);

    // Append Loading State Response Card
    const card = document.createElement('div');
    card.className = 'agent-response-card';
    card.innerHTML = `
        <div class="agent-response-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 0 0 8 20c9 0 14-11 14-11M17 8A18.5 18.5 0 0 0 2 3c0 9 6.5 14.5 10 14.5"/>
            </svg>
            AI INSIGHT &bull; <span style="font-weight: 500; opacity: 0.7;">Recalling Hindsight Memory...</span>
        </div>
        <div class="agent-answer-text" style="color: var(--secondary-text); font-style: italic;">
            Analyzing feedback analytics, recalling Hindsight long-term memories, and synthesizing response...
        </div>
    `;
    chatBox.appendChild(card);
    card.scrollIntoView({ behavior: 'smooth' });

    // Call Backend API
    fetch('/api/agent/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: question })
    })
    .then(res => res.json())
    .then(data => {
        renderAgentResponse(card, data);
    })
    .catch(err => {
        console.error("Agent API error:", err);
        card.querySelector('.agent-answer-text').textContent = "Unable to process question right now. Please try again.";
    });
}

function renderAgentResponse(cardEl, data) {
    const answer = data.answer || "No response generated.";
    const memories = data.memories_used || [];
    const evidence = data.evidence || {};
    const metrics = data.metrics || {};
    const feedbackItems = evidence.feedback || [];
    const releaseItems = evidence.releases || [];

    const feedbackHtml = feedbackItems.map(item => 
        `<div class="memory-item">"${item.text}" &mdash; <span style="color: var(--secondary-text);">${item.date} (${item.channel})</span></div>`
    ).join('') || '<div class="memory-item">No specific feedback quotes matched.</div>';

    const releaseHtml = releaseItems.map(item => 
        `<div class="memory-item"><strong>${item.date} &bull; ${item.feature}</strong>: ${item.description}</div>`
    ).join('') || '<div class="memory-item">No related releases found.</div>';

    const memoryHtml = memories.map(mem => 
        `<div class="memory-item">🧠 ${mem.text || mem}</div>`
    ).join('') || '<div class="memory-item">No historical memories recalled for this query.</div>';

    const cardId = 'card-' + Math.random().toString(36).substr(2, 9);

    cardEl.innerHTML = `
        <div class="agent-response-header">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M17 8C8 10 5.9 16.17 3.82 21.34L5.71 22l1-2.3A4.49 4.49 0 0 0 8 20c9 0 14-11 14-11M17 8A18.5 18.5 0 0 0 2 3c0 9 6.5 14.5 10 14.5"/>
            </svg>
            AI INSIGHT ${data.demo_mode ? '<span class="badge badge-purple" style="margin-left: 8px;">Demo Analytics Mode</span>' : ''}
        </div>

        <div class="agent-answer-text">
            ${answer}
        </div>

        <!-- Evidence Bar -->
        <div class="evidence-bar">
            <span>📊 ${metrics.records_analyzed || 500} feedback records</span>
            <span>📅 ${metrics.product_releases_count || 1} product releases</span>
            <span>🧠 ${memories.length} Hindsight memories</span>
        </div>

        <!-- Accordions -->
        <div style="display: flex; flex-direction: column; gap: 10px;">
            <div class="accordion-section">
                <div class="accordion-header" onclick="toggleAccordion('${cardId}-fb')">
                    <span>▼ Relevant Feedback (${feedbackItems.length})</span>
                    <span style="font-size: 0.8rem; color: var(--secondary-text);">Show quotes</span>
                </div>
                <div class="accordion-body" id="${cardId}-fb" style="display: none;">
                    ${feedbackHtml}
                </div>
            </div>

            <div class="accordion-section">
                <div class="accordion-header" onclick="toggleAccordion('${cardId}-rel')">
                    <span>▼ Relevant Product Releases (${releaseItems.length})</span>
                    <span style="font-size: 0.8rem; color: var(--secondary-text);">Show release</span>
                </div>
                <div class="accordion-body" id="${cardId}-rel" style="display: none;">
                    ${releaseHtml}
                </div>
            </div>

            <div class="accordion-section">
                <div class="accordion-header" onclick="toggleAccordion('${cardId}-mem')" style="background-color: var(--purple-light);">
                    <span style="color: var(--purple-accent); font-weight: 800;">▼ Hindsight Memories Used (${memories.length})</span>
                    <span style="font-size: 0.8rem; color: var(--purple-accent);">Recall from Hindsight</span>
                </div>
                <div class="accordion-body" id="${cardId}-mem" style="display: flex;">
                    ${memoryHtml}
                </div>
            </div>
        </div>
    `;

    cardEl.scrollIntoView({ behavior: 'smooth' });
}

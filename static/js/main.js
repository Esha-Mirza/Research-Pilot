/**
 * Multi-Agent Research Assistant Logic
 * Handles interactive tabs, live UI agent pipeline status, REST requests,
 * and result downloads.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Elements
    const topicInput = document.getElementById('topicInput');
    const runBtn = document.getElementById('runBtn');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const presetChips = document.querySelectorAll('.chip');
    const agentItems = document.querySelectorAll('.agent-item');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');

    // Global result storage
    let currentResults = null;

    // --- 1. Tab Switcher Logic ---
    tabBtns.forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const targetTab = btn.getAttribute('data-tab');

            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            const targetPane = document.getElementById(`tab-${targetTab}`);
            if (targetPane) {
                targetPane.classList.add('active');
            }
        });
    });

    // --- 2. Preset Chips Auto-fill ---
    presetChips.forEach(chip => {
        chip.addEventListener('click', () => {
            topicInput.value = chip.textContent.trim();
            topicInput.focus();
        });
    });

    // --- 3. Execute Research Process ---
    if (runBtn) {
        runBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const topic = topicInput.value.trim();

            if (!topic) {
                alert('Please enter a research topic first.');
                topicInput.focus();
                return;
            }

            setLoadingState(true);
            resetAgentStatuses();

            let agentSequenceTimer = null;

            try {
                // Simulate agent sequence visually while fetching
                agentSequenceTimer = simulateAgentPipeline();

                const response = await fetch('/api/research', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ topic: topic })
                });

                if (agentSequenceTimer) clearInterval(agentSequenceTimer);

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Server error occurred during research execution');
                }

                const data = await response.json();
                currentResults = data;

                // Mark agents as completed
                completeAllAgents();

                // Inject results
                renderResults(data);

            } catch (error) {
                if (agentSequenceTimer) clearInterval(agentSequenceTimer);
                console.error("Error running research pipeline:", error);
                alert(`Execution failed: ${error.message}`);
                resetAgentStatuses();
            } finally {
                setLoadingState(false);
            }
        });
    }

    // Trigger execution on Enter keypress
    if (topicInput) {
        topicInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                runBtn.click();
            }
        });
    }

    // --- Agent Status Helper Functions ---
    function simulateAgentPipeline() {
        let currentStep = 0;
        updateAgentStatus(0, 'active');

        return setInterval(() => {
            if (currentStep < agentItems.length - 1) {
                updateAgentStatus(currentStep, 'completed');
                currentStep++;
                updateAgentStatus(currentStep, 'active');
            }
        }, 1800);
    }

    function updateAgentStatus(index, status) {
        if (!agentItems[index]) return;

        const badge = agentItems[index].querySelector('.agent-badge');
        agentItems[index].classList.remove('active', 'completed');

        if (status === 'active') {
            agentItems[index].classList.add('active');
            if (badge) badge.textContent = 'Running...';
        } else if (status === 'completed') {
            agentItems[index].classList.add('completed');
            if (badge) badge.textContent = 'Completed';
        } else {
            if (badge) badge.textContent = 'Idle';
        }
    }

    function resetAgentStatuses() {
        agentItems.forEach((item, index) => {
            updateAgentStatus(index, 'idle');
        });
    }

    function completeAllAgents() {
        agentItems.forEach((item, index) => {
            updateAgentStatus(index, 'completed');
        });
    }

    function setLoadingState(isLoading) {
        if (isLoading) {
            runBtn.disabled = true;
            runBtn.style.opacity = '0.7';
            runBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Running...';
        } else {
            runBtn.disabled = false;
            runBtn.style.opacity = '1';
            runBtn.innerHTML = '<i class="fa-solid fa-rocket"></i> Run Pipeline';
        }
    }

    // --- Render Results ---
    function renderResults(results) {
        document.getElementById('tab-search').innerHTML =
            `<div class="content-display">${escapeHtml(results.search || 'No search findings.')}</div>`;

        document.getElementById('tab-summary').innerHTML =
            `<div class="content-display">${escapeHtml(results.summary || 'No summary generated.')}</div>`;

        document.getElementById('tab-feedback').innerHTML =
            `<div class="content-display">${escapeHtml(results.feedback || 'No feedback produced.')}</div>`;

        document.getElementById('tab-report').innerHTML =
            `<div class="content-display">${escapeHtml(results.report || 'No final report generated.')}</div>`;
    }

    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // --- 4. Copy to Clipboard ---
    if (copyBtn) {
        copyBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const activePane = document.querySelector('.tab-pane.active .content-display');
            if (!activePane || !activePane.textContent.trim()) {
                alert('Nothing to copy yet!');
                return;
            }

            navigator.clipboard.writeText(activePane.textContent)
                .then(() => {
                    const originalText = copyBtn.innerHTML;
                    copyBtn.innerHTML = '<i class="fa-solid fa-check"></i> Copied!';
                    setTimeout(() => copyBtn.innerHTML = originalText, 2000);
                })
                .catch(err => console.error('Failed to copy content: ', err));
        });
    }

    // --- 5. Export Research Data ---
    if (downloadBtn) {
        downloadBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (!currentResults) {
                alert('Run research first before downloading output!');
                return;
            }

            const topic = topicInput.value.trim() || 'research';
            const exportText = `=== MULTI-AGENT RESEARCH PACKAGE ===\nTopic: ${topic}\n\n` +
                `1. SEARCH FINDINGS:\n${currentResults.search}\n\n` +
                `2. SUMMARY:\n${currentResults.summary}\n\n` +
                `3. FACT CHECK & REVIEW:\n${currentResults.feedback}\n\n` +
                `4. FINAL REPORT:\n${currentResults.report}\n`;

            const blob = new Blob([exportText], { type: 'text/plain;charset=utf-8' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');

            a.href = url;
            a.download = `Research_${topic.replace(/\s+/g, '_')}.txt`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }
});
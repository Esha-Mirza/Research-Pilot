/**
 * Multi-Agent Research Assistant Logic
 * Handles interactive tabs, live UI agent pipeline status, AJAX requests,
 * and result downloads.
 */

document.addEventListener('DOMContentLoaded', () => {
    // DOM Element Selections
    const topicInput = document.getElementById('topicInput');
    const runBtn = document.getElementById('runBtn');
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    const presetChips = document.querySelectorAll('.chip');
    const agentItems = document.querySelectorAll('.agent-item');
    const copyBtn = document.getElementById('copyBtn');
    const downloadBtn = document.getElementById('downloadBtn');

    // Global memory storage for fetched results
    let currentResults = null;

    // --- Tab Switcher Logic ---
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const targetTab = btn.getAttribute('data-tab');

            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));

            btn.classList.add('active');
            document.getElementById(`tab-${targetTab}`).classList.add('active');
        });
    });

    // --- Preset Chips Auto-fill ---
    presetChips.forEach(chip => {
        chip.addEventListener('click', () => {
            topicInput.value = chip.textContent.trim();
            topicInput.focus();
        });
    });

    // --- Execute Research Process ---
    runBtn.addEventListener('click', async () => {
        const topic = topicInput.value.trim();

        if (!topic) {
            alert('Please enter a research topic first.');
            topicInput.focus();
            return;
        }

        setLoadingState(true);
        resetAgentStatuses();

        try {
            // Simulate agent stage sequence visually while awaiting backend execution
            const agentSequenceTimer = simulateAgentPipeline();

            // Send REST request to Flask backend
            const response = await fetch('/api/research', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ topic: topic })
            });

            clearInterval(agentSequenceTimer);

            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.error || 'Server error occurred during research execution');
            }

            const data = await response.json();
            currentResults = data;

            // Mark all steps as complete in agent UI
            completeAllAgents();

            // Inject received content into respective views
            renderResults(data);

        } catch (error) {
            console.error("Error running research pipeline:", error);
            alert(`Execution failed: ${error.message}`);
            resetAgentStatuses();
        } finally {
            setLoadingState(false);
        }
    });

    // Enter key triggers action
    topicInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            runBtn.click();
        }
    });

    // --- Visual Pipeline Simulation Helper ---
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
            runBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
        } else {
            runBtn.disabled = false;
            runBtn.style.opacity = '1';
            runBtn.innerHTML = '<i class="fa-solid fa-rocket"></i> Run Pipeline';
        }
    }

    // --- Display Render Function ---
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

    // Escape raw output safely
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // --- Copy to Clipboard Handler ---
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
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

    // --- Export Research Package ---
    if (downloadBtn) {
        downloadBtn.addEventListener('click', () => {
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
/**
 * Main application logic for TransBack translation tool
 */

// DOM Elements
const form = document.getElementById('translateForm');
const translateBtn = document.getElementById('translateBtn');
const buttonText = document.getElementById('buttonText');
const loadingSpinner = document.getElementById('loadingSpinner');
const translatedOutput = document.getElementById('translatedOutput');
const backTranslatedOutput = document.getElementById('backTranslatedOutput');
const reviewOutput = document.getElementById('reviewOutput');
const translatedStatus = document.getElementById('translatedStatus');
const backTranslatedStatus = document.getElementById('backTranslatedStatus');
const reviewStatus = document.getElementById('reviewStatus');
const comparisonStatus = document.getElementById('comparisonStatus');
const originalText = document.getElementById('originalText');
const backTranslatedText = document.getElementById('backTranslatedText');
const MAX_INPUT_LENGTH = 1500;

/**
 * Updates the status indicator for a section
 * @param {HTMLElement} element - Status indicator element
 * @param {string} status - Status class name (pending, processing, complete, error)
 */
function updateStatus(element, status) {
    element.className = `status-indicator ${status}`;
}

/**
 * Parses Server-Sent Events (SSE) format
 * @param {string} text - Raw SSE text block
 * @returns {Object|null} Parsed event object with event type and data
 */
function parseSSE(text) {
    const lines = text.split('\n');
    let eventType = null;
    let eventData = null;

    for (const line of lines) {
        if (line.startsWith('event:')) {
            eventType = line.substring(6).trim();
        } else if (line.startsWith('data:')) {
            eventData = line.substring(5).trim();
        }
    }

    if (eventType && eventData) {
        try {
            return {
                event: eventType,
                data: JSON.parse(eventData)
            };
        } catch (e) {
            console.error('Failed to parse SSE data:', eventData, e);
            return null;
        }
    }
    return null;
}

/**
 * Handles the translation form submission
 */
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Get form values
    const text = document.getElementById('inputText').value;
    const source = document.getElementById('sourceLanguage').value || 'en';
    const target = document.getElementById('targetLanguage').value || 'af';
    const model = document.getElementById('model').value || 'qwen/qwen3-235b-a22b-2507';

    if (text.length > MAX_INPUT_LENGTH) {
        const errorMsg = `Input too long. Limit is ${MAX_INPUT_LENGTH} characters.`;
        translatedOutput.textContent = `Error: ${errorMsg}`;
        translatedOutput.className = 'result-content error';
        backTranslatedOutput.textContent = 'N/A';
        backTranslatedOutput.className = 'result-content empty';
        reviewOutput.textContent = 'N/A';
        reviewOutput.className = 'result-content empty';
        originalText.innerHTML = 'N/A';
        originalText.className = 'result-content empty';
        backTranslatedText.innerHTML = 'N/A';
        backTranslatedText.className = 'result-content empty';
        updateStatus(translatedStatus, 'error');
        updateStatus(backTranslatedStatus, 'error');
        updateStatus(reviewStatus, 'error');
        updateStatus(comparisonStatus, 'error');
        return;
    }

    // Show loading state
    translateBtn.disabled = true;
    buttonText.textContent = 'Translating...';
    loadingSpinner.classList.remove('hidden');

    // Scroll to results section
    const resultsSection = document.getElementById('results');
    resultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });

    // Reset status indicators
    updateStatus(translatedStatus, 'processing');
    updateStatus(backTranslatedStatus, 'pending');
    updateStatus(reviewStatus, 'pending');
    updateStatus(comparisonStatus, 'pending');

    // Clear previous results
    translatedOutput.textContent = 'Processing...';
    translatedOutput.className = 'result-content';
    backTranslatedOutput.textContent = 'Waiting for translation...';
    backTranslatedOutput.className = 'result-content empty';
    reviewOutput.textContent = 'Waiting for back-translation...';
    reviewOutput.className = 'result-content empty';
    originalText.innerHTML = 'Waiting for back-translation...';
    originalText.className = 'result-content empty';
    backTranslatedText.innerHTML = 'Waiting for back-translation...';
    backTranslatedText.className = 'result-content empty';

    try {
        const response = await fetch('/translate/stream', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text, source, target, model })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { done, value } = await reader.read();
            
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const eventBlocks = buffer.split('\n\n');
            
            // Keep the last incomplete event in buffer
            buffer = eventBlocks.pop() || '';

            for (const eventBlock of eventBlocks) {
                if (eventBlock.trim()) {
                    console.log('Raw event block:', eventBlock);
                    const event = parseSSE(eventBlock);
                    console.log('Parsed event:', event);
                    
                    if (event) {
                        if (event.event === 'translated' && event.data && event.data.translated) {
                            console.log('Updating translated text');
                            translatedOutput.textContent = event.data.translated;
                            translatedOutput.className = 'result-content';
                            updateStatus(translatedStatus, 'complete');
                            updateStatus(backTranslatedStatus, 'processing');
                            backTranslatedOutput.textContent = 'Processing...';
                            backTranslatedOutput.className = 'result-content';
                        } else if (event.event === 'back_translated' && event.data && event.data.back_translated) {
                            console.log('Updating back-translated text');
                            backTranslatedOutput.textContent = event.data.back_translated;
                            backTranslatedOutput.className = 'result-content';
                            updateStatus(backTranslatedStatus, 'complete');
                            updateStatus(reviewStatus, 'processing');
                            updateStatus(comparisonStatus, 'processing');
                            reviewOutput.textContent = 'Processing...';
                            reviewOutput.className = 'result-content';

                            // Create comparison with custom highlighting
                            const highlighted = highlightDifferences(text, event.data.back_translated);

                            originalText.innerHTML = highlighted.original || text;
                            originalText.className = 'result-content';
                            backTranslatedText.innerHTML = highlighted.backTranslated || event.data.back_translated;
                            backTranslatedText.className = 'result-content';
                            updateStatus(comparisonStatus, 'complete');
                        } else if (event.event === 'review' && event.data && event.data.review) {
                            console.log('Updating review text');
                            reviewOutput.textContent = event.data.review;
                            reviewOutput.className = 'result-content';
                            updateStatus(reviewStatus, 'complete');
                        } else if (event.event === 'error') {
                            const errorMsg = (event.data && event.data.error) || 'Unknown error';
                            translatedOutput.textContent = `Error: ${errorMsg}`;
                            translatedOutput.className = 'result-content error';
                            updateStatus(translatedStatus, 'error');
                            updateStatus(backTranslatedStatus, 'error');
                            updateStatus(reviewStatus, 'error');
                            updateStatus(comparisonStatus, 'error');
                            throw new Error(errorMsg);
                        } else if (event.event === 'complete') {
                            console.log('Translation complete');
                        }
                    }
                }
            }
        }

    } catch (error) {
        // Display error
        translatedOutput.textContent = `Error: ${error.message}`;
        translatedOutput.className = 'result-content error';
        backTranslatedOutput.textContent = 'N/A';
        backTranslatedOutput.className = 'result-content empty';
        reviewOutput.textContent = 'N/A';
        reviewOutput.className = 'result-content empty';
        originalText.innerHTML = 'N/A';
        originalText.className = 'result-content empty';
        backTranslatedText.innerHTML = 'N/A';
        backTranslatedText.className = 'result-content empty';
        updateStatus(translatedStatus, 'error');
        updateStatus(backTranslatedStatus, 'error');
        updateStatus(reviewStatus, 'error');
        updateStatus(comparisonStatus, 'error');
    } finally {
        // Reset button state
        translateBtn.disabled = false;
        buttonText.textContent = 'Translate';
        loadingSpinner.classList.add('hidden');
    }
});


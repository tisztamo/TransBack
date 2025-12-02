/**
 * Custom text comparison module for highlighting differences
 * between original and back-translated text
 */

/**
 * Escapes HTML special characters
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

/**
 * Compares two words character by character and returns HTML with highlighting
 * @param {string} word - The word to display
 * @param {string} otherWord - The word to compare against
 * @returns {string} HTML string with highlighted character differences
 */
function highlightCharacterDifferences(word, otherWord) {
    // First, count how many characters differ
    let diffCount = 0;
    const maxLen = Math.max(word.length, otherWord.length);
    
    for (let i = 0; i < word.length; i++) {
        const char = word[i];
        const otherChar = otherWord[i];
        
        if (char !== otherChar) {
            diffCount++;
        }
    }
    
    // If more than half the letters differ, accent the whole word
    if (diffCount > word.length / 2) {
        return `<span class="char-diff">${escapeHtml(word)}</span>`;
    }
    
    // Otherwise, highlight individual characters
    let result = '';
    for (let i = 0; i < word.length; i++) {
        const char = word[i];
        const otherChar = otherWord[i];
        
        if (char === otherChar) {
            // Characters match - no highlighting
            result += escapeHtml(char);
        } else {
            // Characters differ - highlight with strong color
            result += `<span class="char-diff">${escapeHtml(char)}</span>`;
        }
    }
    
    return result;
}

/**
 * Highlights differences in a text compared to another text
 * @param {string} textToDisplay - The text to display and highlight
 * @param {string} textToCompare - The text to compare against
 * @returns {string} HTML string with highlighted differences
 */
function highlightText(textToDisplay, textToCompare) {
    if (!textToDisplay) return '';
    if (!textToCompare) return escapeHtml(textToDisplay);
    
    // Split both texts into words
    const wordsToDisplay = textToDisplay.split(/(\s+)/); // Keep whitespace in array
    const wordsToCompare = textToCompare.split(/\s+/); // Just words for comparison
    
    let result = '';
    let wordIndex = 0; // Index for non-whitespace words
    
    for (let i = 0; i < wordsToDisplay.length; i++) {
        const part = wordsToDisplay[i];
        
        // Check if this part is whitespace
        if (/^\s+$/.test(part)) {
            result += part; // Keep whitespace as-is
            continue;
        }
        
        // This is a word - compare it
        const compareWord = wordsToCompare[wordIndex] || '';
        
        if (part.toLowerCase() === compareWord.toLowerCase()) {
            // Words are the same (case-insensitive) - no highlighting
            result += escapeHtml(part);
        } else {
            // Words differ - apply light background and highlight character differences
            const charHighlighted = highlightCharacterDifferences(part, compareWord);
            result += `<span class="word-diff">${charHighlighted}</span>`;
        }
        
        wordIndex++;
    }
    
    return result;
}

/**
 * Main function to highlight differences between original and back-translated text
 * @param {string} originalText - Original text
 * @param {string} backTranslatedText - Back-translated text
 * @returns {{original: string, backTranslated: string}} Object with highlighted HTML for both texts
 */
function highlightDifferences(originalText, backTranslatedText) {
    return {
        original: highlightText(originalText, backTranslatedText),
        backTranslated: highlightText(backTranslatedText, originalText)
    };
}


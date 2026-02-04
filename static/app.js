// Professional Podcast Generator - Frontend JavaScript

let currentAudioBlob = null;
let allVoices = {};

// Initialize app
document.addEventListener('DOMContentLoaded', () => {
    loadEmotions();
    loadVoices();
});

// Tab switching
function switchTab(tabName) {
    // Hide all tabs
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Show selected tab
    document.getElementById(`${tabName}-tab`).classList.add('active');
    event.target.classList.add('active');
}

// Generate podcast from topic
async function generatePodcast() {
    const topic = document.getElementById('topic').value.trim();
    const duration = parseInt(document.getElementById('duration').value);
    const tone = document.getElementById('tone').value;
    const language = document.getElementById('language').value;
    const keyPoints = document.getElementById('keyPoints').value
        .split(',')
        .map(p => p.trim())
        .filter(p => p);
    const hostVoice = document.getElementById('hostVoice').value;
    const guestVoice = document.getElementById('guestVoice').value;

    if (!topic) {
        showStatus('error', 'Please enter a podcast topic');
        return;
    }

    showStatus('loading', 'Generating your podcast... This may take a few minutes.');
    showLoading(true);

    try {
        const requestBody = {
            topic: topic,
            requirements: {
                duration_minutes: duration,
                tone: tone,
                key_points: keyPoints,
                language: language || 'en-US'
            }
        };

        // Add custom voices if selected
        if (hostVoice || guestVoice) {
            requestBody.voices = {};
            if (hostVoice) {
                requestBody.voices.HOST = hostVoice;
                requestBody.voices['CO-HOST'] = hostVoice;  // Use same voice for CO-HOST
            }
            if (guestVoice) {
                requestBody.voices.GUEST = guestVoice;
            }
        }

        const response = await fetch('/api/podcast/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(requestBody)
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Generation failed');
        }

        const blob = await response.blob();
        currentAudioBlob = blob;

        showResult(blob, `Podcast generated successfully! Topic: ${topic}`);

    } catch (error) {
        showStatus('error', `Failed to generate podcast: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Generate from custom script
async function generateFromScript() {
    const script = document.getElementById('customScript').value.trim();

    if (!script) {
        showStatus('error', 'Please enter a podcast script');
        return;
    }

    showStatus('loading', 'Generating podcast from your script...');
    showLoading(true);

    try {
        const response = await fetch('/api/podcast/from-script', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                script: script
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Generation failed');
        }

        const blob = await response.blob();
        currentAudioBlob = blob;

        showResult(blob, 'Podcast generated from your custom script!');

    } catch (error) {
        showStatus('error', `Failed to generate podcast: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Validate script
async function validateScript() {
    const script = document.getElementById('customScript').value.trim();

    if (!script) {
        showStatus('error', 'Please enter a script to validate');
        return;
    }

    try {
        const response = await fetch('/api/script/validate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                script: script
            })
        });

        const result = await response.json();

        if (result.success && result.valid) {
            const stats = result.statistics;
            displayScriptStats(stats);
            showStatus('success', 'Script is valid! ✓');
        } else {
            showStatus('error', result.error || 'Invalid script format');
        }

    } catch (error) {
        showStatus('error', `Validation failed: ${error.message}`);
    }
}

// Preview script (first 30 seconds)
async function previewScript() {
    const script = document.getElementById('customScript').value.trim();

    if (!script) {
        showStatus('error', 'Please enter a script to preview');
        return;
    }

    showStatus('loading', 'Generating preview (first 30 seconds)...');
    showLoading(true);

    try {
        const response = await fetch('/api/script/preview', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                script: script
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Preview failed');
        }

        const blob = await response.blob();
        showResult(blob, 'Preview generated (first segments only)');

    } catch (error) {
        showStatus('error', `Preview failed: ${error.message}`);
    } finally {
        showLoading(false);
    }
}

// Display script statistics
function displayScriptStats(stats) {
    const statsBox = document.getElementById('scriptStats');
    
    let speakersHTML = '';
    for (const [speaker, data] of Object.entries(stats.speakers)) {
        speakersHTML += `<p><strong>${speaker}:</strong> ${data.segments} segments, ${data.words} words</p>`;
    }

    let emotionsHTML = '';
    for (const [emotion, count] of Object.entries(stats.emotions)) {
        emotionsHTML += `<span style="margin-right: 10px;">${emotion} (${count})</span>`;
    }

    statsBox.innerHTML = `
        <h4>Script Statistics</h4>
        <p><strong>Total Segments:</strong> ${stats.total_segments}</p>
        <p><strong>Total Words:</strong> ${stats.total_words}</p>
        <p><strong>Estimated Duration:</strong> ${stats.estimated_duration_minutes.toFixed(1)} minutes</p>
        <h4 style="margin-top: 15px;">Speakers</h4>
        ${speakersHTML}
        <h4 style="margin-top: 15px;">Emotions Used</h4>
        <p>${emotionsHTML}</p>
    `;
    statsBox.style.display = 'block';
}

// Load available emotions
async function loadEmotions() {
    try {
        const response = await fetch('/api/emotions');
        const data = await response.json();

        if (data.success) {
            const emotionsContainer = document.getElementById('emotionsList');
            emotionsContainer.innerHTML = '';

            data.emotions.forEach(emotion => {
                const card = document.createElement('div');
                card.className = 'emotion-card';
                card.innerHTML = `
                    <h4>${emotion.name}</h4>
                    <p>${emotion.description}</p>
                    <div class="prosody">
                        Rate: ${emotion.prosody.rate} | 
                        Pitch: ${emotion.prosody.pitch} | 
                        Volume: ${emotion.prosody.volume}
                    </div>
                `;
                emotionsContainer.appendChild(card);
            });
        }
    } catch (error) {
        console.error('Failed to load emotions:', error);
    }
}

// Load available voices
async function loadVoices() {
    try {
        const response = await fetch('/api/voices');
        const data = await response.json();

        if (data.success) {
            allVoices = data.voices;
            displayVoices(allVoices);
            populateLocaleFilter(allVoices);
            populateVoiceSelectors(allVoices);
        }
    } catch (error) {
        console.error('Failed to load voices:', error);
        document.getElementById('voicesList').innerHTML = 
            '<div class="status-error">Failed to load voices. Please refresh the page.</div>';
    }
}

// Populate voice selector dropdowns
function populateVoiceSelectors(voices) {
    // Populate language selector
    const languageSelect = document.getElementById('language');
    languageSelect.innerHTML = '<option value="">✨ English (US) - Default</option>';
    
    const languageMap = {
        'en-US': 'English (United States)',
        'en-GB': 'English (United Kingdom)',
        'en-AU': 'English (Australia)',
        'en-IN': 'English (India)',
        'es-ES': 'Spanish (Spain)',
        'es-MX': 'Spanish (Mexico)',
        'fr-FR': 'French (France)',
        'de-DE': 'German (Germany)',
        'it-IT': 'Italian (Italy)',
        'pt-BR': 'Portuguese (Brazil)',
        'hi-IN': 'Hindi (India)',
        'zh-CN': 'Chinese (Mandarin, Simplified)',
        'ja-JP': 'Japanese (Japan)',
        'ko-KR': 'Korean (Korea)',
        'ar-SA': 'Arabic (Saudi Arabia)',
        'ru-RU': 'Russian (Russia)',
        'ta-IN': 'Tamil (India)',
        'te-IN': 'Telugu (India)',
        'ml-IN': 'Malayalam (India)',
        'bn-IN': 'Bengali (India)'
    };
    
    // Add popular languages first
    const sortedLocales = Object.keys(voices).sort((a, b) => {
        const priorityLocales = ['en-US', 'en-GB', 'es-ES', 'fr-FR', 'de-DE', 'hi-IN', 'zh-CN', 'ja-JP'];
        const aIndex = priorityLocales.indexOf(a);
        const bIndex = priorityLocales.indexOf(b);
        if (aIndex !== -1 && bIndex !== -1) return aIndex - bIndex;
        if (aIndex !== -1) return -1;
        if (bIndex !== -1) return 1;
        return a.localeCompare(b);
    });
    
    sortedLocales.forEach(locale => {
        const option = document.createElement('option');
        option.value = locale;
        option.textContent = languageMap[locale] || locale;
        languageSelect.appendChild(option);
    });
    
    // Initial voice dropdowns population
    updateVoiceDropdowns(voices, '');
}

// Filter and update voice dropdowns based on selected language
function filterVoicesByLanguage() {
    const selectedLanguage = document.getElementById('language').value;
    updateVoiceDropdowns(allVoices, selectedLanguage);
}

// Update voice dropdowns based on language filter
function updateVoiceDropdowns(voices, languageFilter) {
    const hostSelect = document.getElementById('hostVoice');
    const guestSelect = document.getElementById('guestVoice');
    
    // Clear existing options
    hostSelect.innerHTML = '<option value="">✨ Default (Jenny - Female, Cheerful)</option>';
    guestSelect.innerHTML = '<option value="">✨ Default (Guy - Male, Professional)</option>';
    
    // Filter voices by language if specified
    const filteredVoices = languageFilter 
        ? { [languageFilter]: voices[languageFilter] || [] }
        : voices;
    
    // Group voices by locale and add to dropdowns
    for (const [locale, voiceList] of Object.entries(filteredVoices)) {
        if (!voiceList || voiceList.length === 0) continue;
        
        const hostGroup = document.createElement('optgroup');
        hostGroup.label = locale;
        const guestGroup = document.createElement('optgroup');
        guestGroup.label = locale;
        
        voiceList.forEach(voice => {
            const hostOption = document.createElement('option');
            hostOption.value = voice.id;
            hostOption.textContent = `${voice.display_name} (${voice.gender})`;
            hostGroup.appendChild(hostOption);
            
            const guestOption = document.createElement('option');
            guestOption.value = voice.id;
            guestOption.textContent = `${voice.display_name} (${voice.gender})`;
            guestGroup.appendChild(guestOption);
        });
        
        hostSelect.appendChild(hostGroup);
        guestSelect.appendChild(guestGroup);
    }
}

// Display voices in grid
function displayVoices(voices) {
    const voicesContainer = document.getElementById('voicesList');
    voicesContainer.innerHTML = '';

    for (const [locale, voiceList] of Object.entries(voices)) {
        voiceList.forEach(voice => {
            const card = document.createElement('div');
            card.className = 'voice-card';
            card.onclick = () => playVoiceDemo(voice.id, card);
            
            card.innerHTML = `
                <div class="voice-info">
                    <span class="voice-name">${voice.display_name}</span>
                    <span class="voice-gender">${voice.gender}</span>
                </div>
                <div class="voice-locale">${locale}</div>
            `;
            
            voicesContainer.appendChild(card);
        });
    }
}

// Populate locale filter dropdown
function populateLocaleFilter(voices) {
    const filter = document.getElementById('localeFilter');
    filter.innerHTML = '<option value="">All Languages</option>';

    const locales = Object.keys(voices).sort();
    locales.forEach(locale => {
        const option = document.createElement('option');
        option.value = locale;
        option.textContent = locale;
        filter.appendChild(option);
    });
}

// Filter voices by locale
function filterVoices() {
    const selectedLocale = document.getElementById('localeFilter').value;

    if (!selectedLocale) {
        displayVoices(allVoices);
    } else {
        const filtered = {
            [selectedLocale]: allVoices[selectedLocale]
        };
        displayVoices(filtered);
    }
}

// Play voice demo
let currentAudio = null;
let currentPlayingCard = null;

async function playVoiceDemo(voiceId, cardElement) {
    try {
        // Stop current audio if playing
        if (currentAudio) {
            currentAudio.pause();
            if (currentPlayingCard) {
                currentPlayingCard.classList.remove('playing');
            }
        }

        // Show loading state
        cardElement.classList.add('playing');
        currentPlayingCard = cardElement;

        // Fetch demo audio
        const response = await fetch(`/api/voice/demo/${voiceId}`);
        
        if (!response.ok) {
            throw new Error('Failed to load demo');
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        // Play audio
        currentAudio = new Audio(url);
        currentAudio.play();

        // Remove playing state when finished
        currentAudio.onended = () => {
            cardElement.classList.remove('playing');
            URL.revokeObjectURL(url);
            currentPlayingCard = null;
        };

        // Handle errors
        currentAudio.onerror = () => {
            cardElement.classList.remove('playing');
            showStatus('error', 'Failed to play demo');
            currentPlayingCard = null;
        };

    } catch (error) {
        cardElement.classList.remove('playing');
        showStatus('error', `Demo failed: ${error.message}`);
        currentPlayingCard = null;
    }
}

// Show status message
function showStatus(type, message) {
    const statusSection = document.getElementById('statusSection');
    const statusTitle = document.getElementById('statusTitle');
    const statusMessage = document.getElementById('statusMessage');

    statusSection.style.display = 'block';
    
    if (type === 'loading') {
        statusTitle.textContent = 'Generating...';
        statusMessage.className = 'status-info';
    } else if (type === 'success') {
        statusTitle.textContent = 'Success';
        statusMessage.className = 'status-success';
    } else if (type === 'error') {
        statusTitle.textContent = 'Error';
        statusMessage.className = 'status-error';
    }

    statusMessage.textContent = message;

    // Hide result section when showing new status
    if (type !== 'result') {
        document.getElementById('resultSection').style.display = 'none';
    }

    // Auto-scroll to status
    statusSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Show/hide loading bar
function showLoading(show) {
    document.getElementById('loadingBar').style.display = show ? 'block' : 'none';
}

// Show result with audio player
function showResult(audioBlob, message) {
    const statusSection = document.getElementById('statusSection');
    const statusTitle = document.getElementById('statusTitle');
    const statusMessage = document.getElementById('statusMessage');
    const resultSection = document.getElementById('resultSection');
    const audioPlayer = document.getElementById('resultAudio');

    statusSection.style.display = 'block';
    statusTitle.textContent = 'Podcast Ready!';
    statusMessage.className = 'status-success';
    statusMessage.textContent = message;

    // Set audio source
    const url = URL.createObjectURL(audioBlob);
    audioPlayer.src = url;

    resultSection.style.display = 'block';

    // Auto-scroll to result
    statusSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Download audio
function downloadAudio() {
    if (!currentAudioBlob) {
        showStatus('error', 'No audio to download');
        return;
    }

    const url = URL.createObjectURL(currentAudioBlob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `podcast_${Date.now()}.mp3`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

// Clear result
function clearResult() {
    document.getElementById('statusSection').style.display = 'none';
    document.getElementById('resultSection').style.display = 'none';
    document.getElementById('resultAudio').src = '';
    currentAudioBlob = null;
}

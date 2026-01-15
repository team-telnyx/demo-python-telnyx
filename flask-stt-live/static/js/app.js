// Global variables
let socket;
let mediaRecorder;
let audioContext;
let audioStream;
let isRecording = false;
let startTime;
let durationInterval;
let wordCount = 0;
let transcriptText = '';

// Configuration
let config = {
    apiKey: '',
    engine: 'V2',
    language: 'en'
};

// DOM Elements
const apiKeyInput = document.getElementById('apiKey');
const toggleApiKeyBtn = document.getElementById('toggleApiKey');
const engineSelect = document.getElementById('engine');
const languageSelect = document.getElementById('language');
const saveConfigBtn = document.getElementById('saveConfig');
const recordBtn = document.getElementById('recordBtn');
const recordText = document.getElementById('recordText');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const transcriptionOutput = document.getElementById('transcriptionOutput');
const clearTranscriptBtn = document.getElementById('clearTranscript');
const saveTranscriptBtn = document.getElementById('saveTranscript');
const wordCountEl = document.getElementById('wordCount');
const durationEl = document.getElementById('duration');
const toast = document.getElementById('toast');

// Initialize Socket.IO
function initSocket() {
    socket = io();

    socket.on('connect', () => {
        console.log('Connected to server');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        updateStatus('disconnected');
    });

    socket.on('transcription_started', (data) => {
        console.log('Transcription started', data);
        updateStatus('connected');
        showToast('Connected to Telnyx STT', 'success');
    });

    socket.on('transcription', (data) => {
        console.log('Transcription received:', data);
        handleTranscription(data);
    });

    socket.on('transcription_stopped', (data) => {
        console.log('Transcription stopped', data);
        updateStatus('disconnected');
    });

    socket.on('error', (data) => {
        console.error('Error:', data);
        showToast(data.message, 'error');
        if (isRecording) {
            stopRecording();
        }
    });
}

// Load saved configuration from localStorage
function loadConfig() {
    const savedConfig = localStorage.getItem('telnyxSTTConfig');
    if (savedConfig) {
        config = JSON.parse(savedConfig);
        apiKeyInput.value = config.apiKey;
        engineSelect.value = config.engine;
        languageSelect.value = config.language;
        if (config.apiKey) {
            recordBtn.disabled = false;
        }
    }
}

// Save configuration
function saveConfig() {
    config.apiKey = apiKeyInput.value;
    config.engine = engineSelect.value;
    config.language = languageSelect.value;

    if (!config.apiKey) {
        showToast('Please enter your API key', 'error');
        return;
    }

    localStorage.setItem('telnyxSTTConfig', JSON.stringify(config));
    recordBtn.disabled = false;
    showToast('Configuration saved successfully', 'success');
}

// Toggle API key visibility
function toggleApiKey() {
    if (apiKeyInput.type === 'password') {
        apiKeyInput.type = 'text';
        toggleApiKeyBtn.textContent = 'Hide';
    } else {
        apiKeyInput.type = 'password';
        toggleApiKeyBtn.textContent = 'Show';
    }
}

// Update status indicator
function updateStatus(status) {
    if (status === 'connected') {
        statusIndicator.classList.add('connected');
        statusText.textContent = 'Connected';
    } else {
        statusIndicator.classList.remove('connected');
        statusText.textContent = 'Not Connected';
    }
}

// Start recording
async function startRecording() {
    try {
        // Request microphone access
        audioStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                echoCancellation: true,
                noiseSuppression: true
            }
        });

        // Create audio context
        audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: 16000
        });

        const source = audioContext.createMediaStreamSource(audioStream);
        const processor = audioContext.createScriptProcessor(4096, 1, 1);

        source.connect(processor);
        processor.connect(audioContext.destination);

        // Start transcription session
        socket.emit('start_transcription', {
            api_key: config.apiKey,
            engine: config.engine,
            language: config.language
        });

        // Process audio data
        processor.onaudioprocess = (e) => {
            if (!isRecording) return;

            const inputData = e.inputBuffer.getChannelData(0);

            // Convert Float32Array to Int16Array (PCM 16-bit)
            const pcmData = new Int16Array(inputData.length);
            for (let i = 0; i < inputData.length; i++) {
                const s = Math.max(-1, Math.min(1, inputData[i]));
                pcmData[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
            }

            // Convert to base64
            const buffer = pcmData.buffer;
            const base64 = arrayBufferToBase64(buffer);

            // Send to server
            socket.emit('audio_data', { audio: base64 });
        };

        isRecording = true;
        recordBtn.classList.add('recording');
        recordText.textContent = 'Stop Recording';

        // Start duration timer
        startTime = Date.now();
        durationInterval = setInterval(updateDuration, 1000);

        showToast('Recording started', 'success');

    } catch (error) {
        console.error('Error starting recording:', error);
        showToast('Failed to access microphone: ' + error.message, 'error');
    }
}

// Stop recording
function stopRecording() {
    isRecording = false;
    recordBtn.classList.remove('recording');
    recordText.textContent = 'Start Recording';

    // Stop audio stream
    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
    }

    // Close audio context
    if (audioContext) {
        audioContext.close();
    }

    // Stop transcription session
    socket.emit('stop_transcription');

    // Stop duration timer
    if (durationInterval) {
        clearInterval(durationInterval);
    }

    showToast('Recording stopped', 'success');
}

// Toggle recording
function toggleRecording() {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
}

// Handle transcription results
function handleTranscription(data) {
    // Remove placeholder if present
    const placeholder = transcriptionOutput.querySelector('.placeholder');
    if (placeholder) {
        placeholder.remove();
    }

    const isFinal = data.is_final || false;
    const text = data.transcript || data.text || '';

    if (!text) return;

    // Create transcription item
    const item = document.createElement('div');
    item.className = 'transcription-item' + (isFinal ? '' : ' interim');

    const timestamp = document.createElement('div');
    timestamp.className = 'timestamp';
    timestamp.textContent = new Date().toLocaleTimeString();

    const textDiv = document.createElement('div');
    textDiv.className = 'text';
    textDiv.textContent = text;

    item.appendChild(timestamp);
    item.appendChild(textDiv);

    if (isFinal) {
        transcriptionOutput.appendChild(item);
        transcriptText += text + ' ';
        updateWordCount();

        // Scroll to bottom
        transcriptionOutput.scrollTop = transcriptionOutput.scrollHeight;
    } else {
        // Update or create interim result
        let interimItem = transcriptionOutput.querySelector('.transcription-item.interim');
        if (interimItem) {
            interimItem.replaceWith(item);
        } else {
            transcriptionOutput.appendChild(item);
        }
    }
}

// Update word count
function updateWordCount() {
    const words = transcriptText.trim().split(/\s+/).filter(word => word.length > 0);
    wordCount = words.length;
    wordCountEl.textContent = wordCount;
}

// Update duration
function updateDuration() {
    const elapsed = Math.floor((Date.now() - startTime) / 1000);
    const minutes = Math.floor(elapsed / 60);
    const seconds = elapsed % 60;
    durationEl.textContent = `${String(minutes).padStart(2, '0')}:${String(seconds).padStart(2, '0')}`;
}

// Clear transcript
function clearTranscript() {
    transcriptionOutput.innerHTML = '<p class="placeholder">Your transcription will appear here...</p>';
    transcriptText = '';
    wordCount = 0;
    wordCountEl.textContent = '0';
    showToast('Transcript cleared', 'success');
}

// Save transcript
function saveTranscript() {
    if (!transcriptText.trim()) {
        showToast('No transcript to save', 'error');
        return;
    }

    const blob = new Blob([transcriptText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `transcript-${new Date().toISOString().slice(0, 10)}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('Transcript saved successfully', 'success');
}

// Show toast notification
function showToast(message, type = 'success') {
    toast.textContent = message;
    toast.className = 'toast ' + type + ' show';

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

// Convert ArrayBuffer to Base64
function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
}

// Event listeners
saveConfigBtn.addEventListener('click', saveConfig);
toggleApiKeyBtn.addEventListener('click', toggleApiKey);
recordBtn.addEventListener('click', toggleRecording);
clearTranscriptBtn.addEventListener('click', clearTranscript);
saveTranscriptBtn.addEventListener('click', saveTranscript);

// Initialize on page load
window.addEventListener('DOMContentLoaded', () => {
    initSocket();
    loadConfig();
});

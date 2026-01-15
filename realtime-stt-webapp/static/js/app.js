// Initialize Socket.IO connection
const socket = io();

// Global variables
let mediaRecorder = null;
let audioContext = null;
let audioStream = null;
let isRecording = false;
let transcripts = [];

// DOM elements
const startBtn = document.getElementById('start-btn');
const stopBtn = document.getElementById('stop-btn');
const saveBtn = document.getElementById('save-btn');
const apiKeyInput = document.getElementById('api-key');
const sttEngineSelect = document.getElementById('stt-engine');
const languageSelect = document.getElementById('language');
const statusPill = document.getElementById('status-pill');
const statusText = statusPill.querySelector('.status-text');
const transcriptContainer = document.getElementById('transcript-container');

// Event listeners
startBtn.addEventListener('click', startRecording);
stopBtn.addEventListener('click', stopRecording);
saveBtn.addEventListener('click', saveTranscript);

// Socket.IO event handlers
socket.on('connect', () => {
    console.log('Connected to server');
    updateStatus('Ready', false);
});

socket.on('disconnect', () => {
    console.log('Disconnected from server');
    updateStatus('Disconnected', false);
    if (isRecording) {
        stopRecording();
    }
});

socket.on('ready', (data) => {
    console.log('Server ready:', data.message);
});

socket.on('connected', (data) => {
    console.log('STT connected:', data.message);
    updateStatus('Recording', true);
});

socket.on('transcript', (data) => {
    console.log('Transcript received:', data);
    handleTranscript(data);
});

socket.on('stopped', (data) => {
    console.log('STT stopped:', data.message);
    updateStatus('Ready', false);
});

socket.on('error', (data) => {
    console.error('Error:', data.message);
    alert('Error: ' + data.message);
    updateStatus('Error', false);
    if (isRecording) {
        stopRecording();
    }
});

// Functions
async function startRecording() {
    const apiKey = apiKeyInput.value.trim();
    if (!apiKey) {
        alert('Please enter your Telnyx API key');
        apiKeyInput.focus();
        return;
    }

    try {
        // Request microphone access
        audioStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
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

        // Start STT session
        socket.emit('start_stt', {
            api_key: apiKey,
            engine: sttEngineSelect.value,
            language: languageSelect.value
        });

        // Process audio chunks
        processor.onaudioprocess = (event) => {
            if (isRecording) {
                const inputData = event.inputBuffer.getChannelData(0);
                const pcmData = convertFloat32ToInt16(inputData);
                const base64Audio = arrayBufferToBase64(pcmData.buffer);

                socket.emit('audio_data', { audio: base64Audio });
            }
        };

        isRecording = true;
        startBtn.disabled = true;
        stopBtn.disabled = false;
        apiKeyInput.disabled = true;
        sttEngineSelect.disabled = true;
        languageSelect.disabled = true;

        clearTranscripts();
        updateStatus('Connecting...', false);

    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Failed to access microphone: ' + error.message);
        updateStatus('Error', false);
    }
}

function stopRecording() {
    if (!isRecording) return;

    isRecording = false;

    // Stop audio stream
    if (audioStream) {
        audioStream.getTracks().forEach(track => track.stop());
        audioStream = null;
    }

    // Close audio context
    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }

    // Stop STT session
    socket.emit('stop_stt');

    startBtn.disabled = false;
    stopBtn.disabled = true;
    apiKeyInput.disabled = false;
    sttEngineSelect.disabled = false;
    languageSelect.disabled = false;

    updateStatus('Ready', false);
}

function handleTranscript(data) {
    // Check if transcript container has empty message
    const emptyMessage = transcriptContainer.querySelector('.transcript-empty');
    if (emptyMessage) {
        emptyMessage.remove();
    }

    const transcript = data.transcript || data.text || '';
    const isFinal = data.is_final || data.final || false;
    const confidence = data.confidence || null;

    if (!transcript) return;

    // Create transcript card
    const card = document.createElement('div');
    card.className = 'transcript-card' + (isFinal ? '' : ' interim');

    const header = document.createElement('div');
    header.className = 'transcript-header';

    const time = document.createElement('span');
    time.className = 'transcript-time';
    time.textContent = new Date().toLocaleTimeString();
    header.appendChild(time);

    if (confidence !== null) {
        const confidenceSpan = document.createElement('span');
        confidenceSpan.className = 'transcript-confidence';
        confidenceSpan.textContent = `Confidence: ${(confidence * 100).toFixed(0)}%`;
        header.appendChild(confidenceSpan);
    }

    const text = document.createElement('div');
    text.className = 'transcript-text';
    text.textContent = transcript;

    card.appendChild(header);
    card.appendChild(text);

    // Add to container
    transcriptContainer.appendChild(card);

    // Scroll to bottom
    transcriptContainer.scrollTop = transcriptContainer.scrollHeight;

    // Store transcript
    if (isFinal) {
        transcripts.push({
            timestamp: new Date().toISOString(),
            text: transcript,
            confidence: confidence
        });
    }
}

async function saveTranscript() {
    if (transcripts.length === 0) {
        alert('No transcript to save');
        return;
    }

    // Create formatted transcript
    let formattedTranscript = 'Patient Symptom Note\n';
    formattedTranscript += '='.repeat(50) + '\n';
    formattedTranscript += `Date: ${new Date().toLocaleDateString()}\n`;
    formattedTranscript += `Time: ${new Date().toLocaleTimeString()}\n`;
    formattedTranscript += `Language: ${languageSelect.options[languageSelect.selectedIndex].text}\n`;
    formattedTranscript += `STT Engine: ${sttEngineSelect.value}\n`;
    formattedTranscript += '='.repeat(50) + '\n\n';

    transcripts.forEach((item, index) => {
        const time = new Date(item.timestamp).toLocaleTimeString();
        formattedTranscript += `[${time}] ${item.text}\n\n`;
    });

    try {
        const response = await fetch('/save-transcript', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                transcript: formattedTranscript,
                filename: `patient_note_${new Date().toISOString().replace(/[:.]/g, '-')}.txt`
            })
        });

        const result = await response.json();

        if (result.success) {
            alert(`Transcript saved successfully to: ${result.filepath}`);
        } else {
            alert(`Failed to save transcript: ${result.error}`);
        }
    } catch (error) {
        console.error('Error saving transcript:', error);
        alert('Failed to save transcript');
    }
}

function updateStatus(text, recording) {
    statusText.textContent = text;
    if (recording) {
        statusPill.classList.add('recording');
    } else {
        statusPill.classList.remove('recording');
    }
}

function clearTranscripts() {
    transcripts = [];
    transcriptContainer.innerHTML = '';
}

function convertFloat32ToInt16(buffer) {
    const l = buffer.length;
    const int16Array = new Int16Array(l);
    for (let i = 0; i < l; i++) {
        const s = Math.max(-1, Math.min(1, buffer[i]));
        int16Array[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return int16Array;
}

function arrayBufferToBase64(buffer) {
    let binary = '';
    const bytes = new Uint8Array(buffer);
    const len = bytes.byteLength;
    for (let i = 0; i < len; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

// Load API key from localStorage if available
window.addEventListener('DOMContentLoaded', () => {
    const savedApiKey = localStorage.getItem('telnyx_api_key');
    if (savedApiKey) {
        apiKeyInput.value = savedApiKey;
    }

    // Save API key to localStorage when changed
    apiKeyInput.addEventListener('blur', () => {
        const apiKey = apiKeyInput.value.trim();
        if (apiKey) {
            localStorage.setItem('telnyx_api_key', apiKey);
        }
    });
});

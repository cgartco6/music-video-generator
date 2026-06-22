const API_URL = 'http://localhost:5000/api';
const WS_URL = 'ws://localhost:5000';

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const fileName = document.getElementById('fileName');
const fileSize = document.getElementById('fileSize');
const fileEmotion = document.getElementById('fileEmotion');
const removeFile = document.getElementById('removeFile');
const generateBtn = document.getElementById('generateBtn');
const progress = document.getElementById('progress');
const progressBar = document.getElementById('progressBar');
const progressText = document.getElementById('progressText');
const progressMessage = document.getElementById('progressMessage');
const videoSection = document.getElementById('videoSection');
const videoPlayer = document.getElementById('videoPlayer');
const videoSource = document.getElementById('videoSource');
const videoInfo = document.getElementById('videoInfo');
const downloadBtn = document.getElementById('downloadBtn');
const shareBtn = document.getElementById('shareBtn');
const regenerateBtn = document.getElementById('regenerateBtn');

// State
let uploadedFile = null;
let fileId = null;
let jobId = null;
let videoUrl = null;
let socket = null;
let isProcessing = false;

// Initialize WebSocket
function initWebSocket() {
    socket = io(WS_URL);
    
    socket.on('connect', () => {
        console.log('WebSocket connected');
    });
    
    socket.on('progress_update', (data) => {
        if (data.job_id === jobId) {
            updateProgress(data.progress, data.message);
        }
    });
    
    socket.on('job_complete', (data) => {
        if (data.job_id === jobId) {
            videoUrl = data.video_url;
            displayVideo(videoUrl);
            isProcessing = false;
            generateBtn.disabled = false;
        }
    });
    
    socket.on('job_error', (data) => {
        if (data.job_id === jobId) {
            alert('Error generating video: ' + data.error);
            isProcessing = false;
            generateBtn.disabled = false;
            progress.style.display = 'none';
        }
    });
}

// Event Listeners
dropZone.addEventListener('click', () => fileInput.click());
dropZone.addEventListener('dragover', handleDragOver);
dropZone.addEventListener('dragleave', handleDragLeave);
dropZone.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
removeFile.addEventListener('click', removeFileHandler);
generateBtn.addEventListener('click', generateVideo);
downloadBtn.addEventListener('click', downloadVideo);
shareBtn.addEventListener('click', shareVideo);
regenerateBtn.addEventListener('click', regenerateVideo);

// Character selection
document.querySelectorAll('.character-card input[type="checkbox"]').forEach(checkbox => {
    checkbox.addEventListener('change', updateGenerateButton);
});

function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

function handleFileSelect(e) {
    if (fileInput.files.length > 0) {
        handleFile(fileInput.files[0]);
    }
}

async function handleFile(file) {
    // Check if audio file
    const validTypes = ['audio/mpeg', 'audio/wav', 'audio/flac', 'audio/x-m4a', 'audio/mp4'];
    if (!validTypes.includes(file.type) && !file.name.match(/\.(mp3|wav|flac|m4a)$/i)) {
        alert('Please upload a valid audio file (MP3, WAV, FLAC, M4A)');
        return;
    }

    // Check file size
    if (file.size > 50 * 1024 * 1024) {
        alert('File size exceeds 50MB limit');
        return;
    }

    uploadedFile = file;
    fileName.textContent = file.name;
    fileSize.textContent = formatFileSize(file.size);
    fileInfo.style.display = 'flex';
    generateBtn.disabled = true;
    updateGenerateButton();

    // Upload file
    await uploadFile(file);
}

async function uploadFile(file) {
    const formData = new FormData();
    formData.append('audio', file);

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Upload failed');
        }

        const data = await response.json();
        fileId = data.file_id;
        
        // Display emotion if detected
        if (data.emotion) {
            fileEmotion.textContent = `🎵 ${data.emotion} (${Math.round(data.emotion_intensity * 100)}%)`;
            fileEmotion.style.display = 'inline-block';
        }
        
        generateBtn.disabled = false;
        console.log('Upload successful:', data);
    } catch (error) {
        console.error('Upload error:', error);
        alert('Failed to upload file: ' + error.message);
        removeFileHandler();
    }
}

function removeFileHandler() {
    uploadedFile = null;
    fileId = null;
    fileInfo.style.display = 'none';
    fileEmotion.style.display = 'none';
    generateBtn.disabled = true;
    videoSection.style.display = 'none';
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function updateGenerateButton() {
    const selected = document.querySelectorAll('.character-card input:checked').length;
    generateBtn.textContent = selected > 0 
        ? `🎬 Generate Music Video (${selected} characters)`
        : '🎬 Generate Music Video';
}

async function generateVideo() {
    if (!fileId) {
        alert('Please upload an audio file first');
        return;
    }

    if (isProcessing) {
        return;
    }

    // Get selected characters
    const selectedCharacters = [];
    document.querySelectorAll('.character-card input:checked').forEach(checkbox => {
        selectedCharacters.push(checkbox.closest('.character-card').dataset.type);
    });

    if (selectedCharacters.length === 0) {
        alert('Please select at least one character');
        return;
    }

    // Get customization options
    const hairstyle = document.getElementById('hairstyle').value;
    const outfit = document.getElementById('outfit').value;
    const ethnicity = document.getElementById('ethnicity').value;
    const genre = document.getElementById('genre').value;
    const colorStyle = document.getElementById('colorStyle').value;
    const enableStyleTransfer = document.getElementById('enableStyleTransfer').checked;
    const enableColorGrading = document.getElementById('enableColorGrading').checked;
    const enableFaceEnhancement = document.getElementById('enableFaceEnhancement').checked;
    const enableEmotionDriven = document.getElementById('enableEmotionDriven').checked;

    // Show progress
    isProcessing = true;
    generateBtn.disabled = true;
    progress.style.display = 'block';
    progressBar.style.width = '0%';
    progressText.textContent = '0%';
    progressMessage.textContent = 'Initializing...';
    videoSection.style.display = 'none';

    try {
        const response = await fetch(`${API_URL}/process`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                file_id: fileId,
                characters: {
                    types: selectedCharacters,
                    hairstyle: hairstyle,
                    outfit: outfit,
                    ethnicity: ethnicity
                },
                enhancements: {
                    style_transfer: enableStyleTransfer,
                    genre: genre,
                    color_grading: enableColorGrading,
                    color_style: colorStyle,
                    face_enhancement: enableFaceEnhancement,
                    emotion_driven: enableEmotionDriven
                }
            })
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Generation failed');
        }

        const data = await response.json();
        jobId = data.job_id;

        // Progress updates will come through WebSocket
        // Wait for completion (WebSocket will handle it)
        
        // Fallback polling in case WebSocket fails
        let attempts = 0;
        const maxAttempts = 300; // 5 minutes
        const pollInterval = setInterval(async () => {
            attempts++;
            try {
                const statusResponse = await fetch(`${API_URL}/status/${jobId}`);
                const statusData = await statusResponse.json();
                
                if (statusData.status === 'complete') {
                    clearInterval(pollInterval);
                    videoUrl = statusData.output_file ? `/api/download/${statusData.output_file}` : null;
                    if (videoUrl) {
                        displayVideo(videoUrl);
                    }
                    isProcessing = false;
                    generateBtn.disabled = false;
                } else if (statusData.status === 'error') {
                    clearInterval(pollInterval);
                    alert('Error generating video: ' + statusData.error);
                    isProcessing = false;
                    generateBtn.disabled = false;
                    progress.style.display = 'none';
                }
            } catch (error) {
                console.error('Status check error:', error);
            }
            
            if (attempts >= maxAttempts) {
                clearInterval(pollInterval);
                alert('Video generation timed out. Please try again.');
                isProcessing = false;
                generateBtn.disabled = false;
                progress.style.display = 'none';
            }
        }, 1000);

    } catch (error) {
        console.error('Generation error:', error);
        alert('Failed to generate video: ' + error.message);
        isProcessing = false;
        generateBtn.disabled = false;
        progress.style.display = 'none';
    }
}

function updateProgress(value, message) {
    const rounded = Math.min(100, Math.round(value));
    progressBar.style.width = rounded + '%';
    progressText.textContent = rounded + '%';
    if (message) {
        progressMessage.textContent = message;
    }
}

function displayVideo(url) {
    const fullUrl = `${API_URL}${url}`;
    videoSource.src = fullUrl;
    videoPlayer.load();
    videoSection.style.display = 'block';
    
    // Show video info
    videoInfo.innerHTML = `
        <span>🎬 Video ready</span>
        <span>📊 ${document.querySelectorAll('.character-card input:checked').length} characters</span>
        <span>🎵 ${document.getElementById('genre').value} style</span>
    `;
    
    // Scroll to video
    videoSection.scrollIntoView({ behavior: 'smooth' });
    
    // Auto-play
    videoPlayer.play().catch(e => console.log('Auto-play prevented'));
}

function downloadVideo() {
    if (videoUrl) {
        const a = document.createElement('a');
        a.href = `${API_URL}${videoUrl}`;
        a.download = 'music_video.mp4';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }
}

async function shareVideo() {
    if (videoUrl) {
        try {
            const response = await fetch(`${API_URL}${videoUrl}`);
            const blob = await response.blob();
            const file = new File([blob], 'music_video.mp4', { type: 'video/mp4' });
            
            if (navigator.share) {
                await navigator.share({
                    title: 'My AI Music Video',
                    files: [file]
                });
            } else {
                // Fallback: copy URL to clipboard
                const fullUrl = window.location.origin + videoUrl;
                await navigator.clipboard.writeText(fullUrl);
                alert('Video URL copied to clipboard!');
            }
        } catch (error) {
            console.error('Share error:', error);
            alert('Failed to share video: ' + error.message);
        }
    }
}

function regenerateVideo() {
    videoSection.style.display = 'none';
    generateVideo();
}

// Initialize WebSocket
initWebSocket();

// Check for audio file support
if (!HTMLMediaElement.prototype.canPlayType) {
    console.warn('Audio file detection may be limited');
}

console.log('🎵 AI Music Video Creator Pro loaded successfully!');
console.log('📁 Supported formats: MP3, WAV, FLAC, M4A');
console.log('🎨 Features: Face generation, Lip sync, Style transfer, Color grading, Emotion-driven scenes');

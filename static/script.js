const socket = io();

// DOM Elements
const promptInput = document.getElementById('promptInput');
const generateBtn = document.getElementById('generateBtn');
const progressSection = document.getElementById('progressSection');
const downloadSection = document.getElementById('downloadSection');
const progressTitle = document.getElementById('progressTitle');
const progressPercentage = document.getElementById('progressPercentage');
const progressFill = document.getElementById('progressFill');
const randomFactElement = document.getElementById('randomFact');
const downloadBtn = document.getElementById('downloadBtn');
const createAnotherBtn = document.getElementById('createAnotherBtn');

let currentVideoFile = null;
let factInterval = null;

// Generate video function
generateBtn.addEventListener('click', generateVideo);
promptInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        generateVideo();
    }
});

function generateVideo() {
    const topic = promptInput.value.trim();
    
    if (!topic) {
        showNotification('Please enter a video topic!', 'error');
        return;
    }
    
    if (topic.length < 3) {
        showNotification('Please enter a more descriptive topic!', 'error');
        return;
    }
    
    // Hide hero section and show progress
    document.querySelector('.hero').style.display = 'none';
    progressSection.style.display = 'block';
    downloadSection.style.display = 'none';
    
    // Reset progress
    resetProgress();
    
    // Start random facts
    startRandomFacts();
    
    // Emit generate video event
    socket.emit('generate_video', { topic: topic });
    
    // Disable input
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<div class="loading"></div> Generating...';
}

function resetProgress() {
    progressFill.style.width = '0%';
    progressPercentage.textContent = '0%';
    progressTitle.textContent = 'Initializing AI Video Generator...';
    
    // Reset all steps
    document.querySelectorAll('.step').forEach(step => {
        step.classList.remove('active', 'completed');
    });
}

function startRandomFacts() {
    // Get initial fact
    socket.emit('get_random_fact');
    
    // Make sure the facts section is visible
    document.getElementById('randomFact').style.display = 'flex';
    
    // Update fact every 2 minutes (120000 milliseconds)
    factInterval = setInterval(() => {
        socket.emit('get_random_fact');
    }, 120000);
}

socket.on('random_fact', (data) => {
    randomFactElement.innerHTML = `<i class="fas fa-lightbulb"></i><span>Did you know? ${data.fact}</span>`;
    randomFactElement.style.display = 'flex'; // Ensure visibility
});

function stopRandomFacts() {
    if (factInterval) {
        clearInterval(factInterval);
        factInterval = null;
    }
}

// Socket event listeners
socket.on('progress', (data) => {
    updateProgress(data.percentage, data.message);
    updateProgressSteps(data.step);
    
    // When video is fully generated (100%), prepare to show download section
    if (data.percentage === 100 && data.message.includes('complete')) {
        setTimeout(() => {
            progressTitle.textContent = 'Video Is Now Ready! 🔥';
            progressPercentage.textContent = '100%';
            progressPercentage.classList.add('completed');
            progressFill.classList.add('completed');
            
            // Mark all steps as completed
            document.querySelectorAll('.step').forEach(step => {
                step.classList.remove('active');
                step.classList.add('completed');
                step.querySelector('.step-icon i').className = 'fas fa-check';
            });
        }, 1000);
    }
});

socket.on('video_found', (data) => {
    stopRandomFacts();
    currentVideoFile = data.filename;
    
    // Update UI for found video
    setTimeout(() => {
        progressSection.style.display = 'none';
        downloadSection.style.display = 'block';
        
        // Update download section message for existing video
        const successMsg = downloadSection.querySelector('h2');
        const descMsg = downloadSection.querySelector('p');
        const downloadButton = downloadSection.querySelector('#downloadBtn');
        
        successMsg.textContent = 'Video Already Available! 🚀';
        descMsg.textContent = `Found existing video: "${data.original_topic}" with ${Math.round(data.similarity * 100)}% similarity to your request.`;
        downloadButton.innerHTML = '<i class="fas fa-download"></i> Download Again';
    }, 1000);
    
    // Re-enable generate button
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<i class="fas fa-play"></i> Generate Video';
});

socket.on('video_complete', (data) => {
    stopRandomFacts();
    currentVideoFile = data.filename;
    
    console.log("Video complete event received:", data); // Debug log
    
    // Ensure the progress shows 100% before transitioning
    updateProgress(100, 'Video generation complete!');
    
    // Show download section after brief delay
    setTimeout(() => {
        progressSection.style.display = 'none';
        downloadSection.style.display = 'block';
        
        // Reset download section message for new video
        const successMsg = downloadSection.querySelector('h2');
        const descMsg = downloadSection.querySelector('p');
        const downloadButton = downloadSection.querySelector('#downloadBtn');
        
        successMsg.textContent = 'Your Video is Ready! 🎉';
        descMsg.textContent = 'Your AI-generated video has been created successfully.';
        downloadButton.innerHTML = '<i class="fas fa-download"></i> Download Video';
        downloadButton.disabled = false;
    }, 2000);
    
    // Re-enable generate button
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<i class="fas fa-play"></i> Generate Video';
});

socket.on('error', (data) => {
    stopRandomFacts();
    showNotification(data.message, 'error');
    
    // Reset UI
    progressSection.style.display = 'none';
    document.querySelector('.hero').style.display = 'flex';
    
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<i class="fas fa-play"></i> Generate Video';
});

function updateProgress(percentage, message) {
    // Update progress fill width with animation
    progressFill.style.width = percentage + '%';
    progressPercentage.textContent = percentage + '%';
    progressTitle.textContent = message;
    
    // Add the completed class if at 100%
    if (percentage >= 100) {
        progressFill.classList.add('completed');
        progressPercentage.classList.add('completed');
        progressTitle.classList.add('completed');
    } else {
        progressFill.classList.remove('completed');
        progressPercentage.classList.remove('completed');
        progressTitle.classList.remove('completed');
    }
}

function updateProgressSteps(currentStep) {
    document.querySelectorAll('.step').forEach((step, index) => {
        const stepNumber = index + 1;
        step.classList.remove('active', 'completed');
        
        if (stepNumber < currentStep) {
            step.classList.add('completed');
            step.querySelector('.step-icon i').className = 'fas fa-check';
        } else if (stepNumber === currentStep) {
            step.classList.add('active');
        }
    });
}

// Enhanced download functionality with progress tracking
downloadBtn.addEventListener('click', async () => {
    if (currentVideoFile) {
        try {
            // Show download starting
            downloadBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Preparing Download...';
            downloadBtn.disabled = true;
            
            // Check if file exists first
            const checkResponse = await fetch(`/download/${currentVideoFile}`, { method: 'HEAD' });
            
            if (!checkResponse.ok) {
                throw new Error('Video file not found on server');
            }
            
            // Start actual download
            downloadBtn.innerHTML = '<i class="fas fa-download"></i> Downloading...';
            
            // Create download link
            const downloadUrl = `/download/${currentVideoFile}`;
            const link = document.createElement('a');
            link.href = downloadUrl;
            link.download = currentVideoFile;
            link.style.display = 'none';
            
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            showNotification('Download started successfully!', 'success');
            
            // Reset button after download starts
            setTimeout(() => {
                downloadBtn.innerHTML = '<i class="fas fa-check"></i> Downloaded';
                downloadBtn.style.background = '#22C55E';
                
                // Reset to original state after a few seconds
                setTimeout(() => {
                    downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Again';
                    downloadBtn.style.background = '';
                    downloadBtn.disabled = false;
                }, 2000);
            }, 1000);
            
        } catch (error) {
            console.error('Download failed:', error);
            showNotification(`Download failed: ${error.message}`, 'error');
            
            // Reset button on error
            downloadBtn.innerHTML = '<i class="fas fa-download"></i> Download Video';
            downloadBtn.disabled = false;
        }
    } else {
        showNotification('No video file available for download!', 'error');
    }
});

createAnotherBtn.addEventListener('click', () => {
    downloadSection.style.display = 'none';
    document.querySelector('.hero').style.display = 'flex';
    promptInput.value = '';
    promptInput.focus();
});

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <i class="fas fa-${type === 'error' ? 'exclamation-circle' : type === 'success' ? 'check-circle' : 'info-circle'}"></i>
        <span>${message}</span>
    `;
    
    // Add notification styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${type === 'error' ? '#EF4444' : type === 'success' ? '#22C55E' : '#8B5CF6'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        z-index: 10000;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transform: translateX(100%);
        transition: transform 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
    }, 100);
    
    // Remove after 4 seconds
    setTimeout(() => {
        notification.style.transform = 'translateX(100%)';
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 4000);
}

// Auto-resize input
promptInput.addEventListener('input', () => {
    const maxLength = promptInput.getAttribute('maxlength');
    const currentLength = promptInput.value.length;
    
    if (currentLength >= maxLength * 0.9) {
        showNotification(`Character limit: ${currentLength}/${maxLength}`, 'info');
    }
});

// Add enter key animation
promptInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
        generateBtn.style.transform = 'scale(0.95)';
        setTimeout(() => {
            generateBtn.style.transform = '';
        }, 150);
    }
});
        setTimeout(() => {
            notification.remove();
        }, 300);

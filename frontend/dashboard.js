// ==================== ENHANCED KISANSAHAYAK AI DASHBOARD JAVASCRIPT ====================

// Configuration
const API_BASE = 'http://localhost:8000';

// Global State
let dashboardState = {
    currentUser: null,
    crops: [],
    notifications: [],
    chatMessages: [],
    isOnline: navigator.onLine
};

// ==================== INITIALIZATION ====================
document.addEventListener('DOMContentLoaded', function() {
    console.log('🌱 KisanSahayak AI Dashboard Loading...');
    initializeDashboard();
    setupEventListeners();
    loadInitialData();
    console.log('✅ Dashboard loaded successfully!');
});

function initializeDashboard() {
    initializeSidebar();
    initializeChat();
    setupConnectionMonitoring();
    
    // Show welcome message
    setTimeout(() => {
        showNotification('🌾 Welcome to KisanSahayak AI Dashboard!', 'success');
        addChatMessage('🌱 Hello! I\'m your AI farming assistant. How can I help you today?', 'ai');
    }, 1000);
}

// ==================== SEARCH FUNCTIONALITY ====================
async function searchCrops() {
    const query = document.getElementById('crop-search-input').value.trim();
    if (!query) {
        showNotification('Please enter a search term', 'warning');
        return;
    }
    
    showLoading('Searching crops...');
    
    try {
        const response = await fetch(`${API_BASE}/search-crops`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ query })
        });
        
        const data = await response.json();
        displaySearchResults(data);
        
    } catch (error) {
        showNotification(`Search error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function displaySearchResults(data) {
    const panel = document.getElementById('search-results-panel');
    const content = document.getElementById('search-results-content');
    
    if (data.results.length === 0) {
        content.innerHTML = `
            <div class="no-results">
                <i class="fas fa-search"></i>
                <h4>No crops found for "${data.query}"</h4>
                <p>Try searching for rice, wheat, cotton, tea, etc.</p>
            </div>
        `;
    } else {
        content.innerHTML = `
            <div class="search-summary">
                <p>Found <strong>${data.total_found}</strong> crops for "<em>${data.query}</em>"</p>
            </div>
            <div class="crop-results">
                ${data.results.map(crop => `
                    <div class="crop-card" onclick="showCropDetails(${crop.id})">
                        <img src="${crop.image}" alt="${crop.name}" class="crop-image">
                        <div class="crop-info">
                            <h4>${crop.name}</h4>
                            <p class="crop-type">${crop.type} • ${crop.category}</p>
                            <p class="crop-description">${crop.description}</p>
                            <div class="crop-states">
                                <i class="fas fa-map-marker-alt"></i>
                                ${crop.major_states.join(', ')}
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
    }
    
    panel.style.display = 'block';
}

function closeSearchPanel() {
    document.getElementById('search-results-panel').style.display = 'none';
}

// ==================== WEATHER FUNCTIONALITY ====================
async function getWeatherConditions() {
    const location = prompt('Enter your location:', 'Delhi') || 'Delhi';
    
    showLoading('Getting weather conditions...');
    
    try {
        const response = await fetch(`${API_BASE}/weather-conditions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ location })
        });
        
        const data = await response.json();
        displayWeatherConditions(data);
        
    } catch (error) {
        showNotification(`Weather error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function displayWeatherConditions(data) {
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    
    modalTitle.innerHTML = `<i class="fas fa-cloud-sun"></i> Weather Conditions - ${data.location}`;
    
    if (data.error) {
        modalBody.innerHTML = `
            <div class="weather-error">
                <i class="fas fa-exclamation-triangle"></i>
                <h4>Weather data unavailable</h4>
                <p>${data.error}</p>
                <p>${data.fallback_advice}</p>
            </div>
        `;
    } else {
        modalBody.innerHTML = `
            <div class="weather-conditions">
                <div class="current-weather">
                    <h4><i class="fas fa-thermometer-half"></i> Current Weather</h4>
                    <div class="weather-grid">
                        <div class="weather-item">
                            <span class="weather-value">${data.current_weather.temperature}°C</span>
                            <span class="weather-label">Temperature</span>
                        </div>
                        <div class="weather-item">
                            <span class="weather-value">${data.current_weather.humidity}%</span>
                            <span class="weather-label">Humidity</span>
                        </div>
                        <div class="weather-item">
                            <span class="weather-value">${data.current_weather.wind_speed} m/s</span>
                            <span class="weather-label">Wind Speed</span>
                        </div>
                        <div class="weather-item">
                            <span class="weather-value">${data.current_weather.description}</span>
                            <span class="weather-label">Condition</span>
                        </div>
                    </div>
                </div>
                
                <div class="farming-advice">
                    <h4><i class="fas fa-lightbulb"></i> Farming Advice</h4>
                    ${data.farming_advice.length > 0 
                        ? data.farming_advice.map(advice => `<p>${advice}</p>`).join('')
                        : '<p>Current weather conditions are suitable for farming activities.</p>'
                    }
                </div>
                
                ${data.suitable_crops.length > 0 ? `
                    <div class="suitable-crops">
                        <h4><i class="fas fa-seedling"></i> Suitable Crops</h4>
                        <div class="crop-tags">
                            ${data.suitable_crops.map(crop => `<span class="crop-tag">${crop}</span>`).join('')}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }
    
    document.getElementById('analysis-modal').style.display = 'block';
}

// ==================== IMAGE ANALYSIS ====================
function triggerImageUpload() {
    document.getElementById('hidden-image-input').click();
}

async function analyzeImage() {
    const fileInput = document.getElementById('hidden-image-input');
    if (!fileInput.files[0]) return;
    
    showLoading('Analyzing crop image...');
    
    const formData = new FormData();
    formData.append('image', fileInput.files[0]);
    
    try {
        const response = await fetch(`${API_BASE}/analyze-crop-image`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        displayImageAnalysis(data);
        
    } catch (error) {
        showNotification(`Image analysis error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function displayImageAnalysis(data) {
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    
    modalTitle.innerHTML = `<i class="fas fa-camera"></i> Crop Image Analysis`;
    modalBody.innerHTML = `
        <div class="image-analysis">
            <div class="analysis-result">
                <h4><i class="fas fa-leaf"></i> Crop Detected</h4>
                <p class="detected-crop">${data.crop_detected}</p>
            </div>
            
            <div class="analysis-result">
                <h4><i class="fas fa-bug"></i> Pest Analysis</h4>
                <p>${data.pest_analysis}</p>
            </div>
            
            <div class="analysis-result">
                <h4><i class="fas fa-prescription"></i> Recommendations</h4>
                <p>${data.recommendations}</p>
            </div>
            
            <div class="analysis-confidence">
                <h4><i class="fas fa-chart-bar"></i> Analysis Confidence</h4>
                <div class="confidence-bar">
                    <div class="confidence-level ${data.confidence.toLowerCase()}">${data.confidence}</div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('analysis-modal').style.display = 'block';
}

// ==================== VOICE RECOGNITION ====================
function triggerVoiceRecognition() {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
        startBrowserVoiceRecognition();
    } else {
        document.getElementById('hidden-audio-input').click();
    }
}

function startBrowserVoiceRecognition() {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'hi-IN';
    
    showLoading('Listening... Speak your farming question');
    
    recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        processVoiceInput(transcript);
    };
    
    recognition.onerror = function(event) {
        hideLoading();
        showNotification('Voice recognition failed. Please try again.', 'error');
    };
    
    recognition.onend = function() {
        hideLoading();
    };
    
    recognition.start();
}

async function processVoiceFile() {
    const fileInput = document.getElementById('hidden-audio-input');
    if (!fileInput.files[0]) return;
    
    showLoading('Processing voice recording...');
    
    const formData = new FormData();
    formData.append('audio', fileInput.files[0]);
    
    try {
        const response = await fetch(`${API_BASE}/voice-recognition`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        displayVoiceResults(data);
        
    } catch (error) {
        showNotification(`Voice processing error: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

async function processVoiceInput(transcript) {
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: transcript })
        });
        
        const data = await response.json();
        
        displayVoiceResults({
            transcription: transcript,
            farming_response: data.response,
            suggested_crops: [],
            status: 'success'
        });
        
    } catch (error) {
        showNotification(`Voice processing error: ${error.message}`, 'error');
    }
}

function displayVoiceResults(data) {
    const modalTitle = document.getElementById('modal-title');
    const modalBody = document.getElementById('modal-body');
    
    modalTitle.innerHTML = `<i class="fas fa-microphone"></i> Voice Recognition Results`;
    modalBody.innerHTML = `
        <div class="voice-results">
            <div class="transcription">
                <h4><i class="fas fa-quote-left"></i> What you said:</h4>
                <p class="transcript">"${data.transcription}"</p>
            </div>
            
            <div class="ai-response">
                <h4><i class="fas fa-robot"></i> AI Response:</h4>
                <p>${data.farming_response}</p>
            </div>
        </div>
    `;
    
    document.getElementById('analysis-modal').style.display = 'block';
    
    // Add to chat
    addChatMessage(data.transcription, 'user');
    addChatMessage(data.farming_response, 'ai');
}

// ==================== CHAT FUNCTIONALITY ====================
async function sendChatMessage() {
    const input = document.getElementById('chat-input');
    const message = input.value.trim();
    
    if (!message) return;
    
    input.value = '';
    addChatMessage(message, 'user');
    
    try {
        const response = await fetch(`${API_BASE}/chat`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });
        
        const data = await response.json();
        addChatMessage(data.response, 'ai');
        
    } catch (error) {
        addChatMessage('Sorry, I encountered an error. Please try again.', 'ai');
        console.error('Chat error:', error);
    }
}

function addChatMessage(message, sender) {
    const chatContainer = document.getElementById('chat-container');
    const messageElement = document.createElement('div');
    messageElement.className = `chat-message ${sender}`;
    messageElement.innerHTML = `<p>${message}</p>`;
    
    messageElement.style.opacity = '0';
    messageElement.style.transform = 'translateY(20px)';
    
    chatContainer.appendChild(messageElement);
    
    requestAnimationFrame(() => {
        messageElement.style.transition = 'all 0.3s ease';
        messageElement.style.opacity = '1';
        messageElement.style.transform = 'translateY(0)';
    });
    
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

// ==================== UTILITY FUNCTIONS ====================
function showLoading(message = 'Loading...') {
    const overlay = document.getElementById('loading-overlay');
    overlay.querySelector('p').textContent = message;
    overlay.style.display = 'flex';
}

function hideLoading() {
    document.getElementById('loading-overlay').style.display = 'none';
}

function showNotification(message, type = 'info') {
    // Simple notification implementation
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 1rem;
        border-radius: 8px;
        z-index: 5000;
        animation: slideIn 0.3s ease;
    `;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

function closeAnalysisModal() {
    document.getElementById('analysis-modal').style.display = 'none';
}

// ==================== EVENT LISTENERS ====================
function setupEventListeners() {
    // Search on Enter key
    const searchInput = document.getElementById('crop-search-input');
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                searchCrops();
            }
        });
    }
    
    // Chat on Enter key
    const chatInput = document.getElementById('chat-input');
    if (chatInput) {
        chatInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendChatMessage();
            }
        });
    }
    
    // Close modals when clicking outside
    window.onclick = function(event) {
        const modal = document.getElementById('analysis-modal');
        const panel = document.getElementById('search-results-panel');
        
        if (event.target === modal) {
            closeAnalysisModal();
        }
        if (event.target === panel) {
            closeSearchPanel();
        }
    }
}

// ==================== INITIALIZATION HELPERS ====================
function initializeSidebar() {
    const sidebarItems = document.querySelectorAll('.nav-item');
    
    sidebarItems.forEach(item => {
        item.addEventListener('click', function() {
            sidebarItems.forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });
}

function initializeChat() {
    // Load initial chat state
    dashboardState.chatMessages = [];
}

function setupConnectionMonitoring() {
    window.addEventListener('online', function() {
        dashboardState.isOnline = true;
        showNotification('Connection restored', 'success');
    });
    
    window.addEventListener('offline', function() {
        dashboardState.isOnline = false;
        showNotification('Connection lost - working in offline mode', 'warning');
    });
}

async function loadInitialData() {
    try {
        // Load crop status
        const response = await fetch(`${API_BASE}/crop-status`);
        if (response.ok) {
            const data = await response.json();
            updateStatusCards(data);
        }
    } catch (error) {
        console.error('Error loading initial data:', error);
    }
}

function updateStatusCards(data) {
    const cardsGrid = document.getElementById('status-cards-grid');
    if (cardsGrid && data.statistics) {
        cardsGrid.innerHTML = `
            <div class="status-card healthy">
                <div class="card-icon"><i class="fas fa-check"></i></div>
                <div class="card-info">
                    <h3>Healthy</h3>
                    <p>${data.statistics.healthy_plants} plants</p>
                    <small>Optimal growth</small>
                </div>
            </div>
            <div class="status-card pests">
                <div class="card-icon"><i class="fas fa-bug"></i></div>
                <div class="card-info">
                    <h3>Pests</h3>
                    <p>${data.statistics.pest_alerts} alerts</p>
                    <small>Immediate attention</small>
                </div>
            </div>
            <div class="status-card tips">
                <div class="card-icon"><i class="fas fa-lightbulb"></i></div>
                <div class="card-info">
                    <h3>Tips</h3>
                    <p>${data.statistics.daily_tips} new tips</p>
                    <small>AI recommendations</small>
                </div>
            </div>
        `;
    }
}

console.log('🌾 Enhanced KisanSahayak AI Dashboard JavaScript loaded successfully!');

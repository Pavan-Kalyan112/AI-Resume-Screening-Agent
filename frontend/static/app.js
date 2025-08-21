// Global variables
let selectedFile = null;
let currentResumeData = null;

// DOM elements
const dropArea = document.getElementById('drop-area');
const resumeFile = document.getElementById('resume-file');
const fileInfo = document.getElementById('file-info');
const fileName = document.getElementById('file-name');
const removeFile = document.getElementById('remove-file');
const uploadBtn = document.getElementById('upload-btn');
const screeningLoader = document.getElementById('screening-loader');
const resultCard = document.getElementById('result-card');
const resultText = document.getElementById('result-text');
const analyticsSection = document.getElementById('analytics-section');
const clearUpload = document.getElementById('clear-upload');
const errorAnimated = document.getElementById('error-animated');
const errorMessage = document.getElementById('error-message');

// Tab functionality
const tabButtons = document.querySelectorAll('.tab-btn');
const tabPanels = document.querySelectorAll('.tab-panel');

tabButtons.forEach(button => {
    button.addEventListener('click', () => {
        const targetTab = button.getAttribute('data-tab');
        
        // Update tab buttons
        tabButtons.forEach(btn => {
            btn.classList.remove('tab-active');
            btn.classList.add('tab-inactive');
            btn.setAttribute('aria-selected', 'false');
        });
        button.classList.remove('tab-inactive');
        button.classList.add('tab-active');
        button.setAttribute('aria-selected', 'true');
        
        // Update tab panels
        tabPanels.forEach(panel => {
            panel.classList.remove('active');
        });
        document.getElementById(`panel-${targetTab}`).classList.add('active');
    });
});

// File upload functionality
dropArea.addEventListener('click', () => resumeFile.click());

dropArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropArea.classList.add('border-blue-400', 'dark:border-blue-500');
});

dropArea.addEventListener('dragleave', () => {
    dropArea.classList.remove('border-blue-400', 'dark:border-blue-500');
});

dropArea.addEventListener('drop', (e) => {
    e.preventDefault();
    dropArea.classList.remove('border-blue-400', 'dark:border-blue-500');
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFileSelect(files[0]);
    }
});

resumeFile.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFileSelect(e.target.files[0]);
    }
});

function handleFileSelect(file) {
    const allowedTypes = ['.pdf', '.docx', '.doc', '.txt'];
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    
    if (!allowedTypes.includes(fileExtension)) {
        showError('❌ Invalid file type. Please upload a PDF, DOCX, DOC, or TXT file.');
        return;
    }
    
    if (file.size > 10 * 1024 * 1024) {
        showError('❌ File too large. Please upload a file smaller than 10MB.');
        return;
    }
    
    selectedFile = file;
    fileName.textContent = file.name;
    fileInfo.classList.remove('hidden');
    uploadBtn.disabled = false;
}

removeFile.addEventListener('click', () => {
    selectedFile = null;
    resumeFile.value = '';
    fileInfo.classList.add('hidden');
    uploadBtn.disabled = true;
});

// Upload functionality
uploadBtn.addEventListener('click', () => {
    if (!selectedFile) {
        showError('Please select a file first.');
        return;
    }
    
    const formData = new FormData();
    formData.append('resume', selectedFile);
    
    screeningLoader.classList.remove('hidden');
    resultCard.classList.add('hidden');
    errorAnimated.classList.add('hidden');
    
    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        screeningLoader.classList.add('hidden');
        if (data.error) {
            showError(data.error);
        } else {
            showResults(data);
            currentResumeData = data;
        }
    })
    .catch(() => {
        screeningLoader.classList.add('hidden');
        showError('An error occurred during analysis.');
    });
});

function showResults(data) {
    resultCard.classList.remove('hidden');
    resultText.textContent = data.summary || 'No summary returned.';
    
    if (data.analytics) {
        showAnalytics(data.analytics, data.model_info);
    }
}

function showAnalytics(analytics, modelInfo) {
    analyticsSection.classList.remove('hidden');
    
    // Score display with RAG indicator
    const scoreDisplay = document.getElementById('score-display');
    const responseTime = document.getElementById('response-time');
    
    if (analytics.score !== undefined) {
        scoreDisplay.textContent = analytics.score;
        scoreDisplay.className = `text-2xl font-bold ${getScoreColor(analytics.score)}`;
        
        // Add RAG indicator if enhanced
        if (modelInfo && modelInfo.rag_enhanced) {
            const ragIndicator = document.createElement('div');
            ragIndicator.className = 'text-xs text-purple-600 dark:text-purple-400 mt-1 flex items-center space-x-1';
            ragIndicator.innerHTML = '<span class="material-icons text-sm">psychology</span><span>RAG Enhanced</span>';
            scoreDisplay.parentNode.appendChild(ragIndicator);
        }
    }
    
    if (modelInfo && modelInfo.response_time) {
        responseTime.textContent = `${modelInfo.response_time.toFixed(1)}s`;
    }
    
    // Skills list
    const skillsList = document.getElementById('skills-list');
    skillsList.innerHTML = '';
    if (analytics.skills && analytics.skills.length > 0) {
        analytics.skills.forEach(skill => {
            const li = document.createElement('li');
            li.className = 'flex items-center space-x-2';
            li.innerHTML = `<span class="w-2 h-2 bg-yellow-500 rounded-full"></span><span>${skill}</span>`;
            skillsList.appendChild(li);
        });
    }
    
    // Experience list
    const experienceList = document.getElementById('experience-list');
    experienceList.innerHTML = '';
    if (analytics.experience && analytics.experience.length > 0) {
        analytics.experience.forEach(exp => {
            const li = document.createElement('li');
            li.className = 'flex items-center space-x-2';
            li.innerHTML = `<span class="w-2 h-2 bg-blue-500 rounded-full"></span><span>${exp}</span>`;
            experienceList.appendChild(li);
        });
    }
    
    // Red flags list
    const redflagsList = document.getElementById('redflags-list');
    redflagsList.innerHTML = '';
    if (analytics.redflags && analytics.redflags.length > 0) {
        analytics.redflags.forEach(flag => {
            const li = document.createElement('li');
            li.className = 'flex items-center space-x-2';
            li.innerHTML = `<span class="w-2 h-2 bg-red-500 rounded-full"></span><span>${flag}</span>`;
            redflagsList.appendChild(li);
        });
    }
    
    // Add improvement suggestions if available
    if (analytics.improvement_suggestions && analytics.improvement_suggestions.length > 0) {
        const improvementSection = document.createElement('div');
        improvementSection.className = 'bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg mt-4';
        improvementSection.innerHTML = `
            <h5 class="font-semibold text-blue-800 dark:text-blue-200 mb-2">💡 Improvement Suggestions</h5>
            <ul class="text-sm text-blue-700 dark:text-blue-300 space-y-1">
                ${analytics.improvement_suggestions.map(suggestion => 
                    `<li class="flex items-center space-x-2"><span class="w-2 h-2 bg-blue-500 rounded-full"></span><span>${suggestion}</span></li>`
                ).join('')}
            </ul>
        `;
        analyticsSection.appendChild(improvementSection);
    }
}

function getScoreColor(score) {
    if (score >= 80) return 'text-green-600 dark:text-green-400';
    if (score >= 60) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
}

// Clear functionality
clearUpload.addEventListener('click', () => {
    selectedFile = null;
    resumeFile.value = '';
    fileInfo.classList.add('hidden');
    uploadBtn.disabled = true;
    resultCard.classList.add('hidden');
    errorAnimated.classList.add('hidden');
    currentResumeData = null;
});

// Error handling
function showError(message) {
    errorMessage.textContent = message;
    errorAnimated.classList.remove('hidden');
}

// JD Match functionality
const jdForm = document.getElementById('jd-form');
const jdResumeFile = document.getElementById('jd-resume-file');
const jdText = document.getElementById('jd-text');
const jdMatchBtn = document.getElementById('jd-match-btn');
const jdLoader = document.getElementById('jd-loader');
const jdResult = document.getElementById('jd-result');
const jdScore = document.getElementById('jd-score');
const matchedKeywords = document.getElementById('matched-keywords');
const missingKeywords = document.getElementById('missing-keywords');
const feedbackList = document.getElementById('feedback-list');
const clearJd = document.getElementById('clear-jd');

jdForm.addEventListener('submit', (e) => {
    e.preventDefault();
    
    const file = jdResumeFile.files[0];
    const jd = jdText.value.trim();
    
    if (!file) {
        showError('Please select a resume file.');
        return;
    }
    
    if (!jd) {
        showError('Please enter a job description.');
        return;
    }
    
    const formData = new FormData();
    formData.append('resume', file);
    formData.append('jd', jd);
    
    jdLoader.classList.remove('hidden');
    jdResult.classList.add('hidden');
    
    fetch('/jd_match', {
        method: 'POST',
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        jdLoader.classList.add('hidden');
        if (data.error) {
            showError(data.error);
        } else {
            showJDResults(data);
        }
    })
    .catch(() => {
        jdLoader.classList.add('hidden');
        showError('An error occurred during JD matching.');
    });
});

function showJDResults(data) {
    jdResult.classList.remove('hidden');
    
    if (data.analytics) {
        const analytics = data.analytics;
        
        // Match score with RAG indicator
        if (analytics.score !== undefined) {
            jdScore.textContent = analytics.score;
            jdScore.className = `text-3xl font-bold ${getScoreColor(analytics.score)}`;
            
            // Add RAG indicator if enhanced
            if (data.model_info && data.model_info.rag_enhanced) {
                const ragIndicator = document.createElement('div');
                ragIndicator.className = 'text-xs text-purple-600 dark:text-purple-400 mt-1 flex items-center space-x-1';
                ragIndicator.innerHTML = '<span class="material-icons text-sm">psychology</span><span>RAG Enhanced</span>';
                jdScore.parentNode.appendChild(ragIndicator);
            }
        }
        
        // Matched keywords
        matchedKeywords.innerHTML = '';
        if (analytics.matched_keywords && analytics.matched_keywords.length > 0) {
            analytics.matched_keywords.forEach(keyword => {
                const span = document.createElement('span');
                span.className = 'bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 px-2 py-1 rounded text-sm';
                span.textContent = keyword;
                matchedKeywords.appendChild(span);
            });
        }
        
        // Missing keywords
        missingKeywords.innerHTML = '';
        if (analytics.missing_keywords && analytics.missing_keywords.length > 0) {
            analytics.missing_keywords.forEach(keyword => {
                const span = document.createElement('span');
                span.className = 'bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 px-2 py-1 rounded text-sm';
                span.textContent = keyword;
                missingKeywords.appendChild(span);
            });
        }
        
        // Feedback
        feedbackList.innerHTML = '';
        if (analytics.feedback && analytics.feedback.length > 0) {
            analytics.feedback.forEach(feedback => {
                const li = document.createElement('li');
                li.className = 'flex items-center space-x-2';
                li.innerHTML = `<span class="w-2 h-2 bg-blue-500 rounded-full"></span><span>${feedback}</span>`;
                feedbackList.appendChild(li);
            });
        }
        
        // Add action items if available
        if (analytics.action_items && analytics.action_items.length > 0) {
            const actionSection = document.createElement('div');
            actionSection.className = 'bg-purple-50 dark:bg-purple-900/20 p-4 rounded-lg mt-4';
            actionSection.innerHTML = `
                <h5 class="font-semibold text-purple-800 dark:text-purple-200 mb-2">🎯 Action Items</h5>
                <ul class="text-sm text-purple-700 dark:text-purple-300 space-y-1">
                    ${analytics.action_items.map(item => 
                        `<li class="flex items-center space-x-2"><span class="w-2 h-2 bg-purple-500 rounded-full"></span><span>${item}</span></li>`
                    ).join('')}
                </ul>
            `;
            jdResult.appendChild(actionSection);
        }
        
        // Add skill gaps if available
        if (analytics.skill_gaps && analytics.skill_gaps.length > 0) {
            const skillGapsSection = document.createElement('div');
            skillGapsSection.className = 'bg-yellow-50 dark:bg-yellow-900/20 p-4 rounded-lg mt-4';
            skillGapsSection.innerHTML = `
                <h5 class="font-semibold text-yellow-800 dark:text-yellow-200 mb-2">📚 Skill Gaps & Learning Paths</h5>
                <div class="space-y-3">
                    ${analytics.skill_gaps.map(gap => `
                        <div class="border-l-4 border-yellow-500 pl-3">
                            <div class="font-medium text-yellow-800 dark:text-yellow-200">${gap.skill}</div>
                            <div class="text-sm text-yellow-700 dark:text-yellow-300">
                                <div>Importance: ${gap.importance}</div>
                                <div>Learning Path: ${gap.learning_path}</div>
                                <div>Time to Learn: ${gap.time_to_learn}</div>
                                ${gap.priority ? `<div>Priority: ${gap.priority}</div>` : ''}
                    </div>
                    </div>
                    `).join('')}
                    </div>
            `;
            jdResult.appendChild(skillGapsSection);
        }
    }
}

clearJd.addEventListener('click', () => {
    jdResumeFile.value = '';
    jdText.value = '';
    jdResult.classList.add('hidden');
    jdLoader.classList.add('hidden');
});

// Chat functionality
const chatForm = document.getElementById('chat-form');
const chatInput = document.getElementById('chat-input');
const chatBox = document.getElementById('chat-box');
const typingIndicator = document.getElementById('typing-indicator');

chatForm.addEventListener('submit', function(e) {
    e.preventDefault();
    const message = chatInput.value.trim();
    if (!message) return;
    
    // Add user message
    addChatMessage('user', message);
    chatInput.value = '';
    
    // Show typing indicator
    typingIndicator.classList.remove('hidden');
    
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ message: message })
    })
    .then(res => res.json())
    .then(data => {
        typingIndicator.classList.add('hidden');
        if (data.error) {
            addChatMessage('ai', `Error: ${data.error}`);
        } else {
            addChatMessage('ai', data.response, data.rag_enhanced);
        }
    })
    .catch(() => {
        typingIndicator.classList.add('hidden');
        addChatMessage('ai', 'Sorry, I encountered an error. Please try again.');
    });
});

function addChatMessage(sender, message, ragEnhanced = false) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-bubble-${sender} mb-4`;
    
    const timestamp = new Date().toLocaleTimeString();
    let ragIndicator = '';
    if (sender === 'ai' && ragEnhanced) {
        ragIndicator = '<div class="text-xs text-purple-600 dark:text-purple-400 mt-1 flex items-center space-x-1"><span class="material-icons text-sm">psychology</span><span>RAG Enhanced</span></div>';
    }
    
    messageDiv.innerHTML = `
        <div class="flex ${sender === 'user' ? 'justify-end' : 'justify-start'}">
            <div class="max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${sender === 'user' ? 'bg-blue-600 text-white' : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-gray-100'}">
                <p class="text-sm">${message}</p>
                <p class="text-xs opacity-75 mt-1">${timestamp}</p>
                ${ragIndicator}
            </div>
        </div>
    `;
    
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

// Analytics panel functionality
function updateAnalyticsPanel() {
    const analyticsContent = document.getElementById('analytics-content');
    
    if (currentResumeData && currentResumeData.analytics) {
        const analytics = currentResumeData.analytics;
        const modelInfo = currentResumeData.model_info;
        
        let ragIndicator = '';
        if (modelInfo && modelInfo.rag_enhanced) {
            ragIndicator = '<div class="text-sm text-purple-600 dark:text-purple-400 mb-4 flex items-center space-x-2"><span class="material-icons">psychology</span><span>Enhanced with RAG Knowledge Base</span></div>';
        }
        
        analyticsContent.innerHTML = `
            <div class="space-y-6">
                ${ragIndicator}
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div class="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div class="flex items-center justify-between">
                            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Resume Score</span>
                            <div class="text-2xl font-bold ${getScoreColor(analytics.score)}">${analytics.score || 'N/A'}</div>
                </div>
                </div>
                    <div class="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                        <div class="flex items-center justify-between">
                            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">Skills Count</span>
                            <div class="text-2xl font-bold text-blue-600 dark:text-blue-400">${analytics.skills ? analytics.skills.length : 0}</div>
            </div>
                    </div>
                </div>
                
                <div class="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                    <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">📊 Skills Breakdown</h4>
                    <div class="flex flex-wrap gap-2">
                        ${analytics.skills ? analytics.skills.map(skill => 
                            `<span class="bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 px-3 py-1 rounded-full text-sm">${skill}</span>`
                        ).join('') : '<p class="text-gray-500">No skills data available</p>'}
                    </div>
                </div>
                
                <div class="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                    <h4 class="font-semibold text-gray-900 dark:text-gray-100 mb-3">💼 Experience Summary</h4>
                    <ul class="space-y-2">
                        ${analytics.experience ? analytics.experience.map(exp => 
                            `<li class="flex items-center space-x-2"><span class="w-2 h-2 bg-blue-500 rounded-full"></span><span class="text-gray-700 dark:text-gray-300">${exp}</span></li>`
                        ).join('') : '<li class="text-gray-500">No experience data available</li>'}
                    </ul>
                </div>
                
                ${analytics.redflags && analytics.redflags.length > 0 ? `
                <div class="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                    <h4 class="font-semibold text-red-800 dark:text-red-200 mb-3">⚠️ Areas for Improvement</h4>
                    <ul class="space-y-2">
                        ${analytics.redflags.map(flag => 
                            `<li class="flex items-center space-x-2"><span class="w-2 h-2 bg-red-500 rounded-full"></span><span class="text-red-700 dark:text-red-300">${flag}</span></li>`
                        ).join('')}
                    </ul>
                </div>
                ` : ''}
                
                ${analytics.improvement_suggestions && analytics.improvement_suggestions.length > 0 ? `
                <div class="bg-white dark:bg-gray-800 p-4 rounded-lg border border-gray-200 dark:border-gray-700">
                    <h4 class="font-semibold text-green-800 dark:text-green-200 mb-3">💡 Improvement Suggestions</h4>
                    <ul class="space-y-2">
                        ${analytics.improvement_suggestions.map(suggestion => 
                            `<li class="flex items-center space-x-2"><span class="w-2 h-2 bg-green-500 rounded-full"></span><span class="text-green-700 dark:text-green-300">${suggestion}</span></li>`
                        ).join('')}
                    </ul>
                </div>
                ` : ''}
            </div>
        `;
            } else {
        analyticsContent.innerHTML = `
            <div class="text-center py-12">
                <div class="text-gray-500 dark:text-gray-400">
                    <span class="material-icons text-6xl mb-4">analytics</span>
                    <p class="text-lg">Upload a resume first to view analytics</p>
                </div>
            </div>
        `;
    }
}

// Update analytics when resume is uploaded
function showResults(data) {
    resultCard.classList.remove('hidden');
    resultText.textContent = data.summary || 'No summary returned.';
    
    if (data.analytics) {
        showAnalytics(data.analytics, data.model_info);
        currentResumeData = data;
        updateAnalyticsPanel();
    }
}

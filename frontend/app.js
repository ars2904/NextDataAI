// NexaData AI App Controller - Independent Dual-Tab Threads, Theme & Dynamic History

let currentMode = 'company';
let isSending = false;
let currentTheme = localStorage.getItem('nexadata_theme') || 'dark';

// Storage Keys
const STORAGE_KEY_CONVS = 'nexadata_saved_conversations';
const STORAGE_KEY_ACTIVE = 'nexadata_active_conv_id';

let activeConvId = localStorage.getItem(STORAGE_KEY_ACTIVE) || null;
let conversations = [];

// Independent Conversation Threads for active view
const threads = {
  company: [],
  general: []
};

// Elements
const pillCompany = document.getElementById('pillCompany');
const pillGeneral = document.getElementById('pillGeneral');
const sideBtnCompany = document.getElementById('sideBtnCompany');
const sideBtnGeneral = document.getElementById('sideBtnGeneral');
const chatInput = document.getElementById('chatInput');
const btnSend = document.getElementById('btnSend');
const chatArea = document.getElementById('chatArea');
const welcomeScreen = document.getElementById('welcomeScreen');
const welcomeSubtitle = document.getElementById('welcomeSubtitle');
const btnNewChat = document.getElementById('btnNewChat');
const sidebar = document.getElementById('sidebar');
const sidebarOverlay = document.getElementById('sidebarOverlay');

// Helper: Escape HTML
function escapeHtml(text) {
  if (!text) return '';
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ----------------------------------------------------
// Theme Management
// ----------------------------------------------------
function initTheme() {
  applyTheme(currentTheme);
}

function toggleTheme() {
  currentTheme = currentTheme === 'dark' ? 'light' : 'dark';
  localStorage.setItem('nexadata_theme', currentTheme);
  applyTheme(currentTheme);
}

function applyTheme(theme) {
  document.documentElement.setAttribute('data-theme', theme);
  const themeToggleIcon = document.getElementById('themeToggleIcon');
  const themeToggleLabel = document.querySelector('.theme-toggle-label');
  const sidebarLogo = document.getElementById('sidebarLogo');
  const mobileLogo = document.getElementById('mobileLogo');

  const logoSrc = theme === 'dark' ? '/static/logo_dark.png' : '/static/logo_light.png';
  if (sidebarLogo) sidebarLogo.src = logoSrc;
  if (mobileLogo) mobileLogo.src = logoSrc;

  if (themeToggleIcon) {
    themeToggleIcon.textContent = theme === 'dark' ? '🌙' : '☀️';
  }
  if (themeToggleLabel) {
    themeToggleLabel.textContent = theme === 'dark' ? 'Dark' : 'Light';
  }
}

// ----------------------------------------------------
// Storage & Conversation History
// ----------------------------------------------------
function loadSavedConversations() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_CONVS);
    conversations = raw ? JSON.parse(raw) : [];
  } catch (e) {
    conversations = [];
  }

  // If no conversations stored yet (or legacy 2 items), populate full 5 starter conversations
  if (!conversations || conversations.length <= 2) {
    conversations = [
      {
        id: 'starter_1',
        title: 'What is NexaData?',
        mode: 'company',
        icon: '💬',
        messages: [
          { type: 'user', text: 'What is NexaData and what solutions do you offer?', timestamp: '10:20 AM' },
          { 
            type: 'bot', 
            reply: 'NexaData AI is an autonomous enterprise data intelligence platform providing document-grounded analytics, real-time knowledge synthesis, and automated business workflows.',
            timestamp: '10:20 AM',
            sources: [{ document: 'NexaData_Company_Overview_and_Services.pdf', page: 1, snippet: 'NexaData platform mission and core capabilities...' }],
            mode: 'company'
          }
        ],
        updatedAt: Date.now() - 120000
      },
      {
        id: 'starter_2',
        title: 'Our solutions overview',
        mode: 'company',
        icon: '📊',
        messages: [
          { type: 'user', text: 'What are your enterprise solutions and pricing plans?', timestamp: '09:30 AM' },
          { 
            type: 'bot', 
            reply: 'We offer Enterprise Engine ($12,500/mo), Cloud Analytics ($4,800/mo), Secure Sandbox ($2,200/mo), and Custom ETL pipelines with dedicated engineering.',
            timestamp: '09:30 AM',
            sources: [{ document: 'NexaData_Company_Overview_and_Services.pdf', page: 2, snippet: 'Enterprise solutions and subscription tiers...' }],
            mode: 'company'
          }
        ],
        updatedAt: Date.now() - 3600000
      },
      {
        id: 'starter_3',
        title: 'Pricing information',
        mode: 'company',
        icon: '💳',
        messages: [
          { type: 'user', text: 'What is the pricing breakdown for your platform tiers?', timestamp: '08:15 AM' },
          { 
            type: 'bot', 
            reply: 'Pricing starts at $1,500/mo for Developer API Gateway up to $12,500/mo for Platinum Enterprise Engine, with volume discounts on multi-year agreements.',
            timestamp: '08:15 AM',
            sources: [{ document: 'NexaData_Company_Overview_and_Services.pdf', page: 3, snippet: 'Platform pricing and licensing options...' }],
            mode: 'company'
          }
        ],
        updatedAt: Date.now() - 10800000
      },
      {
        id: 'starter_4',
        title: 'Security & Data privacy',
        mode: 'company',
        icon: '🛡️',
        messages: [
          { type: 'user', text: 'What are your data privacy and security policies?', timestamp: 'Yesterday' },
          { 
            type: 'bot', 
            reply: 'We enforce zero data leakage, client-isolated enclaves, HIPAA/SOC2 compliant storage, and end-to-end encrypted query pipelines.',
            timestamp: 'Yesterday',
            sources: [{ document: 'NexaData_Company_Overview_and_Services.pdf', page: 4, snippet: 'Data privacy and security standards...' }],
            mode: 'company'
          }
        ],
        updatedAt: Date.now() - 18000000
      },
      {
        id: 'starter_5',
        title: 'Enterprise support',
        mode: 'company',
        icon: '⚡',
        messages: [
          { type: 'user', text: 'What level of technical support is included in enterprise tiers?', timestamp: '2 days ago' },
          { 
            type: 'bot', 
            reply: 'Enterprise plans include 24/7 dedicated solutions engineering, a 99.99% uptime SLA, priority bug resolution, and custom connector integration.',
            timestamp: '2 days ago',
            sources: [{ document: 'NexaData_Company_Overview_and_Services.pdf', page: 5, snippet: 'Dedicated enterprise engineering and SLA...' }],
            mode: 'company'
          }
        ],
        updatedAt: Date.now() - 86400000
      }
    ];
    saveConversationsToStorage();
  }
}

function saveConversationsToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY_CONVS, JSON.stringify(conversations));
    // Asynchronously sync active conversation to server-side PostgreSQL
    if (activeConvId) {
      const active = conversations.find(c => c.id === activeConvId);
      if (active) {
        fetch('/api/conversations', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(active)
        }).catch(() => {});
      }
    }
  } catch (e) {
    console.error('Failed to save conversations:', e);
  }
}

function renderHistoryList(filterTerm = '') {
  const container = document.getElementById('historyListContainer');
  if (!container) return;

  container.innerHTML = '';
  const lower = (filterTerm || '').toLowerCase().trim();

  const filtered = conversations.filter(c => 
    !lower || (c.title && c.title.toLowerCase().includes(lower))
  );

  if (filtered.length === 0) {
    container.innerHTML = `
      <div style="padding: 14px 10px; font-size: 12px; color: var(--text-dim); text-align: center;">
        No conversations found.
      </div>
    `;
    return;
  }

  filtered.forEach(conv => {
    const item = document.createElement('div');
    const isActive = conv.id === activeConvId;
    item.className = 'history-item' + (isActive ? ' active' : '');
    item.onclick = () => openConversation(conv.id);

    let icon = conv.icon || (conv.mode === 'company' ? '📄' : '💬');
    let iconClass = 'blue';
    const tLower = (conv.title || '').toLowerCase();
    if (tLower.includes('what is')) { icon = '💬'; iconClass = 'blue'; }
    else if (tLower.includes('solution') || tLower.includes('overview')) { icon = '📊'; iconClass = 'cyan'; }
    else if (tLower.includes('pricing') || tLower.includes('cost') || tLower.includes('price')) { icon = '💳'; iconClass = 'teal'; }
    else if (tLower.includes('security') || tLower.includes('privacy')) { icon = '🛡️'; iconClass = 'green'; }
    else if (tLower.includes('support') || tLower.includes('pipeline') || tLower.includes('enterprise')) { icon = '⚡'; iconClass = 'amber'; }

    let snippet = 'Conversation ready';
    if (conv.messages && conv.messages.length > 0) {
      const last = conv.messages[conv.messages.length - 1];
      const rawText = last.reply || last.text || '';
      snippet = rawText.replace(/[#*`_\[\]()]/g, '').trim().substring(0, 38) + '...';
    }

    item.innerHTML = `
      <div class="history-item-left">
        <div class="history-item-icon ${iconClass}">${icon}</div>
        <div class="history-item-details">
          <span class="history-title" title="${escapeHtml(conv.title)}">${escapeHtml(conv.title)}</span>
          <span class="history-subtitle">${escapeHtml(snippet)}</span>
        </div>
      </div>
      <div class="history-item-right">
        <button class="history-dots-btn" onclick="event.stopPropagation(); toggleHistoryMenu(this)" title="Options">···</button>
      </div>
      <div class="history-dropdown">
        <button class="history-dropdown-btn" onclick="event.stopPropagation(); renameConversation('${conv.id}')">✏️ Rename</button>
        <button class="history-dropdown-btn delete" onclick="event.stopPropagation(); deleteConversation('${conv.id}')">🗑️ Delete</button>
      </div>
    `;

    container.appendChild(item);
  });
}

function openConversation(convId) {
  const conv = conversations.find(c => c.id === convId);
  if (!conv) return;

  activeConvId = convId;
  localStorage.setItem(STORAGE_KEY_ACTIVE, convId);

  // Switch to the conversation's mode
  currentMode = conv.mode || 'company';
  updateModePillsUI();

  // Load its messages into current mode thread
  threads[currentMode] = (conv.messages || []).map(m => ({ ...m }));
  renderActiveThread();
  renderHistoryList();
  closeSidebar();
}

function startNewConversation() {
  activeConvId = null;
  localStorage.removeItem(STORAGE_KEY_ACTIVE);
  threads[currentMode] = [];
  renderActiveThread();
  renderHistoryList();
  chatInput.value = '';
  chatInput.focus();
  closeSidebar();
}

function renameConversation(convId) {
  const conv = conversations.find(c => c.id === convId);
  if (!conv) return;
  const newName = prompt('Enter new conversation title:', conv.title);
  if (newName && newName.trim()) {
    conv.title = newName.trim();
    saveConversationsToStorage();
    renderHistoryList();
  }
}

function deleteConversation(convId) {
  if (confirm('Delete this conversation from history?')) {
    conversations = conversations.filter(c => c.id !== convId);
    saveConversationsToStorage();
    fetch(`/api/conversations/${convId}`, { method: 'DELETE' }).catch(() => {});
    if (activeConvId === convId) {
      startNewConversation();
    } else {
      renderHistoryList();
    }
  }
}

function filterHistory(term) {
  renderHistoryList(term);
}

// ----------------------------------------------------
// Mode Switcher (Independent Tab Isolation)
// ----------------------------------------------------
function updateModePillsUI() {
  document.body.setAttribute('data-mode', currentMode);
  if (welcomeScreen) {
    welcomeScreen.setAttribute('data-mode', currentMode);
  }

  if (currentMode === 'company') {
    pillCompany.classList.add('active');
    pillGeneral.classList.remove('active');
    sideBtnCompany.classList.add('active');
    sideBtnGeneral.classList.remove('active');
    chatInput.placeholder = 'Ask anything about NexaData...';
  } else {
    pillGeneral.classList.add('active');
    pillCompany.classList.remove('active');
    sideBtnGeneral.classList.add('active');
    sideBtnCompany.classList.remove('active');
    chatInput.placeholder = 'Ask anything or type a prompt...';
  }
}

function switchMode(newMode) {
  if (currentMode === newMode) return;
  currentMode = newMode;
  updateModePillsUI();

  // If active conversation belongs to a different mode, reset active ID
  if (activeConvId) {
    const active = conversations.find(c => c.id === activeConvId);
    if (active && active.mode !== currentMode) {
      activeConvId = null;
      localStorage.removeItem(STORAGE_KEY_ACTIVE);
      threads[currentMode] = [];
      renderHistoryList();
    }
  }

  // Switch to the selected tab's isolated thread
  renderActiveThread();
  chatInput.focus();
}

// ----------------------------------------------------
// Welcome Screen (Option B: Minimalist on General Tab)
// ----------------------------------------------------
function updateWelcomeScreenContent() {
  document.body.setAttribute('data-mode', currentMode);
  if (welcomeScreen) {
    welcomeScreen.setAttribute('data-mode', currentMode);
  }

  const cardsGrid = welcomeScreen ? welcomeScreen.querySelector('#companyCardsGrid') : document.getElementById('companyCardsGrid');
  const pillsRow = welcomeScreen ? welcomeScreen.querySelector('#companyPillsRow') : document.getElementById('companyPillsRow');
  const heading = welcomeScreen ? welcomeScreen.querySelector('.welcome-heading') : document.querySelector('.welcome-heading');
  const subtitle = welcomeSubtitle || (welcomeScreen ? welcomeScreen.querySelector('#welcomeSubtitle') : null);

  if (currentMode === 'company') {
    if (heading) heading.textContent = 'Welcome to NexaData AI';
    if (subtitle) subtitle.textContent = "Get accurate answers from NexaData's official documents.";
    if (cardsGrid) cardsGrid.style.display = 'grid';
    if (pillsRow) pillsRow.style.display = 'flex';
  } else {
    // Option B: Minimalist General Questions View
    if (heading) heading.textContent = 'How can I help you today?';
    if (subtitle) subtitle.textContent = 'Ask me anything — explore ideas, write, summarize, brainstorm, solve problems, or chat about any topic.';
    if (cardsGrid) cardsGrid.style.display = 'none';
    if (pillsRow) pillsRow.style.display = 'none';
  }
}

// ----------------------------------------------------
// Render Active Thread
// ----------------------------------------------------
function renderActiveThread() {
  const activeThread = threads[currentMode];

  // If no messages in this tab yet, show that tab's welcome screen
  if (!activeThread || activeThread.length === 0) {
    chatArea.innerHTML = '';
    welcomeScreen.style.display = 'flex';
    chatArea.appendChild(welcomeScreen);
    updateWelcomeScreenContent();
    return;
  }

  // Otherwise, hide welcome screen and restore that tab's messages
  welcomeScreen.style.display = 'none';
  chatArea.innerHTML = '';

  activeThread.forEach(item => {
    if (item.type === 'user') {
      renderUserBubble(item.text, item.timestamp, item.attachment);
    } else if (item.type === 'bot') {
      renderBotBubble(item.reply, item.timestamp, item.sources, item.mode);
    }
  });

  chatArea.scrollTop = chatArea.scrollHeight;
}

// ----------------------------------------------------
// File & Image Attachment Handling (Max 10 MB)
// ----------------------------------------------------
let stagedAttachment = null;

const SUPPORTED_ATTACHMENT_EXTENSIONS = ['pdf', 'docx', 'txt', 'csv', 'png', 'jpg', 'jpeg', 'webp'];
const MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024; // 10 MB

function formatFileSize(bytes) {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function handleFileSelect(event) {
  const file = event.target.files && event.target.files[0];
  if (!file) return;

  const ext = file.name.split('.').pop().toLowerCase();
  if (!SUPPORTED_ATTACHMENT_EXTENSIONS.includes(ext)) {
    alert(`Unsupported file format '.${ext}'. Please select a PDF, DOCX, TXT, CSV, PNG, JPG, or WEBP file.`);
    event.target.value = '';
    return;
  }

  if (file.size > MAX_ATTACHMENT_BYTES) {
    alert(`File is too large (${formatFileSize(file.size)}). The maximum allowed file size is 10 MB.`);
    event.target.value = '';
    return;
  }

  const isImage = ['png', 'jpg', 'jpeg', 'webp'].includes(ext);
  let previewUrl = null;

  if (isImage) {
    previewUrl = URL.createObjectURL(file);
  }

  stagedAttachment = {
    file: file,
    name: file.name,
    size: formatFileSize(file.size),
    sizeBytes: file.size,
    ext: ext,
    isImage: isImage,
    previewUrl: previewUrl
  };

  // Update UI preview bar
  const bar = document.getElementById('filePreviewBar');
  const thumb = document.getElementById('filePreviewThumb');
  const nameEl = document.getElementById('filePreviewName');
  const metaEl = document.getElementById('filePreviewMeta');

  if (bar && thumb && nameEl && metaEl) {
    nameEl.textContent = file.name;
    metaEl.textContent = `${formatFileSize(file.size)} • Ready to analyze`;

    if (isImage && previewUrl) {
      thumb.innerHTML = `<img src="${previewUrl}" alt="Preview">`;
    } else {
      let icon = '📄';
      if (ext === 'csv') icon = '📊';
      else if (ext === 'docx') icon = '📑';
      else if (ext === 'txt') icon = '📝';
      thumb.innerHTML = icon;
    }
    bar.style.display = 'flex';
  }
}

function removeAttachedFile() {
  if (stagedAttachment && stagedAttachment.previewUrl) {
    URL.revokeObjectURL(stagedAttachment.previewUrl);
  }
  stagedAttachment = null;
  const fileInput = document.getElementById('fileInput');
  if (fileInput) fileInput.value = '';

  const bar = document.getElementById('filePreviewBar');
  if (bar) bar.style.display = 'none';
}

// ----------------------------------------------------
// Voice Recording & Speech Recognition (English / Hindi)
// ----------------------------------------------------
let isRecordingVoice = false;
let speechRecognition = null;
let currentSpeechLang = 'en-IN';
let initialTextBeforeVoice = '';
let mediaRecorder = null;
let recordedAudioChunks = [];
let voiceStream = null;

function setSpeechLanguage(lang) {
  currentSpeechLang = lang;
  const btnEn = document.getElementById('btnLangEn');
  const btnHi = document.getElementById('btnLangHi');

  if (btnEn && btnHi) {
    if (lang.startsWith('hi')) {
      btnHi.classList.add('active');
      btnEn.classList.remove('active');
    } else {
      btnEn.classList.add('active');
      btnHi.classList.remove('active');
    }
  }

  if (speechRecognition && isRecordingVoice) {
    speechRecognition.lang = lang;
  }
}

function updateVoiceRecordingUI(isRecording, statusText = '') {
  const bar = document.getElementById('voiceRecordingBar');
  const statusEl = document.getElementById('voiceRecordingStatus');
  const micBtn = document.getElementById('btnMic');

  if (bar) bar.style.display = isRecording ? 'flex' : 'none';
  if (statusEl && statusText) statusEl.textContent = statusText;
  if (micBtn) {
    if (isRecording) {
      micBtn.classList.add('recording');
      micBtn.setAttribute('title', 'Recording in progress... Click to stop');
    } else {
      micBtn.classList.remove('recording');
      micBtn.setAttribute('title', 'Speak your question (English / Hindi)');
    }
  }
}

function toggleVoiceRecording() {
  if (isRecordingVoice) {
    stopVoiceRecording(true);
  } else {
    startVoiceRecording();
  }
}

function startVoiceRecording() {
  initialTextBeforeVoice = chatInput.value;
  const SpeechRecClass = window.SpeechRecognition || window.webkitSpeechRecognition;

  if (SpeechRecClass) {
    try {
      speechRecognition = new SpeechRecClass();
      speechRecognition.continuous = true;
      speechRecognition.interimResults = true;
      speechRecognition.lang = currentSpeechLang;

      speechRecognition.onstart = () => {
        isRecordingVoice = true;
        const langLabel = currentSpeechLang.startsWith('hi') ? 'Hindi (हिंदी)' : 'English';
        updateVoiceRecordingUI(true, `Listening in ${langLabel}... Speak now`);
      };

      speechRecognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          const item = event.results[i];
          if (item.isFinal) {
            finalTranscript += item[0].transcript;
          } else {
            interimTranscript += item[0].transcript;
          }
        }

        const transcript = (finalTranscript || interimTranscript).trim();
        if (transcript) {
          const prefix = initialTextBeforeVoice.trim() ? initialTextBeforeVoice.trim() + ' ' : '';
          chatInput.value = prefix + transcript;
          adjustInputHeight(chatInput);
          chatInput.scrollTop = chatInput.scrollHeight;
        }
      };

      speechRecognition.onerror = (event) => {
        console.warn('SpeechRecognition error:', event.error);
        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          alert('Microphone access was denied. Please allow microphone permissions in your browser address bar.');
          stopVoiceRecording(false);
        } else if (event.error === 'no-speech') {
          updateVoiceRecordingUI(true, 'No speech detected. Still listening...');
        } else {
          stopVoiceRecording(true);
        }
      };

      speechRecognition.onend = () => {
        if (isRecordingVoice) {
          stopVoiceRecording(true);
        }
      };

      speechRecognition.start();
      return;
    } catch (err) {
      console.warn('SpeechRecognition initialization failed, trying MediaRecorder fallback:', err);
    }
  }

  // Fallback to MediaRecorder audio capture with server-side transcription
  startMediaRecorderFallback();
}

async function startMediaRecorderFallback() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert('Voice input is not supported in this browser. Please use Chrome, Edge, Safari, or a modern mobile browser.');
    return;
  }

  try {
    voiceStream = await navigator.mediaDevices.getUserMedia({ audio: true });
    recordedAudioChunks = [];
    mediaRecorder = new MediaRecorder(voiceStream);

    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        recordedAudioChunks.push(e.data);
      }
    };

    mediaRecorder.onstop = async () => {
      if (voiceStream) {
        voiceStream.getTracks().forEach(track => track.stop());
        voiceStream = null;
      }

      if (recordedAudioChunks.length > 0 && isRecordingVoice) {
        updateVoiceRecordingUI(true, 'Transcribing audio...');
        const audioBlob = new Blob(recordedAudioChunks, { type: 'audio/webm' });
        const formData = new FormData();
        formData.append('file', audioBlob, 'voice_recording.webm');
        formData.append('language', currentSpeechLang.startsWith('hi') ? 'hi' : 'en');

        try {
          const res = await fetch('/api/transcribe', { method: 'POST', body: formData });
          if (res.ok) {
            const data = await res.json();
            if (data.text) {
              const prefix = initialTextBeforeVoice.trim() ? initialTextBeforeVoice.trim() + ' ' : '';
              chatInput.value = prefix + data.text.trim();
              adjustInputHeight(chatInput);
            }
          }
        } catch (err) {
          console.warn('Transcription request failed:', err);
        }
      }
      stopVoiceRecording(true);
    };

    mediaRecorder.start();
    isRecordingVoice = true;
    updateVoiceRecordingUI(true, 'Recording audio... Click Done when finished');
  } catch (err) {
    console.warn('Microphone permission error:', err);
    if (err.name === 'NotAllowedError' || err.name === 'PermissionDeniedError') {
      alert('Microphone permission was denied. Please allow microphone access to use voice input.');
    } else {
      alert(`Could not access microphone: ${err.message}`);
    }
    stopVoiceRecording(false);
  }
}

function stopVoiceRecording(keepText = true) {
  isRecordingVoice = false;

  if (speechRecognition) {
    try {
      speechRecognition.stop();
    } catch (e) {}
    speechRecognition = null;
  }

  if (mediaRecorder && mediaRecorder.state !== 'inactive') {
    try {
      mediaRecorder.stop();
    } catch (e) {}
    mediaRecorder = null;
  }

  if (voiceStream) {
    try {
      voiceStream.getTracks().forEach(track => track.stop());
    } catch (e) {}
    voiceStream = null;
  }

  if (!keepText) {
    chatInput.value = initialTextBeforeVoice;
    adjustInputHeight(chatInput);
  }

  updateVoiceRecordingUI(false);
  chatInput.focus();
}

// ----------------------------------------------------
// Inputs & Actions
// ----------------------------------------------------
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    submitMessage();
  }
}

function adjustInputHeight(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
}

function triggerPrompt(promptText) {
  chatInput.value = promptText;
  submitMessage();
}

function getTimeString() {
  const d = new Date();
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// ----------------------------------------------------
// Send Message
// ----------------------------------------------------
async function submitMessage() {
  const query = chatInput.value.trim();
  if ((!query && !stagedAttachment) || isSending) return;

  const modeForThisQuery = currentMode;
  const time = getTimeString();
  const attachmentToSend = stagedAttachment;

  // Title for conversation
  const convTitle = query || (attachmentToSend ? `File: ${attachmentToSend.name}` : 'New Conversation');

  // If there is no active conversation yet, create one now!
  if (!activeConvId) {
    activeConvId = 'conv_' + Date.now();
    localStorage.setItem(STORAGE_KEY_ACTIVE, activeConvId);
    const newConv = {
      id: activeConvId,
      title: convTitle.length > 32 ? convTitle.substring(0, 32) + '...' : convTitle,
      mode: modeForThisQuery,
      messages: [],
      updatedAt: Date.now()
    };
    conversations.unshift(newConv);
  } else {
    // Bring active conversation to top
    const existingIdx = conversations.findIndex(c => c.id === activeConvId);
    if (existingIdx > 0) {
      const conv = conversations.splice(existingIdx, 1)[0];
      conversations.unshift(conv);
    }
  }

  // Hide welcome screen
  if (welcomeScreen && welcomeScreen.style.display !== 'none') {
    welcomeScreen.style.display = 'none';
  }

  // Clear input
  chatInput.value = '';
  chatInput.style.height = '24px';
  chatInput.focus();

  // Reset file staging UI immediately so user sees clear input
  removeAttachedFile();

  // Save to thread and render
  const userMsg = {
    type: 'user',
    text: query,
    timestamp: time,
    attachment: attachmentToSend ? {
      name: attachmentToSend.name,
      size: attachmentToSend.size,
      isImage: attachmentToSend.isImage,
      dataUrl: attachmentToSend.previewUrl
    } : null
  };
  threads[modeForThisQuery].push(userMsg);

  // Sync to active conversation
  const currentConv = conversations.find(c => c.id === activeConvId);
  if (currentConv) {
    currentConv.messages.push(userMsg);
    currentConv.updatedAt = Date.now();
    saveConversationsToStorage();
    renderHistoryList();
  }

  renderUserBubble(query, time, userMsg.attachment);

  // Show Typing Indicator
  const typingElement = appendTypingIndicator();
  isSending = true;
  btnSend.disabled = true;

  try {
    // Extract prior conversational turns for context (up to last 8 messages prior to current turn)
    const priorThread = threads[modeForThisQuery] || [];
    const previousMessages = priorThread.slice(0, -1);
    const recentHistory = previousMessages
      .filter(m => (m.type === 'user' && m.text) || (m.type === 'bot' && m.reply))
      .slice(-8)
      .map(m => ({
        role: m.type === 'user' ? 'user' : 'assistant',
        content: m.type === 'user' ? (m.text || '') : (m.reply || '')
      }));

    if (attachmentToSend && attachmentToSend.file) {
      // Multipart upload with file
      const formData = new FormData();
      formData.append('message', query || '');
      formData.append('mode', modeForThisQuery);
      formData.append('conversation_history', JSON.stringify(recentHistory));
      formData.append('file', attachmentToSend.file);

      const res = await fetch('/api/chat-upload', {
        method: 'POST',
        body: formData
      });

      typingElement.remove();

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `HTTP ${res.status}`);
      }

      const data = await res.json();
      const replyTime = data.timestamp || getTimeString();

      const botMsg = {
        type: 'bot',
        reply: data.reply,
        timestamp: replyTime,
        sources: data.sources || [],
        mode: modeForThisQuery,
        attachment_info: data.attachment_info || null
      };

      // Save response to thread
      threads[modeForThisQuery].push(botMsg);

      // Sync to active conversation in storage
      if (currentConv) {
        currentConv.messages.push(botMsg);
        currentConv.updatedAt = Date.now();
        saveConversationsToStorage();
        renderHistoryList();
      }

      // Render if still on the same tab
      if (currentMode === modeForThisQuery) {
        renderBotBubble(data.reply, replyTime, data.sources, modeForThisQuery);
      }

    } else {
      // Real-time progressive token streaming via Server-Sent Events (SSE)
      const res = await fetch('/api/chat-stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: query,
          mode: modeForThisQuery,
          conversation_history: recentHistory
        })
      });

      typingElement.remove();

      if (!res.ok) {
        const errJson = await res.json().catch(() => ({}));
        throw new Error(errJson.detail || `HTTP ${res.status}`);
      }

      // Initialize streaming bubble
      const streamObj = createStreamingBotBubble(modeForThisQuery);
      let streamedText = '';
      let streamSources = [];
      let finalTimestamp = getTimeString();

      const reader = res.body.getReader();
      const decoder = new TextDecoder('utf-8');
      let buffer = '';

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const events = buffer.split('\n\n');
        buffer = events.pop();

        for (const evt of events) {
          const trimmed = evt.trim();
          if (!trimmed.startsWith('data:')) continue;
          const jsonStr = trimmed.slice(5).trim();
          if (!jsonStr) continue;
          try {
            const data = JSON.parse(jsonStr);
            if (data.token) {
              streamedText += data.token;
              if (typeof marked !== 'undefined') {
                streamObj.textContainer.innerHTML = marked.parse(streamedText);
              } else {
                streamObj.textContainer.textContent = streamedText;
              }
              chatArea.scrollTop = chatArea.scrollHeight;
            }
            if (data.done) {
              if (data.sources) streamSources = data.sources;
              if (data.timestamp) finalTimestamp = data.timestamp;
              if (data.reply && !streamedText) streamedText = data.reply;
            }
          } catch (pe) {
            console.warn('SSE chunk parsing error:', pe);
          }
        }
      }

      finalizeStreamingBotBubble(streamObj, streamedText, finalTimestamp, streamSources, modeForThisQuery);

      const botMsg = {
        type: 'bot',
        reply: streamedText,
        timestamp: finalTimestamp,
        sources: streamSources,
        mode: modeForThisQuery,
        attachment_info: null
      };

      // Save response to thread
      threads[modeForThisQuery].push(botMsg);

      // Sync to active conversation in storage
      if (currentConv) {
        currentConv.messages.push(botMsg);
        currentConv.updatedAt = Date.now();
        saveConversationsToStorage();
        renderHistoryList();
      }
    }

  } catch (err) {
    typingElement.remove();
    const errorMsg = `⚠️ NexaData AI: ${err.message}.`;
    const errObj = {
      type: 'bot',
      reply: errorMsg,
      timestamp: getTimeString(),
      sources: [],
      mode: modeForThisQuery
    };
    threads[modeForThisQuery].push(errObj);
    if (currentConv) {
      currentConv.messages.push(errObj);
      saveConversationsToStorage();
      renderHistoryList();
    }
    if (currentMode === modeForThisQuery) {
      renderBotBubble(errorMsg, getTimeString(), [], modeForThisQuery);
    }
  } finally {
    isSending = false;
    btnSend.disabled = false;
    chatInput.focus();
  }
}

// ----------------------------------------------------
// Bubble Renderers
// ----------------------------------------------------
function renderUserBubble(text, timestamp, attachment = null) {
  const row = document.createElement('div');
  row.className = 'chat-row user';

  const avatar = document.createElement('div');
  avatar.className = 'chat-avatar user';
  avatar.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;

  const body = document.createElement('div');
  body.className = 'chat-body';

  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble';

  if (attachment) {
    if (attachment.isImage && attachment.dataUrl) {
      const img = document.createElement('img');
      img.src = attachment.dataUrl;
      img.className = 'msg-attachment-img';
      img.alt = attachment.name || 'Uploaded Image';
      bubble.appendChild(img);
    } else {
      const pill = document.createElement('div');
      pill.className = 'msg-attachment-pill';
      pill.innerHTML = `
        <span class="msg-file-icon">📎</span>
        <span class="msg-file-name">${escapeHtml(attachment.name || 'File')}</span>
        <span class="msg-file-size">(${escapeHtml(attachment.size || '')})</span>
      `;
      bubble.appendChild(pill);
    }
  }

  if (text) {
    const textNode = document.createElement('div');
    textNode.className = 'msg-text-content';
    textNode.textContent = text;
    bubble.appendChild(textNode);
  }

  const time = document.createElement('div');
  time.className = 'chat-time';
  time.textContent = timestamp;

  body.appendChild(bubble);
  body.appendChild(time);
  row.appendChild(avatar);
  row.appendChild(body);

  chatArea.appendChild(row);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function createStreamingBotBubble(mode) {
  const row = document.createElement('div');
  row.className = 'chat-row bot';

  const avatar = document.createElement('div');
  avatar.className = 'chat-avatar bot';
  avatar.innerHTML = `<img src="/static/icon.png" alt="NexaData" style="width: 22px; height: 22px; object-fit: contain;">`;

  const body = document.createElement('div');
  body.className = 'chat-body';

  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble';

  const textContainer = document.createElement('div');
  textContainer.className = 'streaming-content';
  bubble.appendChild(textContainer);

  const time = document.createElement('div');
  time.className = 'chat-time';
  time.textContent = getTimeString();

  body.appendChild(bubble);
  body.appendChild(time);
  row.appendChild(avatar);
  row.appendChild(body);

  chatArea.appendChild(row);
  chatArea.scrollTop = chatArea.scrollHeight;

  return { row, body, bubble, textContainer, timeEl: time };
}

function finalizeStreamingBotBubble(streamObj, replyMarkdown, timestamp, sources, mode) {
  const { bubble, body, textContainer, timeEl } = streamObj;

  // Render markdown safely
  if (typeof marked !== 'undefined') {
    textContainer.innerHTML = marked.parse(replyMarkdown);
  } else {
    textContainer.textContent = replyMarkdown;
  }

  // Source card for company mode
  if (mode === 'company') {
    const sourceCard = document.createElement('div');
    sourceCard.className = 'source-clean-card';
    
    const docName = (sources && sources.length > 0) ? sources[0].document : 'NexaData_Company_Overview_and_Services.pdf';
    const pageNum = (sources && sources.length > 0) ? `Page ${sources[0].page}` : 'Official Documents';

    sourceCard.innerHTML = `
      <div class="source-clean-left">
        <div class="source-file-icon">📄</div>
        <div class="source-clean-text">
          <h4>Source</h4>
          <p>Based on official NexaData documents (${pageNum})</p>
        </div>
      </div>
      <button class="source-view-btn" onclick="toggleDetails(this)">View sources ›</button>
    `;

    const detailsBox = document.createElement('div');
    detailsBox.style.display = 'none';
    detailsBox.style.marginTop = '8px';
    detailsBox.style.padding = '10px 12px';
    detailsBox.style.background = 'rgba(0,0,0,0.2)';
    detailsBox.style.borderRadius = '8px';
    detailsBox.style.fontSize = '12px';
    detailsBox.style.color = '#94A3B8';
    detailsBox.innerHTML = `<b>Document:</b> <code>${docName}</code><br/><b>Verified Status:</b> Pre-indexed NexaData Knowledge Base`;
    
    sourceCard.appendChild(detailsBox);
    bubble.appendChild(sourceCard);
  }

  // General Mode disclaimer
  if (mode === 'general') {
    const disclaimer = document.createElement('div');
    disclaimer.className = 'general-disclaimer-box';
    disclaimer.innerHTML = `
      <span class="disclaimer-icon">ℹ️</span>
      <div>This is a general information answer, not specific to NexaData's documents. For NexaData's official solutions, please use <b>Company Questions mode</b>.</div>
    `;
    bubble.appendChild(disclaimer);
  }

  // Feedback Action Buttons
  const actions = document.createElement('div');
  actions.className = 'bubble-actions';
  actions.innerHTML = `
    <button class="bubble-act-btn" onclick="copyReply(this)" title="Copy answer">📋</button>
    <button class="bubble-act-btn" onclick="feedback(this, 'like')" title="Helpful">👍</button>
    <button class="bubble-act-btn" onclick="feedback(this, 'dislike')" title="Not helpful">👎</button>
  `;

  timeEl.textContent = timestamp || getTimeString();
  body.insertBefore(actions, timeEl);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function renderBotBubble(replyMarkdown, timestamp, sources, mode) {
  const row = document.createElement('div');
  row.className = 'chat-row bot';

  // Official NexaData Emblem Avatar
  const avatar = document.createElement('div');
  avatar.className = 'chat-avatar bot';
  avatar.innerHTML = `<img src="/static/icon.png" alt="NexaData" style="width: 22px; height: 22px; object-fit: contain;">`;

  const body = document.createElement('div');
  body.className = 'chat-body';

  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble';

  // Render markdown safely
  if (typeof marked !== 'undefined') {
    bubble.innerHTML = marked.parse(replyMarkdown);
  } else {
    bubble.textContent = replyMarkdown;
  }

  // SCREEN 2: Clean Source Card (Company Mode)
  if (mode === 'company') {
    const sourceCard = document.createElement('div');
    sourceCard.className = 'source-clean-card';
    
    const docName = (sources && sources.length > 0) ? sources[0].document : 'NexaData_Company_Overview_and_Services.pdf';
    const pageNum = (sources && sources.length > 0) ? `Page ${sources[0].page}` : 'Official Documents';

    sourceCard.innerHTML = `
      <div class="source-clean-left">
        <div class="source-file-icon">📄</div>
        <div class="source-clean-text">
          <h4>Source</h4>
          <p>Based on official NexaData documents (${pageNum})</p>
        </div>
      </div>
      <button class="source-view-btn" onclick="toggleDetails(this)">View sources ›</button>
    `;

    // Hidden source details
    const detailsBox = document.createElement('div');
    detailsBox.style.display = 'none';
    detailsBox.style.marginTop = '8px';
    detailsBox.style.padding = '10px 12px';
    detailsBox.style.background = 'rgba(0,0,0,0.2)';
    detailsBox.style.borderRadius = '8px';
    detailsBox.style.fontSize = '12px';
    detailsBox.style.color = '#94A3B8';
    detailsBox.innerHTML = `<b>Document:</b> <code>${docName}</code><br/><b>Verified Status:</b> Pre-indexed NexaData Knowledge Base`;
    
    sourceCard.appendChild(detailsBox);
    bubble.appendChild(sourceCard);
  }

  // SCREEN 3: General Information Disclaimer (General Mode)
  if (mode === 'general') {
    const disclaimer = document.createElement('div');
    disclaimer.className = 'general-disclaimer-box';
    disclaimer.innerHTML = `
      <span class="disclaimer-icon">ℹ️</span>
      <div>This is a general information answer, not specific to NexaData's documents. For NexaData's official solutions, please use <b>Company Questions mode</b>.</div>
    `;
    bubble.appendChild(disclaimer);
  }

  // Feedback Action Buttons (Copy, Like, Dislike)
  const actions = document.createElement('div');
  actions.className = 'bubble-actions';
  actions.innerHTML = `
    <button class="bubble-act-btn" onclick="copyReply(this)" title="Copy answer">📋</button>
    <button class="bubble-act-btn" onclick="feedback(this, 'like')" title="Helpful">👍</button>
    <button class="bubble-act-btn" onclick="feedback(this, 'dislike')" title="Not helpful">👎</button>
  `;

  const time = document.createElement('div');
  time.className = 'chat-time';
  time.textContent = timestamp;

  body.appendChild(bubble);
  body.appendChild(actions);
  body.appendChild(time);
  row.appendChild(avatar);
  row.appendChild(body);

  chatArea.appendChild(row);
  chatArea.scrollTop = chatArea.scrollHeight;
}

function toggleDetails(btn) {
  const card = btn.closest('.source-clean-card');
  const details = card.querySelector('div[style*="display"]');
  if (details) {
    const isHidden = details.style.display === 'none';
    details.style.display = isHidden ? 'block' : 'none';
    btn.textContent = isHidden ? 'Hide sources ‹' : 'View sources ›';
  }
}

function copyReply(btn) {
  const bubble = btn.closest('.chat-body').querySelector('.chat-bubble');
  navigator.clipboard.writeText(bubble.innerText);
  btn.textContent = '✅';
  setTimeout(() => { btn.textContent = '📋'; }, 1500);
}

function feedback(btn, type) {
  btn.style.color = type === 'like' ? '#10B981' : '#EF4444';
}

function appendTypingIndicator() {
  const row = document.createElement('div');
  row.className = 'chat-row bot';
  row.innerHTML = `
    <div class="chat-avatar bot"><img src="/static/icon.png" alt="NexaData" style="width: 22px; height: 22px; object-fit: contain;"></div>
    <div class="chat-body">
      <div class="chat-bubble typing-dots">
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
        <span class="typing-dot"></span>
      </div>
    </div>
  `;
  chatArea.appendChild(row);
  chatArea.scrollTop = chatArea.scrollHeight;
  return row;
}

// ----------------------------------------------------
// Options & Dropdowns
// ----------------------------------------------------
function toggleHistoryMenu(btn) {
  const item = btn.closest('.history-item');
  const dropdown = item.querySelector('.history-dropdown');
  document.querySelectorAll('.history-dropdown').forEach(d => {
    if (d !== dropdown) d.classList.remove('active');
  });
  dropdown.classList.toggle('active');
}

document.addEventListener('click', (e) => {
  if (!e.target.closest('.history-item-right') && !e.target.closest('.history-dropdown')) {
    document.querySelectorAll('.history-dropdown').forEach(d => d.classList.remove('active'));
  }
});

// Mobile Drawer
function toggleSidebar() {
  sidebar.classList.toggle('mobile-open');
  if (sidebarOverlay) {
    sidebarOverlay.classList.toggle('active', sidebar.classList.contains('mobile-open'));
  }
}

function closeSidebar() {
  sidebar.classList.remove('mobile-open');
  if (sidebarOverlay) {
    sidebarOverlay.classList.remove('active');
  }
}

// ----------------------------------------------------
// PDF Export for Active Conversation
// ----------------------------------------------------
async function exportCurrentChatPdf() {
  const activeThread = threads[currentMode] || [];
  if (activeThread.length === 0) {
    alert("The current conversation is empty. Please ask a question before exporting to PDF.");
    return;
  }

  const exportBtns = [
    document.getElementById('btnExportPdf'),
    document.getElementById('btnTopNavExport')
  ].filter(Boolean);

  const originalStates = exportBtns.map(b => ({ btn: b, html: b.innerHTML }));
  exportBtns.forEach(b => {
    b.disabled = true;
    b.innerHTML = '<span style="display:flex;align-items:center;gap:6px;">⏳ <span class="export-btn-text">Preparing...</span></span>';
  });

  try {
    let title = "NexaData Conversation";
    if (activeConvId) {
      const active = conversations.find(c => c.id === activeConvId);
      if (active && active.title) title = active.title;
    } else if (activeThread.length > 0) {
      const firstUser = activeThread.find(m => m.type === 'user');
      if (firstUser && firstUser.text) {
        title = firstUser.text.slice(0, 35);
      }
    }

    const payload = {
      title: title,
      mode: currentMode,
      messages: activeThread,
      export_time: new Date().toLocaleString()
    };

    const res = await fetch('/api/export-pdf', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    });

    if (!res.ok) {
      throw new Error(`Server returned status ${res.status}`);
    }

    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const downloadAnchor = document.createElement('a');
    downloadAnchor.href = url;
    downloadAnchor.download = `NexaData_${title.replace(/[^a-zA-Z0-9_-]/g, '_')}.pdf`;
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    document.body.removeChild(downloadAnchor);
    window.URL.revokeObjectURL(url);
    closeSidebar();
  } catch (err) {
    console.error('Error exporting PDF:', err);
    alert('Could not export conversation PDF. Please check server logs and try again.');
  } finally {
    originalStates.forEach(item => {
      item.btn.disabled = false;
      item.btn.innerHTML = item.html;
    });
  }
}

// Initialize on Load
btnNewChat.addEventListener('click', startNewConversation);

document.addEventListener('DOMContentLoaded', () => {
  updateModePillsUI();
  initTheme();
  loadSavedConversations();
  renderHistoryList();

  // If active conversation was saved, load it; else show fresh thread
  if (activeConvId) {
    const active = conversations.find(c => c.id === activeConvId);
    if (active) {
      openConversation(activeConvId);
    } else {
      renderActiveThread();
    }
  } else {
    renderActiveThread();
  }

  chatInput.focus();
});

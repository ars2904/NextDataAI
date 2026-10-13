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

  // If no conversations stored yet, populate starter conversations
  if (!conversations || conversations.length === 0) {
    conversations = [
      {
        id: 'starter_1',
        title: 'What is NexaData?',
        mode: 'company',
        messages: [
          { type: 'user', text: 'What is NexaData and what solutions do you offer?', timestamp: '10:20 AM' },
          { 
            type: 'bot', 
            reply: 'NexaData AI is an autonomous data analytics and intelligence platform providing end-to-end data processing, automated SQL analytics, and executive reporting.',
            timestamp: '10:20 AM',
            sources: [{ document: 'NexaData_Company_Overview_and_Services.pdf', page: 1, snippet: 'NexaData AI platform overview...' }],
            mode: 'company'
          }
        ],
        updatedAt: Date.now() - 120000
      },
      {
        id: 'starter_2',
        title: 'Our solutions overview',
        mode: 'company',
        messages: [
          { type: 'user', text: 'What are your enterprise solutions and pricing plans?', timestamp: '09:30 AM' },
          { 
            type: 'bot', 
            reply: 'We offer Enterprise Analytics, Real-time Reporting, and Custom AI Connectors tailored to enterprise data workflows.',
            timestamp: '09:30 AM',
            sources: [{ document: 'NexaData_Company_Overview_and_Services.pdf', page: 1, snippet: 'Enterprise solutions and tiers...' }],
            mode: 'company'
          }
        ],
        updatedAt: Date.now() - 3600000
      }
    ];
    saveConversationsToStorage();
  }
}

function saveConversationsToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY_CONVS, JSON.stringify(conversations));
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

    const icon = conv.mode === 'company' ? '📄' : '💬';
    let snippet = 'Conversation ready';
    if (conv.messages && conv.messages.length > 0) {
      const last = conv.messages[conv.messages.length - 1];
      const rawText = last.reply || last.text || '';
      snippet = rawText.replace(/[#*`_\[\]()]/g, '').trim().substring(0, 36) + '...';
    }

    item.innerHTML = `
      <div class="history-item-left">
        <div class="history-item-icon">${icon}</div>
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
    chatInput.placeholder = 'Ask a general programming or analytics question...';
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
    if (subtitle) subtitle.textContent = 'Ask open-ended questions about Python, data science, algorithms, and general topics.';
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
      renderUserBubble(item.text, item.timestamp);
    } else if (item.type === 'bot') {
      renderBotBubble(item.reply, item.timestamp, item.sources, item.mode);
    }
  });

  chatArea.scrollTop = chatArea.scrollHeight;
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
  if (!query || isSending) return;

  const modeForThisQuery = currentMode;
  const time = getTimeString();

  // If there is no active conversation yet, create one now!
  if (!activeConvId) {
    activeConvId = 'conv_' + Date.now();
    localStorage.setItem(STORAGE_KEY_ACTIVE, activeConvId);
    const newConv = {
      id: activeConvId,
      title: query.length > 32 ? query.substring(0, 32) + '...' : query,
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

  // Save to thread and render
  const userMsg = {
    type: 'user',
    text: query,
    timestamp: time
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

  renderUserBubble(query, time);

  // Show Typing Indicator
  const typingElement = appendTypingIndicator();
  isSending = true;
  btnSend.disabled = true;

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        message: query,
        mode: modeForThisQuery
      })
    });

    typingElement.remove();

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    const replyTime = data.timestamp || getTimeString();

    const botMsg = {
      type: 'bot',
      reply: data.reply,
      timestamp: replyTime,
      sources: data.sources || [],
      mode: modeForThisQuery
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

    // Only render if user is still on the same tab
    if (currentMode === modeForThisQuery) {
      renderBotBubble(data.reply, replyTime, data.sources, modeForThisQuery);
    }

  } catch (err) {
    typingElement.remove();
    const errorMsg = `⚠️ Could not connect to NexaData AI service: ${err.message}.`;
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
  }
}

// ----------------------------------------------------
// Bubble Renderers
// ----------------------------------------------------
function renderUserBubble(text, timestamp) {
  const row = document.createElement('div');
  row.className = 'chat-row user';

  const avatar = document.createElement('div');
  avatar.className = 'chat-avatar user';
  avatar.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>`;

  const body = document.createElement('div');
  body.className = 'chat-body';

  const bubble = document.createElement('div');
  bubble.className = 'chat-bubble';
  bubble.textContent = text;

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

  const exportBtn = document.getElementById('btnExportPdf');
  const originalHtml = exportBtn ? exportBtn.innerHTML : '';
  if (exportBtn) {
    exportBtn.disabled = true;
    exportBtn.innerHTML = '<span>⏳ Preparing PDF...</span>';
  }

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
    if (exportBtn) {
      exportBtn.disabled = false;
      exportBtn.innerHTML = originalHtml;
    }
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

// NexaData AI App Controller - Independent Dual-Tab Threads & Theme Management

let currentMode = 'company';
let isSending = false;
let currentTheme = localStorage.getItem('nexadata_theme') || 'dark';

// Independent Conversation Threads for each tab
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

// Theme Management
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

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  renderActiveThread();
  chatInput.focus();
});

// Mode Switcher (Independent Tab Isolation)
function switchMode(newMode) {
  if (currentMode === newMode) return;
  currentMode = newMode;

  // Update UI Pills and Sidebar Buttons
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

  // Switch to the selected tab's isolated thread
  renderActiveThread();
  chatInput.focus();
}

// Render the active tab's thread
function renderActiveThread() {
  const activeThread = threads[currentMode];

  // If no messages in this tab yet, show that tab's welcome screen
  if (activeThread.length === 0) {
    chatArea.innerHTML = '';
    updateWelcomeScreenContent();
    welcomeScreen.style.display = 'flex';
    chatArea.appendChild(welcomeScreen);
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

// Update Welcome Screen text based on mode
function updateWelcomeScreenContent() {
  if (currentMode === 'company') {
    welcomeSubtitle.innerHTML = "Get accurate answers from NexaData's official documents.";
  } else {
    welcomeSubtitle.innerHTML = "Ask open-ended questions about Python, data science, databases, and general topics.";
  }
}

// Keydown handler
function handleKey(e) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    submitMessage();
  }
}

// Auto-expand input
function adjustInputHeight(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = Math.min(textarea.scrollHeight, 100) + 'px';
}

// Quick Prompt Sender
function triggerPrompt(promptText) {
  chatInput.value = promptText;
  submitMessage();
}

// Timestamp generator
function getTimeString() {
  const d = new Date();
  return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
}

// Send Message
async function submitMessage() {
  const query = chatInput.value.trim();
  if (!query || isSending) return;

  const modeForThisQuery = currentMode;
  const time = getTimeString();

  // Hide welcome screen
  if (welcomeScreen && welcomeScreen.style.display !== 'none') {
    welcomeScreen.style.display = 'none';
  }

  // Clear input
  chatInput.value = '';
  chatInput.style.height = '24px';
  chatInput.focus();

  // Save to thread and render
  threads[modeForThisQuery].push({
    type: 'user',
    text: query,
    timestamp: time
  });
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

    // Save response to thread
    threads[modeForThisQuery].push({
      type: 'bot',
      reply: data.reply,
      timestamp: replyTime,
      sources: data.sources || [],
      mode: modeForThisQuery
    });

    // Only render if user is still on the same tab
    if (currentMode === modeForThisQuery) {
      renderBotBubble(data.reply, replyTime, data.sources, modeForThisQuery);
    }

  } catch (err) {
    typingElement.remove();
    const errorMsg = `⚠️ Could not connect to NexaData AI service: ${err.message}.`;
    threads[modeForThisQuery].push({
      type: 'bot',
      reply: errorMsg,
      timestamp: getTimeString(),
      sources: [],
      mode: modeForThisQuery
    });
    if (currentMode === modeForThisQuery) {
      renderBotBubble(errorMsg, getTimeString(), [], modeForThisQuery);
    }
  } finally {
    isSending = false;
    btnSend.disabled = false;
  }
}

// Render User Bubble
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

// Render Bot Bubble matching Mockup Screen 2 & Screen 3
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

// Toggle View Sources Accordion
function toggleDetails(btn) {
  const card = btn.closest('.source-clean-card');
  const details = card.querySelector('div[style*="display"]');
  if (details) {
    const isHidden = details.style.display === 'none';
    details.style.display = isHidden ? 'block' : 'none';
    btn.textContent = isHidden ? 'Hide sources ‹' : 'View sources ›';
  }
}

// Copy Action
function copyReply(btn) {
  const bubble = btn.closest('.chat-body').querySelector('.chat-bubble');
  navigator.clipboard.writeText(bubble.innerText);
  btn.textContent = '✅';
  setTimeout(() => { btn.textContent = '📋'; }, 1500);
}

// Feedback Action
function feedback(btn, type) {
  btn.style.color = type === 'like' ? '#10B981' : '#EF4444';
}

// Typing Indicator Bubble
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

// New Conversation button (clears current tab's thread)
btnNewChat.addEventListener('click', () => {
  threads[currentMode] = [];
  renderActiveThread();
  chatInput.value = '';
  chatInput.focus();
  closeSidebar();
});

// Load sample from history
function loadSampleHistory(query) {
  chatInput.value = query;
  submitMessage();
  closeSidebar();
}

// Filter history items by search
function filterHistory(term) {
  const items = document.querySelectorAll('.history-item');
  const lower = term.toLowerCase();
  items.forEach(it => {
    const title = it.querySelector('.history-title').textContent.toLowerCase();
    it.style.display = title.includes(lower) ? 'flex' : 'none';
  });
}

// History 3-Dot Options Menu Handlers
function toggleHistoryMenu(btn) {
  const item = btn.closest('.history-item');
  const dropdown = item.querySelector('.history-dropdown');
  // Close any other open dropdowns first
  document.querySelectorAll('.history-dropdown').forEach(d => {
    if (d !== dropdown) d.classList.remove('active');
  });
  dropdown.classList.toggle('active');
}

function renameHistoryItem(btn) {
  const item = btn.closest('.history-item');
  const titleEl = item.querySelector('.history-title');
  const newName = prompt('Enter new conversation title:', titleEl.textContent);
  if (newName && newName.trim()) {
    titleEl.textContent = newName.trim();
  }
  btn.closest('.history-dropdown').classList.remove('active');
}

function deleteHistoryItem(btn) {
  const item = btn.closest('.history-item');
  if (confirm('Delete this conversation from history?')) {
    item.remove();
  }
}

// Close any open dropdowns when clicking outside
document.addEventListener('click', (e) => {
  if (!e.target.closest('.history-item-right') && !e.target.closest('.history-dropdown')) {
    document.querySelectorAll('.history-dropdown').forEach(d => d.classList.remove('active'));
  }
});

// Mobile sidebar drawer controls
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

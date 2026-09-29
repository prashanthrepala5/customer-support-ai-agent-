def get_global_css() -> str:
    return """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Reset & Base ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
    --bg-main: #0B0E14;
    --bg-panel: #11141D;
    --bg-card: #161A23;
    --text-primary: #E2E8F0;
    --text-secondary: #8B949E;
    --accent-blue: #3B82F6;
    --accent-indigo: #6366F1;
    --success-green: #22C55E;
    --warn-amber: #F59E0B;
    --border-color: rgba(255, 255, 255, 0.06);
    --border-highlight: rgba(99, 102, 241, 0.3);
}

html, body, [data-testid="stAppViewContainer"], .stApp {
    background: var(--bg-main) !important;
    font-family: 'Inter', sans-serif !important;
    color: var(--text-primary) !important;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header, [data-testid="collapsedControl"], [data-testid="stSidebarNav"] { display: none !important; }

/* Main layout padding */
[data-testid="stAppViewContainer"] > .main > .block-container {
    padding: 0 16px !important;
    max-width: 100% !important;
}

/* ── Top Navigation Bar ── */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 24px;
    height: 54px;
    background: var(--bg-panel);
    border-bottom: 1px solid var(--border-color);
    position: sticky;
    top: 0;
    z-index: 100;
    margin: 0 -16px 20px -16px;
    font-size: 0.85rem;
}
.topbar-brand { display: flex; align-items: center; gap: 12px; }
.topbar-name { font-size: 1.1rem; font-weight: 600; color: #FFF; }
.topbar-status {
    display: flex; align-items: center; gap: 16px;
}
.status-badge {
    display: flex; align-items: center; gap: 6px;
    font-size: 0.75rem; color: var(--text-secondary);
    padding: 4px 10px; background: rgba(255,255,255,0.02);
    border: 1px solid var(--border-color); border-radius: 6px;
    font-family: 'JetBrains Mono', monospace;
}
.dot { width: 6px; height: 6px; border-radius: 50%; }
.dot.green { background: var(--success-green); box-shadow: 0 0 8px var(--success-green); }
.dot.blue { background: var(--accent-indigo); box-shadow: 0 0 8px var(--accent-indigo); }

/* ── Customer/Profile Cards ── */
.customer-card {
    padding: 10px 12px; border-radius: 6px;
    border: 1px solid transparent;
    background: transparent;
    margin-bottom: 4px; transition: all 0.2s ease;
}
.customer-card:hover { background: rgba(255,255,255,0.03); }
.customer-card.active {
    border: 1px solid var(--border-highlight);
    background: rgba(99,102,241,0.05);
}
.customer-avatar {
    width: 32px; height: 32px; border-radius: 4px;
    display: flex; align-items: center; justify-content: center;
    font-weight: 600; font-size: 0.8rem; color: #FFF;
    background: var(--bg-card);
    border: 1px solid var(--border-color);
}
.customer-name { font-size: 0.85rem; font-weight: 500; color: var(--text-primary); }
.customer-role { font-size: 0.7rem; color: var(--text-secondary); font-family: 'JetBrains Mono', monospace; }

/* ── Memory Panel ── */
.memory-panel {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 16px;
    margin-bottom: 16px;
}
.memory-header {
    font-size: 0.85rem; font-weight: 600; color: var(--text-primary);
    display: flex; align-items: center; gap: 8px; margin-bottom: 12px;
}
.left-panel-container {
    max-height: calc(100vh - 120px);
    overflow-y: auto;
    padding-right: 8px;
}
.left-panel-container::-webkit-scrollbar { width: 4px; }
.left-panel-container::-webkit-scrollbar-thumb { background: rgba(255, 255, 255, 0.1); border-radius: 4px; }

.memory-scroll-container {
    max-height: calc(100vh - 380px);
    overflow-y: auto;
    padding-right: 12px;
}
/* Custom Scrollbar for memory panel */
.memory-scroll-container::-webkit-scrollbar {
    width: 6px;
}
.memory-scroll-container::-webkit-scrollbar-track {
    background: transparent; 
}
.memory-scroll-container::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.1); 
    border-radius: 4px;
}
.memory-scroll-container::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.2); 
}

.memory-card {
    background: rgba(255,255,255,0.02);
    border: 1px solid var(--border-color);
    padding: 10px; border-radius: 6px;
    margin-bottom: 8px; font-size: 0.75rem; color: var(--text-primary);
}
.memory-tag {
    font-size: 0.6rem; padding: 2px 6px; border-radius: 4px;
    background: rgba(99,102,241,0.15); color: #818CF8;
    margin-bottom: 6px; display: inline-block; font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Chat Messages ── */
.chat-container {
    background: var(--bg-card);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    padding: 20px;
}
.chat-message-bubble {
    font-size: 0.85rem; line-height: 1.5;
}
.memory-recalled-indicator {
    font-size: 0.7rem; color: var(--success-green);
    display: flex; align-items: center; gap: 6px;
    margin-bottom: 8px; font-weight: 500;
    font-family: 'JetBrains Mono', monospace;
}

/* ── Form Inputs & Buttons ── */
.stButton > button {
    border-radius: 6px !important; font-weight: 500 !important;
    transition: all 0.2s ease !important;
    font-size: 0.8rem !important;
}
.stButton > button[kind="primary"] {
    background: var(--accent-indigo) !important;
    border: 1px solid var(--accent-indigo) !important; color: white !important;
}
.stButton > button[kind="secondary"] {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid var(--border-color) !important; color: var(--text-primary) !important;
}

[data-testid="stChatInput"] > div {
    background: var(--bg-panel) !important;
    border: 1px solid var(--border-color) !important;
    border-radius: 6px !important;
}
</style>
"""

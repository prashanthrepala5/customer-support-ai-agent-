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
.topbar-brand { display: flex; align-items: center; gap: 14px; cursor: pointer; }
.topbar-logo {
    font-size: 1.6rem;
    color: var(--accent-indigo);
    text-shadow: 0 0 12px rgba(99, 102, 241, 0.6);
    display: flex; align-items: center; justify-content: center;
}
.topbar-name { 
    font-size: 1.4rem; 
    font-weight: 700; 
    letter-spacing: -0.02em;
    background: linear-gradient(135deg, #FFF, #A5B4FC);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
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

/* ── Login Page – Pixel-Perfect High-Fidelity SaaS Theme ── */

/* Constellation & Glowing Orbs Background */
.login-page-bg {
    position: fixed;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    z-index: 0;
    pointer-events: none;
    overflow: hidden;
    background: #060913;
}
.login-page-bg::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background:
        radial-gradient(circle 520px at 0% 0%, rgba(37, 99, 235, 0.28) 0%, rgba(30, 58, 138, 0.1) 45%, transparent 70%),
        radial-gradient(circle 650px at 100% 100%, rgba(139, 92, 246, 0.38) 0%, rgba(99, 102, 241, 0.18) 35%, rgba(67, 56, 202, 0.08) 55%, transparent 70%),
        radial-gradient(circle 350px at 0% 100%, rgba(29, 78, 216, 0.18) 0%, transparent 60%);
}
.login-constellation-svg {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    object-fit: cover;
}

/* Center card vertically and horizontally when login form is present */
[data-testid="stAppViewContainer"]:has(form[data-testid="stForm"]) > .main > .block-container {
    min-height: 100vh !important;
    display: flex !important;
    flex-direction: column !important;
    justify-content: center !important;
    align-items: center !important;
    padding-top: 2rem !important;
    padding-bottom: 2rem !important;
}

/* Glassmorphism Login Card (The Form itself) */
form[data-testid="stForm"] {
    position: relative !important;
    z-index: 10 !important;
    max-width: 420px !important;
    width: 100% !important;
    margin: 40px auto !important;
    padding: 38px 34px 34px 34px !important;
    background: rgba(13, 20, 42, 0.72) !important;
    backdrop-filter: blur(28px) saturate(160%) !important;
    -webkit-backdrop-filter: blur(28px) saturate(160%) !important;
    border: 1px solid rgba(56, 90, 160, 0.32) !important;
    border-radius: 20px !important;
    box-shadow: 0 25px 60px -10px rgba(0, 0, 0, 0.8), 0 0 50px rgba(24, 40, 85, 0.25), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}

/* Brand Header */
.login-brand-header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    margin-bottom: 2px;
}
.login-brand-logo {
    display: flex;
    align-items: center;
    justify-content: center;
}
.login-brand-name {
    font-size: 30px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.02em;
    font-family: 'Inter', -apple-system, sans-serif;
}
.login-card-title {
    font-size: 20px;
    font-weight: 600;
    color: #FFFFFF;
    text-align: center;
    margin-top: 14px;
    margin-bottom: 6px;
    font-family: 'Inter', -apple-system, sans-serif;
}
.login-card-subtitle {
    font-size: 13px;
    font-weight: 400;
    color: #7E8DA6;
    text-align: center;
    margin-bottom: 24px;
    font-family: 'Inter', -apple-system, sans-serif;
}

/* Hide Streamlit input labels */
form[data-testid="stForm"] [data-testid="stTextInput"] label {
    display: none !important;
}

/* BaseWeb container */
form[data-testid="stForm"] [data-baseweb="input"] {
    background: transparent !important;
    border: none !important;
    padding: 0 !important;
}
form[data-testid="stForm"] [data-baseweb="base-input"] {
    background: rgba(14, 22, 45, 0.8) !important;
    border: 1px solid rgba(65, 88, 140, 0.35) !important;
    border-radius: 10px !important;
    height: 48px !important;
    box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.3) !important;
    transition: all 0.2s ease !important;
}
form[data-testid="stForm"] [data-baseweb="base-input"]:focus-within {
    border-color: rgba(99, 102, 241, 0.65) !important;
    box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.22), 0 0 14px rgba(59, 130, 246, 0.18) !important;
}

/* Inputs styling */
form[data-testid="stForm"] input {
    background-color: transparent !important;
    color: #FFFFFF !important;
    font-size: 14px !important;
    height: 48px !important;
    border: none !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}
form[data-testid="stForm"] input::placeholder {
    color: #556885 !important;
    font-size: 14px !important;
}

/* Username input: Mail icon */
form[data-testid="stForm"] input[type="text"] {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%23627594' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='2' y='4' width='20' height='16' rx='2'/%3E%3Cpath d='m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7'/%3E%3C/svg%3E") !important;
    background-position: 15px center !important;
    background-repeat: no-repeat !important;
    background-size: 18px 18px !important;
    padding-left: 44px !important;
    padding-right: 16px !important;
}

/* Password inputs: Lock icon on left, Eye icon on right */
form[data-testid="stForm"] input[type="password"] {
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%23627594' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2' ry='2'/%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'/%3E%3C/svg%3E"),
                     url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='18' height='18' viewBox='0 0 24 24' fill='none' stroke='%23627594' stroke-width='1.8' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z'/%3E%3Ccircle cx='12' cy='12' r='3'/%3E%3C/svg%3E") !important;
    background-position: 15px center, calc(100% - 15px) center !important;
    background-repeat: no-repeat, no-repeat !important;
    background-size: 18px 18px, 18px 18px !important;
    padding-left: 44px !important;
    padding-right: 44px !important;
}

/* Input container vertical spacing */
form[data-testid="stForm"] [data-testid="stTextInput"] {
    margin-bottom: 8px !important;
}

/* Submit Button: Orange-Coral-Pink Gradient */
form[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button {
    width: 100% !important;
    height: 48px !important;
    background: linear-gradient(90deg, #FF6A3D 0%, #FA5165 48%, #F43F8B 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    color: #FFFFFF !important;
    font-size: 15px !important;
    font-weight: 600 !important;
    letter-spacing: 0.01em !important;
    box-shadow: 0 4px 20px rgba(255, 106, 61, 0.42), 0 2px 10px rgba(244, 63, 139, 0.28) !important;
    transition: all 0.25s ease !important;
    margin-top: 10px !important;
    cursor: pointer !important;
    font-family: 'Inter', -apple-system, sans-serif !important;
}
form[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button:hover {
    box-shadow: 0 6px 28px rgba(255, 106, 61, 0.55), 0 3px 14px rgba(244, 63, 139, 0.42) !important;
    transform: translateY(-1px) !important;
    filter: brightness(1.04) !important;
}
form[data-testid="stForm"] [data-testid="stFormSubmitButton"] > button:active {
    transform: translateY(1px) !important;
    box-shadow: 0 2px 8px rgba(255, 106, 61, 0.4) !important;
}

/* Forgot Password Link */
.login-forgot-pwd {
    text-align: right;
    margin-top: 10px;
    margin-bottom: 14px;
}
.login-forgot-pwd a {
    color: #55729F;
    font-size: 12.5px;
    text-decoration: none;
    transition: color 0.2s ease;
    font-family: 'Inter', sans-serif;
}
.login-forgot-pwd a:hover {
    color: #7B9ED4;
    text-decoration: underline;
}

/* Divider & Auth Switch Row */
.login-auth-switch-row {
    display: flex;
    align-items: center;
    justify-content: center;
    margin-top: 18px;
    margin-bottom: 4px;
    gap: 12px;
}
.login-auth-switch-line {
    flex: 1;
    height: 1px;
    background: rgba(75, 95, 145, 0.22);
}
.login-auth-switch-content {
    font-size: 13px;
    color: #556B8B;
    white-space: nowrap;
    font-family: 'Inter', sans-serif;
}
.login-auth-switch-content a {
    color: #3B82F6;
    font-weight: 600;
    text-decoration: none;
    margin-left: 4px;
    transition: color 0.2s ease;
}
.login-auth-switch-content a:hover {
    color: #60A5FA;
    text-decoration: underline;
}

/* Error messages */
.login-error {
    color: #F87171;
    font-size: 13px;
    text-align: center;
    margin-top: 10px;
    padding: 10px 14px;
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.25);
    border-radius: 8px;
    font-family: 'Inter', sans-serif;
}
</style>
"""


def get_login_background_html() -> str:
    """Returns the SVG background with constellations and glowing orbs exactly as in the design."""
    return """
<div class="login-page-bg">
    <svg class="login-constellation-svg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" xmlns="http://www.w3.org/2000/svg">
        <defs>
            <filter id="cyanGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="3.5" result="blur"/>
                <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <filter id="purpleGlow" x="-50%" y="-50%" width="200%" height="200%">
                <feGaussianBlur stdDeviation="3.5" result="blur"/>
                <feMerge>
                    <feMergeNode in="blur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
            <linearGradient id="leftArcGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#3b82f6" stop-opacity="0.32"/>
                <stop offset="100%" stop-color="#1d4ed8" stop-opacity="0.04"/>
            </linearGradient>
            <linearGradient id="rightArcGrad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#8b5cf6" stop-opacity="0.4"/>
                <stop offset="100%" stop-color="#4c1d95" stop-opacity="0.08"/>
            </linearGradient>
        </defs>

        <!-- Top Left & Bottom Right Curved Orbs -->
        <circle cx="50" cy="50" r="280" fill="url(#leftArcGrad)" filter="blur(40px)"/>
        <circle cx="1380" cy="850" r="380" fill="url(#rightArcGrad)" filter="blur(35px)"/>
        <path d="M 960 900 Q 1200 640 1440 680" fill="none" stroke="rgba(139, 92, 246, 0.22)" stroke-width="1.8"/>
        <path d="M 1040 900 Q 1260 720 1440 750" fill="none" stroke="rgba(99, 102, 241, 0.3)" stroke-width="1.2"/>

        <!-- LEFT CONSTELLATION -->
        <g stroke="rgba(56, 189, 248, 0.2)" stroke-width="1">
            <line x1="90" y1="360" x2="170" y2="490"/>
            <line x1="170" y1="490" x2="100" y2="660"/>
            <line x1="100" y1="660" x2="230" y2="750"/>
            <line x1="170" y1="490" x2="230" y2="750"/>
            <line x1="170" y1="490" x2="300" y2="420"/>
            <line x1="90" y1="360" x2="200" y2="340"/>
            <line x1="200" y1="340" x2="300" y2="420"/>
            <line x1="170" y1="490" x2="225" y2="600"/>
            <line x1="225" y1="600" x2="230" y2="750"/>
        </g>
        <circle cx="90" cy="360" r="3.5" fill="#38BDF8" filter="url(#cyanGlow)"/>
        <circle cx="90" cy="360" r="8" fill="rgba(56, 189, 248, 0.22)"/>
        <circle cx="170" cy="490" r="4.5" fill="#38BDF8" filter="url(#cyanGlow)"/>
        <circle cx="170" cy="490" r="10" fill="rgba(56, 189, 248, 0.28)"/>
        <circle cx="100" cy="660" r="3.5" fill="#38BDF8" filter="url(#cyanGlow)"/>
        <circle cx="100" cy="660" r="7" fill="rgba(56, 189, 248, 0.22)"/>
        <circle cx="230" cy="750" r="4" fill="#38BDF8" filter="url(#cyanGlow)"/>
        <circle cx="230" cy="750" r="9" fill="rgba(56, 189, 248, 0.25)"/>
        <circle cx="200" cy="340" r="3" fill="#38BDF8" filter="url(#cyanGlow)"/>
        <circle cx="300" cy="420" r="3.5" fill="#38BDF8" filter="url(#cyanGlow)"/>
        <circle cx="225" cy="600" r="3" fill="#60A5FA"/>
        <circle cx="310" cy="235" r="2" fill="#38BDF8" opacity="0.8"/>
        <circle cx="22" cy="450" r="2" fill="#38BDF8" opacity="0.6"/>

        <!-- RIGHT CONSTELLATION -->
        <g stroke="rgba(168, 85, 247, 0.2)" stroke-width="1">
            <line x1="1280" y1="120" x2="1390" y2="160"/>
            <line x1="1280" y1="120" x2="1350" y2="250"/>
            <line x1="1350" y1="250" x2="1390" y2="160"/>
            <line x1="1160" y1="305" x2="1350" y2="250"/>
            <line x1="1350" y1="250" x2="1310" y2="460"/>
            <line x1="1160" y1="305" x2="1310" y2="460"/>
        </g>
        <circle cx="1280" cy="120" r="4.5" fill="#60A5FA" filter="url(#cyanGlow)"/>
        <circle cx="1280" cy="120" r="10" fill="rgba(96, 165, 250, 0.28)"/>
        <circle cx="1390" cy="160" r="3.5" fill="#818CF8" filter="url(#purpleGlow)"/>
        <circle cx="1350" cy="250" r="4" fill="#60A5FA" filter="url(#cyanGlow)"/>
        <circle cx="1350" cy="250" r="9" fill="rgba(96, 165, 250, 0.24)"/>
        <circle cx="1160" cy="305" r="3.5" fill="#A855F7" filter="url(#purpleGlow)"/>
        <circle cx="1160" cy="305" r="8" fill="rgba(168, 85, 247, 0.25)"/>
        <circle cx="1310" cy="460" r="4" fill="#38BDF8" filter="url(#cyanGlow)"/>
        <circle cx="1310" cy="460" r="9" fill="rgba(56, 189, 248, 0.25)"/>
        <circle cx="1145" cy="105" r="2.5" fill="#60A5FA" opacity="0.7"/>
        <circle cx="1400" cy="390" r="2" fill="#A855F7" opacity="0.6"/>
    </svg>
</div>
"""


def get_login_card_header_html(mode: str = "login") -> str:
    """Returns the diamond logo and titles matching the reference design."""
    title = "SupportAI Copilot" if mode == "login" else "Create Account"
    subtitle = "AI Support Agent with Long-Term Memory" if mode == "login" else "Join Helixa with Long-Term Memory Support"
    return f"""
<div class="login-brand-header">
    <div class="login-brand-logo">
        <svg width="40" height="40" viewBox="0 0 44 44" fill="none" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <linearGradient id="tileTop" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#38BDF8"/>
              <stop offset="100%" stop-color="#22D3EE"/>
            </linearGradient>
            <linearGradient id="tileLeft" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#38BDF8"/>
              <stop offset="100%" stop-color="#3B82F6"/>
            </linearGradient>
            <linearGradient id="tileRight" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#60A5FA"/>
              <stop offset="100%" stop-color="#6366F1"/>
            </linearGradient>
            <linearGradient id="tileBottom" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stop-color="#4F46E5"/>
              <stop offset="100%" stop-color="#818CF8"/>
            </linearGradient>
          </defs>
          <rect x="17.25" y="5.75" width="9.5" height="9.5" rx="2.2" transform="rotate(45 22 10.5)" fill="url(#tileTop)"/>
          <rect x="5.75" y="17.25" width="9.5" height="9.5" rx="2.2" transform="rotate(45 10.5 22)" fill="url(#tileLeft)"/>
          <rect x="28.75" y="17.25" width="9.5" height="9.5" rx="2.2" transform="rotate(45 33.5 22)" fill="url(#tileRight)"/>
          <rect x="17.25" y="28.75" width="9.5" height="9.5" rx="2.2" transform="rotate(45 22 33.5)" fill="url(#tileBottom)"/>
        </svg>
    </div>
    <div class="login-brand-name">Helixa</div>
</div>
<div class="login-card-title">{title}</div>
<div class="login-card-subtitle">{subtitle}</div>
"""


def get_login_card_footer_html(mode: str = "login") -> str:
    """Returns the Forgot Password link and the mode switch divider row."""
    if mode == "login":
        return """
<div class="login-forgot-pwd">
    <a href="#" onclick="alert('Demo credentials:\\nUser: maya.chen or alex.rivera\\nPassword: demo123'); return false;">Forgot password?</a>
</div>
<div class="login-auth-switch-row">
    <div class="login-auth-switch-line"></div>
    <div class="login-auth-switch-content">
        Don't have an account? <a href="?auth_mode=signup" target="_self">Sign up</a>
    </div>
    <div class="login-auth-switch-line"></div>
</div>
"""
    else:
        return """
<div class="login-auth-switch-row" style="margin-top: 22px;">
    <div class="login-auth-switch-line"></div>
    <div class="login-auth-switch-content">
        Already have an account? <a href="?auth_mode=login" target="_self">Sign in</a>
    </div>
    <div class="login-auth-switch-line"></div>
</div>
"""


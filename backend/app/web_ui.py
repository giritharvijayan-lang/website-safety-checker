INDEX_HTML = """<!DOCTYPE html>
<html lang="en" class="dark">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Website Safety Checker</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <script>
    tailwind.config = {
      darkMode: 'class',
      theme: {
        extend: {
          colors: {
            appwrite: {
              pink: '#FD366E',
              pinkHover: '#FF4D80',
              pinkActive: '#E0295A',
              card: '#19191D',
              border: '#27272F',
              bg: '#141416',
            }
          }
        }
      }
    }
  </script>
  <style>
    /* Appwrite Dark Console Glass Styling */
    .glass-panel {
      background: rgba(25, 25, 29, 0.75);
      backdrop-filter: blur(20px);
      -webkit-backdrop-filter: blur(20px);
      border: 1px solid #27272F;
      box-shadow: 0 10px 30px 0 rgba(0, 0, 0, 0.45), inset 0 1px 0 0 rgba(255, 255, 255, 0.06);
    }
    .glass-menu {
      background: rgba(22, 22, 26, 0.92);
      backdrop-filter: blur(24px);
      -webkit-backdrop-filter: blur(24px);
      border: 1px solid rgba(253, 54, 110, 0.25);
      box-shadow: 0 20px 45px 0 rgba(0, 0, 0, 0.65), inset 0 1px 0 0 rgba(255, 255, 255, 0.1);
    }
    .glass-pill {
      background: rgba(255, 255, 255, 0.04);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid #2E2E38;
      box-shadow: inset 0 1px 0 0 rgba(255, 255, 255, 0.05);
    }
    .glass-pill:hover {
      background: rgba(255, 255, 255, 0.07);
      border-color: rgba(253, 54, 110, 0.4);
    }
    .glow-appwrite {
      box-shadow: 0 0 45px -8px rgba(253, 54, 110, 0.25);
    }
    @keyframes pulse-subtle {
      0%, 100% { opacity: 1; transform: scale(1); }
      50% { opacity: 0.75; transform: scale(0.98); }
    }
    .pulse-subtle { animation: pulse-subtle 3s ease-in-out infinite; }
  </style>
</head>
<body class="bg-[#141416] text-[#EDEDF0] min-h-screen font-sans antialiased selection:bg-[#FD366E]/30 selection:text-[#FF7098] relative overflow-x-hidden">

  <!-- Ambient Blurred Background Warm Pink & Dark Glows matching Appwrite Console -->
  <div class="fixed top-[-10%] right-[-5%] w-[600px] h-[600px] rounded-full bg-[#FD366E]/[0.07] blur-[150px] pointer-events-none -z-10"></div>
  <div class="fixed bottom-[-10%] left-[10%] w-[500px] h-[500px] rounded-full bg-[#FD366E]/[0.05] blur-[140px] pointer-events-none -z-10"></div>

  <div class="max-w-3xl mx-auto px-4 py-6 sm:py-10 relative">

    <!-- Floating Top Navigation Bar (Appwrite Console Style) -->
    <header class="glass-panel rounded-2xl px-5 py-3.5 flex items-center justify-between transition-all duration-300">
      <div class="flex items-center space-x-3.5">
        <div class="w-10 h-10 rounded-xl glass-pill flex items-center justify-center text-[#FD366E] border-[#FD366E]/30 shadow-[0_0_20px_rgba(253,54,110,0.25)]">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
          </svg>
        </div>
        <div>
          <h1 class="text-base font-bold tracking-tight text-white flex items-center gap-2">
            Safety Shield
            <span class="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-[#FD366E]/15 text-[#FD366E] border border-[#FD366E]/30">v1.0</span>
          </h1>
          <p class="text-[11px] text-[#8F8F9D] font-medium">Security Threat Intelligence Engine</p>
        </div>
      </div>

      <!-- Right Header Actions -->
      <div class="flex items-center space-x-2 relative">
        <span class="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium glass-pill text-emerald-400 border-emerald-500/25">
          <span class="w-1.5 h-1.5 mr-1.5 rounded-full bg-emerald-400 pulse-subtle"></span> :8000 Live
        </span>

        <!-- Menu Button -->
        <button id="glassMenuTrigger" type="button" class="glass-pill p-2 rounded-xl text-slate-300 hover:text-white hover:border-[#FD366E]/40 transition-all flex items-center space-x-1.5">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"/>
          </svg>
        </button>

        <!-- Dropdown Menu -->
        <div id="glassDropdown" class="hidden absolute right-0 top-12 w-56 glass-menu rounded-2xl p-2 z-50 shadow-2xl transition-all duration-200">
          <div class="px-3 py-2 border-b border-[#2E2E38] mb-1">
            <p class="text-xs font-semibold text-white">Application Options</p>
            <p class="text-[10px] text-[#8F8F9D]">Website Safety Checker</p>
          </div>
          <button type="button" id="menuClearHistory" class="w-full text-left px-3 py-2 text-xs text-[#FD366E] hover:bg-[#FD366E]/10 rounded-xl transition-colors flex items-center space-x-2.5">
            <span>🗑️</span> <span>Clear Recent History</span>
          </button>
        </div>
      </div>
    </header>

    <!-- Scan Input Card (Appwrite Console Dark Pink Aesthetic) -->
    <section class="mt-8 glass-panel rounded-3xl p-6 sm:p-7 glow-appwrite transition-all duration-300 relative overflow-hidden">
      <!-- Subtle top-edge light glare -->
      <div class="absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-[#FD366E]/40 to-transparent"></div>

      <div class="mb-5">
        <h2 class="text-lg font-bold text-white tracking-tight">Evaluate Link Safety</h2>
        <p class="text-xs text-[#8F8F9D] mt-1">Concurrently runs 7 security engines with real TLS inspection, Levenshtein brand lookalike checks, and scam detection.</p>
      </div>
      
      <form id="scanForm" class="flex flex-col sm:flex-row gap-3">
        <div class="relative flex-1">
          <div class="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-400">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" />
            </svg>
          </div>
          <input 
            type="text" 
            id="urlInput" 
            placeholder="Paste URL (e.g., https://example.com or fl1pkart.com)" 
            required 
            class="w-full pl-11 pr-24 py-3.5 bg-[#121215] border border-[#27272F] rounded-2xl text-sm text-white placeholder-[#6C6C7A] focus:outline-none focus:border-[#FD366E]/70 focus:ring-4 focus:ring-[#FD366E]/15 shadow-[inset_0_2px_4px_rgba(0,0,0,0.5)] transition-all"
          />
          <button 
            type="button" 
            id="pasteBtn" 
            class="absolute right-2.5 top-2.5 px-3 py-1.5 text-xs font-medium glass-pill text-slate-300 hover:text-white rounded-xl transition-all"
          >
            Paste
          </button>
        </div>
        <button 
          type="submit" 
          id="submitBtn" 
          class="inline-flex items-center justify-center px-7 py-3.5 bg-[#FD366E] hover:bg-[#FF4D80] active:bg-[#E0295A] text-white font-semibold text-sm rounded-2xl shadow-[0_4px_25px_rgba(253,54,110,0.35)] hover:shadow-[0_6px_30px_rgba(253,54,110,0.5)] transition-all disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <span id="btnText">Scan Website</span>
          <svg id="btnSpinner" class="hidden animate-spin ml-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
        </button>
      </form>
    </section>

    <!-- Scan Results Container (Hidden initially) -->
    <main id="resultsContainer" class="hidden mt-8 space-y-6">
      
      <!-- Overall Verdict Glass Banner -->
      <div id="verdictBanner" class="glass-panel rounded-3xl p-6 sm:p-7 relative overflow-hidden transition-all duration-300">
        <div id="verdictGlare" class="absolute inset-x-0 top-0 h-[1px] bg-gradient-to-r from-transparent via-white/30 to-transparent"></div>

        <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-5">
          <div class="flex items-center space-x-4">
            <div id="verdictIconContainer" class="p-3.5 rounded-2xl glass-pill shadow-inner">
              <!-- Dynamically populated icon -->
            </div>
            <div>
              <div class="flex items-center space-x-2">
                <span id="verdictTag" class="text-2xl font-black tracking-wide uppercase drop-shadow-md">LOOKS_OK</span>
              </div>
              <p id="verdictLabel" class="text-sm font-medium mt-0.5 opacity-90 text-[#A1A1AA]">Looks OK (No known threats found)</p>
            </div>
          </div>
          <div class="flex items-center space-x-3 self-start sm:self-auto">
            <div class="glass-pill px-5 py-3 rounded-2xl text-right border-[#2E2E38]">
              <div class="text-[10px] uppercase tracking-wider opacity-75 font-semibold text-[#8F8F9D]">Overall Score</div>
              <div id="overallScoreBadge" class="text-3xl font-black text-white">90<span class="text-xs font-normal opacity-60"> / 100</span></div>
            </div>
          </div>
        </div>

        <div class="mt-5 pt-4 border-t border-[#27272F] flex flex-wrap items-center justify-between text-xs text-[#8F8F9D] gap-2">
          <div class="truncate max-w-md">
            <span class="font-semibold text-slate-400">Inspected URL:</span> <span id="targetUrlText" class="font-mono text-[#FD366E]">https://example.com</span>
          </div>
          <div class="flex items-center space-x-2">
            <a id="openExternalBrowserLink" href="#" target="_blank" rel="noopener noreferrer" class="font-semibold text-emerald-400 hover:text-emerald-300 flex items-center space-x-1.5 glass-pill px-3 py-1.5 rounded-xl transition-all border-emerald-500/30">
              <svg class="w-4 h-4 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
              </svg>
              <span>Open in Browser</span>
            </a>
            <button id="openWhyScoreBtn" class="font-medium text-[#FD366E] hover:text-[#FF4D80] flex items-center space-x-1.5 glass-pill px-3 py-1.5 rounded-xl transition-all">
              <svg class="w-4 h-4 text-[#FD366E]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <span>Why this score?</span>
            </button>
          </div>
        </div>
      </div>

      <!-- Categories Header & Controls -->
      <div class="flex items-center justify-between pt-2">
        <h3 class="text-base font-bold text-white flex items-center space-x-2">
          <span>Security Category Breakdown</span>
          <span class="text-[11px] font-semibold px-2.5 py-0.5 rounded-full glass-pill text-[#FD366E] border-[#FD366E]/30">7 Analyzed</span>
        </h3>
        <span class="text-xs text-[#8F8F9D] flex items-center space-x-1">
          <svg class="w-3.5 h-3.5 text-[#6C6C7A]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
          </svg>
          <span>Tap to expand signals</span>
        </span>
      </div>

      <!-- Category Cards Accordion List (Appwrite Card Style) -->
      <div id="categoriesList" class="space-y-3">
        <!-- Dynamically rendered -->
      </div>
    </main>

    <!-- Recent Scans Section -->
    <section class="mt-12 pt-8 border-t border-[#27272F]">
      <div class="flex items-center justify-between mb-4">
        <h3 class="text-xs font-bold uppercase tracking-wider text-[#8F8F9D] flex items-center space-x-2">
          <span>Recent Scans</span>
        </h3>
        <button id="clearHistoryBtn" class="text-xs text-[#8F8F9D] hover:text-[#FD366E] transition-colors glass-pill px-2.5 py-1 rounded-lg">
          Clear History
        </button>
      </div>
      <div id="historyList" class="space-y-2.5">
        <!-- Rendered from localStorage -->
      </div>
    </section>

  </div>

  <!-- "Why this score?" Glass Bottom Sheet / Modal -->
  <div id="whyModal" class="fixed inset-0 z-50 hidden bg-black/80 backdrop-blur-md flex items-end sm:items-center justify-center p-0 sm:p-4 transition-all duration-300">
    <div class="glass-menu rounded-t-3xl sm:rounded-3xl max-w-lg w-full max-h-[85vh] overflow-y-auto p-6 sm:p-7 shadow-[0_25px_60px_-15px_rgba(0,0,0,0.85)] border border-[#2E2E38]">
      <div class="flex items-center justify-between pb-4 border-b border-[#2E2E38]">
        <div class="flex items-center space-x-2.5 text-white">
          <div class="p-2 rounded-xl glass-pill text-[#FD366E]">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
            </svg>
          </div>
          <h4 class="font-bold text-base">How This Score Was Calculated</h4>
        </div>
        <button id="closeWhyModalBtn" class="glass-pill p-1.5 rounded-xl text-slate-400 hover:text-white transition-all">
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
        </button>
      </div>

      <div class="py-4 space-y-4 text-sm text-slate-300">
        <div class="p-4 glass-panel rounded-2xl space-y-2 border-[#27272F]">
          <div class="flex justify-between items-center text-xs text-[#8F8F9D] font-semibold uppercase">
            <span>Overall Verdict</span>
            <span id="modalVerdict" class="text-white font-bold">LOOKS_OK</span>
          </div>
          <div class="flex justify-between items-center text-xs text-[#8F8F9D] font-semibold uppercase">
            <span>Overall Score</span>
            <span id="modalScore" class="text-white font-bold">90 / 100</span>
          </div>
          <div class="flex justify-between items-center text-xs text-[#8F8F9D] font-semibold uppercase">
            <span>Driving Category</span>
            <span id="modalDriver" class="text-[#FD366E] font-bold">-</span>
          </div>
        </div>

        <div class="p-4 glass-pill rounded-2xl">
          <h5 class="font-semibold text-white mb-1 flex items-center space-x-2">
            <span>⚖️ Worst-Category-Wins Architecture</span>
          </h5>
          <p class="text-xs text-[#8F8F9D] leading-relaxed">
            The overall score is driven strictly by <code class="text-[#FD366E] bg-white/5 px-1.5 py-0.5 rounded">min(category_scores) - secondary_penalties</code>. We strictly avoid simple averages so that high clean scores can never mask high-risk threats.
          </p>
        </div>

        <div class="p-4 glass-pill rounded-2xl">
          <h5 class="font-semibold text-white mb-1 flex items-center space-x-2">
            <span>🚨 Critical Override Rule</span>
          </h5>
          <p class="text-xs text-[#8F8F9D] leading-relaxed">
            A single critical hit in <strong class="text-slate-200">Malware</strong> or <strong class="text-slate-200">Phishing</strong> immediately forces the top verdict to <span class="text-[#FD366E] font-semibold">DANGEROUS</span> and hard-caps the score at &le; 25.
          </p>
        </div>

        <div class="p-4 glass-pill rounded-2xl">
          <h5 class="font-semibold text-white mb-1 flex items-center space-x-2">
            <span>🛡️ Anti-False-Positive Guardrails</span>
          </h5>
          <ul class="text-xs text-[#8F8F9D] space-y-1.5 list-disc list-inside">
            <li>Soft categories (Shopping, Scam, Reputation) require at least <strong class="text-slate-200">2 independent signals</strong> before triggering a HIGH risk rating.</li>
            <li>Domains registered &lt; 90 days ago with zero scam signals evaluate to <span class="text-slate-300 font-semibold">NOT_ENOUGH_INFO</span> rather than false panic.</li>
            <li>The maximum verdict is <strong class="text-emerald-400 font-semibold">LOOKS_OK</strong> ("Looks OK (No known threats found)"), never outputting "100% Safe".</li>
          </ul>
        </div>
      </div>
    </div>
  </div>

  <script>
    const form = document.getElementById('scanForm');
    const urlInput = document.getElementById('urlInput');
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnSpinner = document.getElementById('btnSpinner');
    const pasteBtn = document.getElementById('pasteBtn');
    const resultsContainer = document.getElementById('resultsContainer');
    const verdictBanner = document.getElementById('verdictBanner');
    const verdictTag = document.getElementById('verdictTag');
    const verdictLabel = document.getElementById('verdictLabel');
    const overallScoreBadge = document.getElementById('overallScoreBadge');
    const targetUrlText = document.getElementById('targetUrlText');
    const verdictIconContainer = document.getElementById('verdictIconContainer');
    const categoriesList = document.getElementById('categoriesList');
    const historyList = document.getElementById('historyList');
    const clearHistoryBtn = document.getElementById('clearHistoryBtn');
    const menuClearHistory = document.getElementById('menuClearHistory');

    // Menu trigger & dropdown
    const glassMenuTrigger = document.getElementById('glassMenuTrigger');
    const glassDropdown = document.getElementById('glassDropdown');

    glassMenuTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      glassDropdown.classList.toggle('hidden');
    });

    document.addEventListener('click', (e) => {
      if (!glassDropdown.contains(e.target) && e.target !== glassMenuTrigger) {
        glassDropdown.classList.add('hidden');
      }
    });

    // Why Modal
    const whyModal = document.getElementById('whyModal');
    const openWhyScoreBtn = document.getElementById('openWhyScoreBtn');
    const closeWhyModalBtn = document.getElementById('closeWhyModalBtn');
    const modalVerdict = document.getElementById('modalVerdict');
    const modalScore = document.getElementById('modalScore');
    const modalDriver = document.getElementById('modalDriver');

    let currentScanData = null;

    // Paste button handler
    pasteBtn.addEventListener('click', async () => {
      try {
        const text = await navigator.clipboard.readText();
        if (text) {
          urlInput.value = text.trim();
          executeScan(text.trim());
        }
      } catch (e) {
        urlInput.focus();
      }
    });

    // Form submit
    form.addEventListener('submit', (e) => {
      e.preventDefault();
      executeScan(urlInput.value.trim());
    });

    async function executeScan(url) {
      if (!url) return;
      setLoading(true);

      try {
        const response = await fetch('/api/v1/scan', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: url })
        });

        if (!response.ok) {
          const err = await response.json().catch(() => ({ detail: 'Scan request failed' }));
          throw new Error(err.detail || 'Scan failed');
        }

        const data = await response.json();
        currentScanData = data;
        renderResults(data);
        saveToHistory(data);
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
      } catch (err) {
        alert('Scan Error: ' + err.message);
      } finally {
        setLoading(false);
      }
    }

    function setLoading(isLoading) {
      submitBtn.disabled = isLoading;
      if (isLoading) {
        btnText.textContent = 'Analyzing...';
        btnSpinner.classList.remove('hidden');
      } else {
        btnText.textContent = 'Scan Website';
        btnSpinner.classList.add('hidden');
      }
    }

    function getVerdictGlassStyles(verdict) {
      switch (verdict) {
        case 'DANGEROUS':
          return {
            bg: 'bg-[#FD366E]/10 border-[#FD366E]/40 text-red-100 shadow-[0_8px_32px_0_rgba(253,54,110,0.25)]',
            icon: `<svg class="w-8 h-8 text-[#FD366E]" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`
          };
        case 'SUSPICIOUS':
          return {
            bg: 'bg-amber-500/10 border-amber-500/30 text-amber-100 shadow-[0_8px_32px_0_rgba(245,158,11,0.25)]',
            icon: `<svg class="w-8 h-8 text-amber-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>`
          };
        case 'NOT_ENOUGH_INFO':
          return {
            bg: 'bg-slate-500/10 border-slate-500/30 text-slate-100 shadow-[0_8px_32px_0_rgba(100,116,139,0.25)]',
            icon: `<svg class="w-8 h-8 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`
          };
        case 'LOOKS_OK':
        default:
          return {
            bg: 'bg-emerald-500/10 border-emerald-500/30 text-emerald-100 shadow-[0_8px_32px_0_rgba(16,185,129,0.25)]',
            icon: `<svg class="w-8 h-8 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>`
          };
      }
    }

    function getRiskBadgeGlassClass(risk) {
      switch (risk) {
        case 'CRITICAL': return 'bg-[#FD366E]/20 text-[#FD366E] border-[#FD366E]/30';
        case 'HIGH': return 'bg-orange-500/15 text-orange-400 border-orange-500/30';
        case 'MEDIUM': return 'bg-amber-500/15 text-amber-400 border-amber-500/30';
        case 'LOW': return 'bg-blue-500/15 text-blue-400 border-blue-500/30';
        case 'NOT_ENOUGH_INFO': return 'bg-slate-500/15 text-slate-300 border-slate-500/30';
        case 'UNKNOWN': return 'bg-purple-500/15 text-purple-400 border-purple-500/30';
        case 'SAFE':
        default: return 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30';
      }
    }

    function getSeverityBadgeGlassClass(sev) {
      switch (sev.toUpperCase()) {
        case 'CRITICAL': return 'bg-[#FD366E] text-white font-bold';
        case 'HIGH': return 'bg-orange-600 text-white';
        case 'MEDIUM': return 'bg-amber-600 text-white';
        case 'LOW': return 'bg-blue-600 text-white';
        case 'INFO': return 'bg-[#27272F] text-slate-300 border border-[#3E3E4A]';
        default: return 'bg-purple-600 text-white';
      }
    }

    function getCategoryTitle(name) {
      const map = {
        'phishing': 'Phishing & Impersonation',
        'malware': 'Malware & Threat Intelligence',
        'shopping_trust': 'Shopping & E-Commerce Trust',
        'scam_offer': 'Scam Offers & Artificial Urgency',
        'connection_security': 'Connection Security & TLS',
        'trackers': 'Trackers & Privacy Networks',
        'reputation': 'Domain Reputation & Age'
      };
      return map[name] || name.toUpperCase();
    }

    function getCategoryIcon(name) {
      switch (name) {
        case 'phishing': return '🎣';
        case 'malware': return '🦠';
        case 'shopping_trust': return '🛍️';
        case 'scam_offer': return '🎁';
        case 'connection_security': return '🔒';
        case 'trackers': return '👁️';
        case 'reputation': return '🌐';
        default: return '🛡️';
      }
    }

    function renderResults(data) {
      resultsContainer.classList.remove('hidden');

      const styles = getVerdictGlassStyles(data.overall.verdict);
      verdictBanner.className = `glass-panel rounded-3xl p-6 sm:p-7 relative overflow-hidden transition-all duration-300 ${styles.bg}`;
      verdictTag.textContent = data.overall.verdict;
      verdictLabel.textContent = data.overall.label;
      overallScoreBadge.innerHTML = `${data.overall.score}<span class="text-xs font-normal opacity-60"> / 100</span>`;
      targetUrlText.textContent = data.url;
      verdictIconContainer.innerHTML = styles.icon;

      // Setup Open in Browser link
      const openLink = document.getElementById('openExternalBrowserLink');
      if (openLink) {
        let launchUrl = data.url.trim();
        if (!launchUrl.startsWith('http://') && !launchUrl.startsWith('https://')) {
          launchUrl = 'https://' + launchUrl;
        }
        openLink.href = launchUrl;
        if (data.overall.verdict === 'DANGEROUS') {
          openLink.className = "font-semibold text-rose-400 hover:text-rose-300 flex items-center space-x-1.5 glass-pill px-3 py-1.5 rounded-xl transition-all border-rose-500/30";
          openLink.onclick = (e) => {
            if (!confirm("⚠️ SECURITY WARNING: This website was flagged as DANGEROUS (" + (data.overall.max_risk_category || 'threat detected') + "). Proceeding could compromise your security, steal credentials, or install malware.\n\nAre you sure you want to open this site?")) {
              e.preventDefault();
            }
          };
        } else if (data.overall.verdict === 'SUSPICIOUS') {
          openLink.className = "font-semibold text-amber-400 hover:text-amber-300 flex items-center space-x-1.5 glass-pill px-3 py-1.5 rounded-xl transition-all border-amber-500/30";
          openLink.onclick = (e) => {
            if (!confirm("⚠️ CAUTION: This website has suspicious signals (" + (data.overall.max_risk_category || 'potential risk') + "). Exercise care before sharing sensitive information.\n\nProceed to site?")) {
              e.preventDefault();
            }
          };
        } else {
          openLink.className = "font-semibold text-emerald-400 hover:text-emerald-300 flex items-center space-x-1.5 glass-pill px-3 py-1.5 rounded-xl transition-all border-emerald-500/30";
          openLink.onclick = null;
        }
      }

      // Render Categories
      categoriesList.innerHTML = '';
      data.categories.forEach((cat, idx) => {
        const card = document.createElement('div');
        card.className = 'glass-panel rounded-2xl overflow-hidden transition-all duration-300 hover:border-[#FD366E]/30';
        
        const signalCountText = cat.signals.length === 1 ? '1 signal' : `${cat.signals.length} signals`;
        
        let signalsHtml = '';
        if (cat.signals.length === 0) {
          signalsHtml = `<div class="p-4 text-xs text-[#8F8F9D] italic">No threats or risk signals detected in this category.</div>`;
        } else {
          signalsHtml = cat.signals.map(s => `
            <div class="p-3.5 glass-pill rounded-xl mb-2 last:mb-0 transition-colors border-[#27272F]">
              <div class="flex items-center justify-between mb-1.5">
                <span class="text-xs font-bold text-slate-200 tracking-wide">${s.name.replace(/_/g, ' ').toUpperCase()}</span>
                <span class="px-2.5 py-0.5 rounded-full text-[10px] font-bold ${getSeverityBadgeGlassClass(s.severity)}">${s.severity}</span>
              </div>
              <p class="text-xs text-[#B5B5BE] leading-relaxed">${s.description}</p>
            </div>
          `).join('');
        }

        card.innerHTML = `
          <button type="button" class="w-full px-5 py-4 flex items-center justify-between text-left hover:bg-white/[0.03] transition-colors focus:outline-none cursor-pointer" onclick="toggleAccordion(${idx})">
            <div class="flex items-center space-x-3.5">
              <div class="w-10 h-10 rounded-xl glass-pill flex items-center justify-center font-black text-sm text-[#FD366E] border-[#2E2E38]">
                ${cat.score}
              </div>
              <div>
                <h4 class="text-sm font-semibold text-white flex items-center space-x-1.5">
                  <span>${getCategoryIcon(cat.name)}</span>
                  <span>${getCategoryTitle(cat.name)}</span>
                </h4>
                <div class="flex items-center space-x-2 mt-1">
                  <span class="text-[10px] font-semibold px-2 py-0.5 rounded-full border ${getRiskBadgeGlassClass(cat.riskLevel)}">${cat.riskLevel}</span>
                  <span class="text-xs text-[#8F8F9D]">&bull; ${signalCountText}</span>
                </div>
              </div>
            </div>
            <div class="flex items-center space-x-2 text-slate-400">
              <div class="p-1 rounded-lg glass-pill text-slate-300">
                <svg id="chevron-${idx}" class="w-4 h-4 transform transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"/>
                </svg>
              </div>
            </div>
          </button>
          <div id="content-${idx}" class="hidden px-5 pb-5 pt-1 border-t border-[#27272F]">
            ${signalsHtml}
          </div>
        `;
        categoriesList.appendChild(card);
      });
    }

    window.toggleAccordion = function(idx) {
      const content = document.getElementById(`content-${idx}`);
      const chevron = document.getElementById(`chevron-${idx}`);
      if (content.classList.contains('hidden')) {
        content.classList.remove('hidden');
        chevron.classList.add('rotate-180');
      } else {
        content.classList.add('hidden');
        chevron.classList.remove('rotate-180');
      }
    };

    // "Why this score?" modal events
    openWhyScoreBtn.addEventListener('click', () => {
      if (!currentScanData) return;
      modalVerdict.textContent = currentScanData.overall.verdict;
      modalScore.textContent = `${currentScanData.overall.score} / 100`;
      modalDriver.textContent = currentScanData.overall.max_risk_category || 'Evenly evaluated across categories';
      whyModal.classList.remove('hidden');
    });

    closeWhyModalBtn.addEventListener('click', () => {
      whyModal.classList.add('hidden');
    });

    whyModal.addEventListener('click', (e) => {
      if (e.target === whyModal) whyModal.classList.add('hidden');
    });

    // History Storage
    function saveToHistory(scan) {
      let history = JSON.parse(localStorage.getItem('safety_scans') || '[]');
      history = [scan, ...history.filter(h => h.url !== scan.url)].slice(0, 8);
      localStorage.setItem('safety_scans', JSON.stringify(history));
      renderHistory();
    }

    function renderHistory() {
      const history = JSON.parse(localStorage.getItem('safety_scans') || '[]');
      if (history.length === 0) {
        historyList.innerHTML = `<p class="text-xs text-[#8F8F9D] italic p-3 glass-pill rounded-xl">No recent scans saved yet.</p>`;
        return;
      }
      historyList.innerHTML = history.map(item => `
        <div class="flex items-center justify-between p-3.5 rounded-2xl glass-pill hover:border-[#FD366E]/40 cursor-pointer transition-all" onclick="loadFromHistory('${item.url}')">
          <div class="flex items-center space-x-3.5 truncate">
            <span class="w-8 h-8 rounded-xl glass-panel flex items-center justify-center text-xs font-bold text-[#FD366E] border-[#2E2E38]">${item.overall.score}</span>
            <div class="truncate">
              <p class="text-xs font-semibold text-white truncate">${item.domain}</p>
              <p class="text-[11px] text-[#8F8F9D] truncate">${item.overall.label}</p>
            </div>
          </div>
          <span class="text-xs text-[#FD366E] font-medium ml-2 px-2.5 py-1 rounded-lg glass-panel">&rarr;</span>
        </div>
      `).join('');
    }

    window.loadFromHistory = function(url) {
      const history = JSON.parse(localStorage.getItem('safety_scans') || '[]');
      const match = history.find(h => h.url === url);
      if (match) {
        currentScanData = match;
        urlInput.value = match.url;
        renderResults(match);
        resultsContainer.scrollIntoView({ behavior: 'smooth' });
      }
    };

    const handleClearHistory = () => {
      localStorage.removeItem('safety_scans');
      glassDropdown.classList.add('hidden');
      renderHistory();
    };

    clearHistoryBtn.addEventListener('click', handleClearHistory);
    menuClearHistory.addEventListener('click', handleClearHistory);

    // Initial history load
    renderHistory();
  </script>
</body>
</html>
"""

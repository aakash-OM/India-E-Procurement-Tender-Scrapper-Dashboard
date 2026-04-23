/**
 * Gov Tender Dashboard – Main Frontend Logic
 */

// ── State ─────────────────────────────────────────────────────────────────────
const state = {
  keywords:         [],
  portals:          [],
  selectedPortals:  new Set(['gem']),
  selectedKeywords: new Set(),
  portalCategory:   'central',
  results:          [],
  totalResults:     0,
  page:             0,
  pageSize:         50,
  filters:          {},
  charts:           {},
  sortCol:          'scraped_at',
  sortDir:          'desc',
  polling:          null,
};

// ── Init ──────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  initNav();
  init3DCards();
  loadKeywords();
  loadPortals();
  loadStats();
  loadResults();
  initCharts();
  showSection('dashboard');
});

// ── Navigation ────────────────────────────────────────────────────────────────
function initNav() {
  document.querySelectorAll('[data-section]').forEach(btn => {
    btn.addEventListener('click', () => {
      const sec = btn.dataset.section;
      showSection(sec);
      document.querySelectorAll('[data-section]').forEach(b => b.classList.remove('active'));
      document.querySelectorAll(`[data-section="${sec}"]`).forEach(b => b.classList.add('active'));
    });
  });
}

function showSection(name) {
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  const sec = document.getElementById('sec-' + name);
  if (sec) sec.classList.add('active');
  if (name === 'dashboard') loadStats();
  if (name === 'results')   loadResults();
}

// ── 3D Card Tilt Effect ───────────────────────────────────────────────────────
function initCardTilt(root) {
  (root || document).querySelectorAll('.card-3d').forEach(card => {
    card.addEventListener('mousemove', e => {
      const rect = card.getBoundingClientRect();
      const x = (e.clientX - rect.left) / rect.width  - 0.5;
      const y = (e.clientY - rect.top)  / rect.height - 0.5;
      card.style.transform = `perspective(800px) rotateX(${-y * 12}deg) rotateY(${x * 14}deg) translateZ(8px)`;
    });
    card.addEventListener('mouseleave', () => {
      card.style.transform = 'perspective(800px) rotateX(0) rotateY(0) translateZ(0)';
    });
  });
}

function init3DCards() { initCardTilt(); }

// ── Keywords ──────────────────────────────────────────────────────────────────
async function loadKeywords() {
  const res  = await fetch('/api/keywords');
  state.keywords = await res.json();
  renderKeywords();
  renderSearchKeywords();
}

function renderKeywords() {
  const search = (document.getElementById('kw-search')?.value || '').toLowerCase();
  const container = document.getElementById('keywords-container');
  if (!container) return;

  // Group by category
  const cats = {};
  state.keywords.forEach(k => {
    if (search && !k.keyword.toLowerCase().includes(search)) return;
    if (!cats[k.category]) cats[k.category] = [];
    cats[k.category].push(k);
  });

  container.innerHTML = Object.entries(cats).map(([cat, kws]) => `
    <div class="keyword-category-block">
      <div class="keyword-cat-label">
        <i class="fa-solid fa-tag"></i>
        ${escHtml(cat)} <span class="text-muted" style="font-size:10px;margin-left:4px">(${kws.length})</span>
      </div>
      <div class="keyword-chips">
        ${kws.map(k => `
          <span class="keyword-chip ${k.is_active ? '' : 'inactive'}"
                data-id="${k.id}"
                onclick="toggleKwActive(${k.id})">
            ${escHtml(k.keyword)}
            <button class="chip-delete" onclick="event.stopPropagation(); deleteKeyword(${k.id})"
                    title="Delete keyword">
              <i class="fa-solid fa-xmark"></i>
            </button>
          </span>
        `).join('')}
      </div>
    </div>
  `).join('') || '<div class="empty-state"><i class="fa-solid fa-magnifying-glass"></i><p>No keywords match.</p></div>';

  initCardTilt(container);
}

function renderSearchKeywords() {
  const container = document.getElementById('search-keywords-container');
  if (!container) return;
  container.innerHTML = state.keywords
    .filter(k => k.is_active)
    .map(k => `
      <span class="sel-kw-chip ${state.selectedKeywords.has(k.id) ? 'selected' : ''}"
            data-id="${k.id}"
            onclick="toggleSearchKw(${k.id})"
            style="${state.selectedKeywords.has(k.id) ? '' : 'opacity:.6'}">
        ${escHtml(k.keyword)}
        ${state.selectedKeywords.has(k.id) ? '<i class="fa-solid fa-xmark" style="margin-left:4px;font-size:9px"></i>' : ''}
      </span>
    `).join('');
}

function toggleSearchKw(id) {
  if (state.selectedKeywords.has(id)) state.selectedKeywords.delete(id);
  else state.selectedKeywords.add(id);
  renderSearchKeywords();
}

window.toggleKwActive = async (id) => {
  await fetch(`/api/keywords/${id}/toggle`, { method: 'POST' });
  await loadKeywords();
};

window.deleteKeyword = async (id) => {
  if (!confirm('Delete this keyword?')) return;
  await fetch(`/api/keywords/${id}`, { method: 'DELETE' });
  state.keywords = state.keywords.filter(k => k.id !== id);
  state.selectedKeywords.delete(id);
  renderKeywords();
  renderSearchKeywords();
  showToast('Keyword deleted', 'info');
};

// Add keyword modal
window.openAddKeyword = () => {
  document.getElementById('modal-add-keyword').classList.add('open');
  document.getElementById('new-kw-input')?.focus();
};

window.closeAddKeyword = () => {
  document.getElementById('modal-add-keyword').classList.remove('open');
  document.getElementById('new-kw-input').value = '';
};

window.submitAddKeyword = async () => {
  const keyword  = document.getElementById('new-kw-input').value.trim();
  const category = document.getElementById('new-kw-cat').value.trim() || 'General';
  if (!keyword) return;

  const res = await fetch('/api/keywords', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ keyword, category }),
  });

  if (res.ok) {
    const data = await res.json();
    state.keywords.push({ ...data, is_active: 1 });
    renderKeywords();
    renderSearchKeywords();
    closeAddKeyword();
    showToast(`"${keyword}" added`, 'success');
  }
};

document.getElementById('kw-search')?.addEventListener('input', renderKeywords);

// ── Portals ───────────────────────────────────────────────────────────────────
async function loadPortals() {
  const res = await fetch('/api/portals');
  state.portals = await res.json();
  renderPortals(state.portalCategory);
  renderSearchPortalChips();
  updateSelectedPortalsSummary();
}

const PORTAL_CATS = {
  central:   'Central Government',
  railways:  'Railways & Defence',
  energy:    'Power & Energy',
  petroleum: 'Petroleum & Energy',
  mfg:       'Manufacturing',
  infra:     'Infrastructure',
  state:     'state',
};

function renderPortals(catFilter) {
  state.portalCategory = catFilter;
  document.querySelectorAll('[data-portal-cat]').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.portalCat === catFilter);
  });

  const container = document.getElementById('portals-grid');
  if (!container) return;

  let portals;
  if (catFilter === 'state') {
    portals = state.portals.filter(p => p.type === 'state');
  } else if (catFilter === 'all') {
    portals = state.portals;
  } else {
    const label = PORTAL_CATS[catFilter];
    portals = state.portals.filter(p => p.category === label);
  }

  container.innerHTML = portals.map(p => `
    <div class="portal-card glass-card card-3d ${state.selectedPortals.has(p.id) ? 'selected' : ''}"
         data-id="${p.id}"
         onclick="togglePortal('${p.id}')">
      <div class="portal-card-header">
        <div class="portal-icon" style="background:${p.color}20; color:${p.color}">
          <i class="fa-solid ${p.icon}"></i>
        </div>
        <span class="portal-badge ${p.implemented ? 'live' : 'coming'}">
          ${p.implemented ? 'LIVE' : 'SOON'}
        </span>
      </div>
      <div class="portal-name">${escHtml(p.name)}</div>
      <div class="portal-fullname">${escHtml(p.full_name || p.state || '')}</div>
      ${p.description ? `<div style="font-size:10px;color:var(--text3);margin-top:4px;line-height:1.4;">${escHtml(p.description)}</div>` : ''}
      <div style="margin-top:8px;display:flex;align-items:center;justify-content:space-between;">
        <div class="portal-check">
          ${state.selectedPortals.has(p.id) ? '<i class="fa-solid fa-check"></i>' : ''}
        </div>
        ${p.url ? `
          <a href="${escHtml(p.url)}" target="_blank" rel="noopener"
             onclick="event.stopPropagation()"
             style="font-size:10px;color:${p.color};opacity:.8;text-decoration:none;display:flex;align-items:center;gap:3px;"
             title="Open ${escHtml(p.name)} portal">
            <i class="fa-solid fa-arrow-up-right-from-square"></i> Visit
          </a>` : ''}
      </div>
    </div>
  `).join('') || `<div class="empty-state" style="grid-column:1/-1"><i class="fa-solid fa-globe"></i><p>No portals in this category.</p></div>`;

  initCardTilt(container);
}

window.togglePortal = (id) => {
  if (state.selectedPortals.has(id)) {
    if (state.selectedPortals.size === 1) { showToast('Select at least one portal', 'error'); return; }
    state.selectedPortals.delete(id);
  } else {
    state.selectedPortals.add(id);
  }
  renderPortals(state.portalCategory);
  updateSelectedPortalsSummary();
};

function updateSelectedPortalsSummary() {
  const el = document.getElementById('selected-portals-count');
  if (el) el.textContent = `${state.selectedPortals.size} portal${state.selectedPortals.size !== 1 ? 's' : ''} selected`;
  renderSearchPortalChips();
}

function renderSearchPortalChips() {
  const container = document.getElementById('search-portal-chips');
  if (!container) return;
  if (!state.portals.length) return;

  container.innerHTML = [...state.selectedPortals].map(id => {
    const p = state.portals.find(x => x.id === id);
    if (!p) return '';
    const live = p.implemented;
    return `
      <span style="display:inline-flex;align-items:center;gap:6px;padding:5px 12px;
                   border-radius:12px;font-size:11px;font-weight:600;
                   background:${live ? 'rgba(0,212,255,0.15)' : 'rgba(255,107,53,0.1)'};
                   border:1px solid ${live ? 'rgba(0,212,255,0.3)' : 'rgba(255,107,53,0.2)'};
                   color:${live ? 'var(--cyan)' : 'var(--orange)'};">
        <i class="fa-solid ${live ? 'fa-check' : 'fa-clock'}"></i>
        ${escHtml(p.name)}${live ? '' : ' <span style="font-weight:400;opacity:.7">(soon)</span>'}
        ${live && p.search_url ? `<a href="${escHtml(p.search_url)}" target="_blank" rel="noopener"
            style="color:inherit;opacity:.7;margin-left:2px;" title="Open ${escHtml(p.name)} bid listing">
            <i class="fa-solid fa-arrow-up-right-from-square" style="font-size:9px;"></i></a>` : ''}
      </span>`;
  }).join('');
}

document.querySelectorAll('[data-portal-cat]').forEach(btn => {
  btn.addEventListener('click', () => renderPortals(btn.dataset.portalCat));
});

// Region filter (sidebar)
document.querySelectorAll('.region-chip').forEach(chip => {
  chip.addEventListener('click', () => {
    chip.classList.toggle('selected');
    applyRegionFilter();
  });
});

function applyRegionFilter() {
  const selected = [...document.querySelectorAll('.region-chip.selected')].map(c => c.dataset.region);
  state.filters.regions = selected;
}

// ── Stats & Charts ────────────────────────────────────────────────────────────
async function loadStats() {
  const res  = await fetch('/api/stats');
  const data = await res.json();

  setText('stat-total',   data.total_bids?.toLocaleString() || '0');
  setText('stat-today',   data.today_bids?.toLocaleString() || '0');
  setText('stat-week',    data.week_bids?.toLocaleString()  || '0');
  setText('stat-value',   `₹${data.total_value?.toFixed(1) || '0'}Cr`);
  setText('stat-keywords',data.total_keywords?.toString()  || '0');

  updateCharts(data);
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) animateNumber(el, val);
}

function animateNumber(el, target) {
  const isStr = isNaN(target.replace(/[₹,Cr]/g, ''));
  if (isStr) { el.textContent = target; return; }
  el.textContent = target;
}

function initCharts() {
  const defaults = {
    plugins: {
      legend: { labels: { color: '#8898b3', font: { family: 'Space Grotesk', size: 11 }, boxWidth: 12 } },
      tooltip: {
        backgroundColor: 'rgba(10,15,35,0.95)',
        borderColor: 'rgba(0,212,255,0.3)',
        borderWidth: 1,
        titleColor: '#00d4ff',
        bodyColor: '#e0e6ff',
        titleFont: { family: 'Space Grotesk' },
        bodyFont: { family: 'Space Grotesk' },
      },
    },
    scales: {
      x: { ticks: { color: '#4a5568', font: { family: 'Space Grotesk', size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
      y: { ticks: { color: '#4a5568', font: { family: 'Space Grotesk', size: 10 } }, grid: { color: 'rgba(255,255,255,0.04)' } },
    },
    animation: { duration: 800, easing: 'easeOutQuart' },
    responsive: true,
    maintainAspectRatio: true,
  };

  const portalCtx = document.getElementById('chart-portals')?.getContext('2d');
  if (portalCtx) {
    state.charts.portals = new Chart(portalCtx, {
      type: 'doughnut',
      data: { labels: [], datasets: [{ data: [], backgroundColor: ['#00d4ff','#7b2fff','#ff6b35','#00ff88','#ffd700','#ff2d78'], borderWidth: 0, hoverOffset: 8 }] },
      options: { ...defaults, scales: undefined, plugins: { ...defaults.plugins, legend: { position: 'right', labels: { color: '#8898b3', font: { family: 'Space Grotesk', size: 11 }, boxWidth: 10 } } } },
    });
  }

  const stateCtx = document.getElementById('chart-states')?.getContext('2d');
  if (stateCtx) {
    state.charts.states = new Chart(stateCtx, {
      type: 'bar',
      data: { labels: [], datasets: [{ label: 'Bids', data: [], backgroundColor: 'rgba(0,212,255,0.5)', borderColor: '#00d4ff', borderWidth: 1, borderRadius: 4, hoverBackgroundColor: 'rgba(0,212,255,0.8)' }] },
      options: { ...defaults, indexAxis: 'y', plugins: { ...defaults.plugins, legend: { display: false } } },
    });
  }

  const timeCtx = document.getElementById('chart-timeline')?.getContext('2d');
  if (timeCtx) {
    state.charts.timeline = new Chart(timeCtx, {
      type: 'line',
      data: { labels: [], datasets: [{ label: 'Bids/Day', data: [], borderColor: '#7b2fff', backgroundColor: 'rgba(123,47,255,0.1)', fill: true, tension: 0.4, pointBackgroundColor: '#7b2fff', pointRadius: 3, pointHoverRadius: 6 }] },
      options: { ...defaults },
    });
  }
}

function updateCharts(data) {
  if (state.charts.portals && data.by_portal?.length) {
    state.charts.portals.data.labels   = data.by_portal.map(r => r.portal_id.toUpperCase());
    state.charts.portals.data.datasets[0].data = data.by_portal.map(r => r.count);
    state.charts.portals.update();
  }
  if (state.charts.states && data.by_state?.length) {
    const top10 = data.by_state.slice(0, 10);
    state.charts.states.data.labels = top10.map(r => r.state);
    state.charts.states.data.datasets[0].data = top10.map(r => r.count);
    state.charts.states.update();
  }
  if (state.charts.timeline && data.timeline?.length) {
    state.charts.timeline.data.labels = data.timeline.map(r => r.day);
    state.charts.timeline.data.datasets[0].data = data.timeline.map(r => r.count);
    state.charts.timeline.update();
  }
}

// ── Results ───────────────────────────────────────────────────────────────────
async function loadResults() {
  const params = new URLSearchParams({
    limit:  state.pageSize,
    offset: state.page * state.pageSize,
    ...(state.filters.state   ? { state:   state.filters.state }   : {}),
    ...(state.filters.region  ? { region:  state.filters.region }  : {}),
    ...(state.filters.portal  ? { portal:  state.filters.portal }  : {}),
    ...(state.filters.keyword ? { keyword: state.filters.keyword } : {}),
  });

  const res  = await fetch('/api/bids?' + params);
  const data = await res.json();
  state.results     = data.bids;
  state.totalResults = data.total;

  renderResults();
  renderPagination();
}

function renderResults() {
  const tbody = document.getElementById('results-tbody');
  if (!tbody) return;

  if (!state.results.length) {
    tbody.innerHTML = `<tr><td colspan="10" class="empty-state"><i class="fa-solid fa-inbox"></i><p>No bids found. Run a search to populate results.</p></td></tr>`;
    return;
  }

  const fmt = v => v ? `₹${(v / 1e7).toFixed(2)} Cr` : '—';

  tbody.innerHTML = state.results.map(b => `
    <tr>
      <td><a class="bid-link" href="${escHtml(b.bid_url || '#')}" target="_blank">${escHtml(b.bid_number || '—')}</a></td>
      <td><span class="portal-tag">${escHtml(b.portal_id?.toUpperCase() || '—')}</span></td>
      <td title="${escHtml(b.org_name || '')}">${escHtml((b.org_name || '—').slice(0, 30))}</td>
      <td title="${escHtml(b.department || '')}">${escHtml((b.department || '—').slice(0, 25))}</td>
      <td>${escHtml(b.state || '—')}</td>
      <td><span class="text-cyan">${escHtml(b.region || '—')}</span></td>
      <td title="${escHtml(b.item_category || '')}">${escHtml((b.item_category || '—').slice(0, 30))}</td>
      <td class="value-cell">${fmt(b.estimated_value)}</td>
      <td>${escHtml(b.bid_end_date || '—')}</td>
      <td>${escHtml(b.keyword_used || '—')}</td>
    </tr>
  `).join('');

  document.getElementById('results-count').textContent =
    `Showing ${state.page * state.pageSize + 1}–${Math.min((state.page + 1) * state.pageSize, state.totalResults)} of ${state.totalResults} bids`;
}

function renderPagination() {
  const wrap = document.getElementById('pagination');
  if (!wrap) return;
  const pages = Math.ceil(state.totalResults / state.pageSize);

  let html = `<button class="page-btn" onclick="goPage(${state.page - 1})" ${state.page === 0 ? 'disabled' : ''}>
    <i class="fa-solid fa-chevron-left"></i>
  </button>`;

  const start = Math.max(0, state.page - 2);
  const end   = Math.min(pages - 1, state.page + 2);
  for (let p = start; p <= end; p++) {
    html += `<button class="page-btn ${p === state.page ? 'active' : ''}" onclick="goPage(${p})">${p + 1}</button>`;
  }

  html += `<button class="page-btn" onclick="goPage(${state.page + 1})" ${state.page >= pages - 1 ? 'disabled' : ''}>
    <i class="fa-solid fa-chevron-right"></i>
  </button>`;

  wrap.innerHTML = html;
}

window.goPage = (p) => {
  state.page = Math.max(0, p);
  loadResults();
};

// Results filters
document.getElementById('filter-state')?.addEventListener('change', e => {
  state.filters.state = e.target.value;
  state.page = 0;
  loadResults();
});

document.getElementById('filter-portal')?.addEventListener('change', e => {
  state.filters.portal = e.target.value;
  state.page = 0;
  loadResults();
});

document.getElementById('filter-keyword-input')?.addEventListener('input', e => {
  state.filters.keyword = e.target.value;
  state.page = 0;
  loadResults();
});

// Export
window.exportResults = () => {
  const params = new URLSearchParams(state.filters);
  window.location = '/api/bids/export?' + params;
};

// ── Search / Scraping ─────────────────────────────────────────────────────────
window.startSearch = async () => {
  const portals = [...state.selectedPortals];
  const kwIds   = [...state.selectedKeywords];
  const maxPages = parseInt(document.getElementById('max-pages')?.value || 5);
  const headless = document.getElementById('headless-mode')?.value === 'true';

  const btn = document.getElementById('btn-search');
  btn.disabled = true;
  btn.textContent = 'Starting...';

  const body = {
    portals,
    keyword_ids: kwIds.length ? kwIds : [],
    max_pages:   maxPages,
    headless,
    states:      [...document.querySelectorAll('.region-chip.selected')].map(c => c.dataset.region),
  };

  const res = await fetch('/api/search', {
    method:  'POST',
    headers: { 'Content-Type': 'application/json' },
    body:    JSON.stringify(body),
  });

  if (!res.ok) {
    const err = await res.json();
    showToast(err.error || 'Failed to start search', 'error');
    btn.disabled = false;
    btn.innerHTML = '<i class="fa-solid fa-search"></i> START SEARCH';
    return;
  }

  showToast('Scraping started!', 'success');
  startPolling();
};

function startPolling() {
  if (state.polling) clearInterval(state.polling);
  state.polling = setInterval(pollStatus, 2500);
  updateScrapeUI(true);
}

async function pollStatus() {
  const res  = await fetch('/api/search/status');
  const data = await res.json();

  // Update progress
  const progFill = document.getElementById('prog-fill');
  const progText = document.getElementById('prog-text');
  const progPdf  = document.getElementById('prog-pdf');

  if (progFill) progFill.style.width = (data.progress || 0) + '%';
  if (progText) progText.textContent = `${data.current_portal || ''} › ${data.current_keyword || ''} — ${data.bids_found || 0} bids found`;
  if (progPdf)  progPdf.style.width  = (data.pdf_progress || 0) + '%';

  // Log
  const logEl = document.getElementById('scrape-log');
  if (logEl && data.log) {
    logEl.innerHTML = data.log.slice(-30).map(line => {
      const cls = line.includes('[ERROR]') ? 'error' : line.includes('complete') ? 'success' : '';
      return `<div class="log-entry ${cls}">${escHtml(line)}</div>`;
    }).join('');
    logEl.scrollTop = logEl.scrollHeight;
  }

  // Header indicator
  const dot  = document.querySelector('.scrape-dot');
  const span = document.querySelector('.scrape-indicator span');
  if (dot) dot.classList.toggle('active', data.active);
  if (span) span.textContent = data.active ? `Scraping: ${data.bids_found || 0} found` : 'Idle';

  const prog = document.getElementById('progress-block');
  if (prog) prog.classList.toggle('visible', data.active);

  if (!data.active) {
    clearInterval(state.polling);
    state.polling = null;
    updateScrapeUI(false);
    const progText = document.getElementById('prog-text');
    if (progText) progText.textContent = 'Ready — press START SEARCH to begin fetching from GeM';
    if (data.bids_found > 0) showToast(`Done! ${data.bids_found} new bids saved.`, 'success');
    loadStats();
    loadResults();
  }
}

function updateScrapeUI(active) {
  const btn = document.getElementById('btn-search');
  const stopBtn = document.getElementById('btn-stop');
  if (btn) {
    btn.disabled = active;
    btn.innerHTML = active
      ? '<i class="fa-solid fa-spinner fa-spin"></i> SCRAPING...'
      : '<i class="fa-solid fa-magnifying-glass"></i> START SEARCH';
  }
  if (stopBtn) stopBtn.style.display = active ? 'inline-flex' : 'none';
}

window.stopSearch = async () => {
  await fetch('/api/search/stop', { method: 'POST' });
  showToast('Search stopped', 'info');
};

// ── Toast ─────────────────────────────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', info: 'fa-info-circle' };
  const container = document.getElementById('toast-container');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<i class="fa-solid ${icons[type]}"></i><span>${escHtml(msg)}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.style.animation = 'none'; toast.style.opacity = '0'; toast.style.transition = 'opacity 0.3s'; setTimeout(() => toast.remove(), 300); }, 3500);
}

// ── Utilities ─────────────────────────────────────────────────────────────────
function escHtml(str) {
  if (!str) return '';
  return String(str).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');
}

// ── Select all / none for portals ─────────────────────────────────────────────
window.selectAllPortals = () => {
  state.portals.forEach(p => state.selectedPortals.add(p.id));
  renderPortals(state.portalCategory);
  updateSelectedPortalsSummary();
};

window.clearAllPortals = () => {
  state.selectedPortals.clear();
  state.selectedPortals.add('gem');
  renderPortals(state.portalCategory);
  updateSelectedPortalsSummary();
};

window.selectAllKeywords = () => {
  state.keywords.filter(k => k.is_active).forEach(k => state.selectedKeywords.add(k.id));
  renderSearchKeywords();
};

window.clearAllKeywords = () => {
  state.selectedKeywords.clear();
  renderSearchKeywords();
};

// Close modal on overlay click
document.getElementById('modal-add-keyword')?.addEventListener('click', e => {
  if (e.target === e.currentTarget) closeAddKeyword();
});

// Enter key on keyword input
document.getElementById('new-kw-input')?.addEventListener('keydown', e => {
  if (e.key === 'Enter') submitAddKeyword();
});

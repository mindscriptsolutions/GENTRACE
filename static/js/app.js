/* ── GeneTrace Shared JS ──────────────────────────────────────────────────── */

const API = 'http://localhost:8000';

// ── Token helpers ─────────────────────────────────────────────────────────────
const Auth = {
  getToken: () => localStorage.getItem('gt_token'),
  getUser:  () => { try { return JSON.parse(localStorage.getItem('gt_user')); } catch { return null; } },
  setSession: (token, user) => { localStorage.setItem('gt_token', token); localStorage.setItem('gt_user', JSON.stringify(user)); },
  clear: () => { localStorage.removeItem('gt_token'); localStorage.removeItem('gt_user'); },
  isLoggedIn: () => !!localStorage.getItem('gt_token'),
  requireAuth: () => { if (!Auth.isLoggedIn()) { window.location.href = '/login'; return false; } return true; },
  requireGuest: () => { if (Auth.isLoggedIn()) { window.location.href = '/dashboard'; return false; } return true; },
};

// ── HTTP helpers ──────────────────────────────────────────────────────────────
async function apiFetch(path, options = {}) {
  const token = Auth.getToken();
  const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { ...options, headers });
  if (res.status === 401) { Auth.clear(); window.location.href = '/login'; return; }
  const data = res.headers.get('content-type')?.includes('application/json') ? await res.json() : await res.text();
  if (!res.ok) throw new Error(data?.detail || data || `HTTP ${res.status}`);
  return data;
}

async function apiForm(path, formData) {
  const token = Auth.getToken();
  const headers = {};
  if (token) headers['Authorization'] = `Bearer ${token}`;
  const res = await fetch(`${API}${path}`, { method: 'POST', headers, body: formData });
  if (res.status === 401) { Auth.clear(); window.location.href = '/login'; return; }
  const data = await res.json();
  if (!res.ok) throw new Error(data?.detail || `HTTP ${res.status}`);
  return data;
}

// ── UI helpers ────────────────────────────────────────────────────────────────
function showAlert(container, msg, type = 'danger') {
  const icons = { danger: '⚠', success: '✓', warning: '⚠', info: 'ℹ' };
  container.innerHTML = `<div class="alert alert-${type}"><span>${icons[type]}</span><span>${msg}</span></div>`;
  container.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function clearAlert(container) { container.innerHTML = ''; }

function showLoading(text = 'Processing...') {
  const el = document.createElement('div');
  el.className = 'loading-overlay'; el.id = 'gt-loading';
  el.innerHTML = `<div class="spinner"></div><p>${text}</p>`;
  document.body.appendChild(el);
}

function hideLoading() { document.getElementById('gt-loading')?.remove(); }

function setBtn(btn, loading, text) {
  btn.disabled = loading;
  btn.innerHTML = loading ? `<span class="spinner" style="width:18px;height:18px;border-width:2px"></span> ${text}` : text;
}

// ── Risk helpers ──────────────────────────────────────────────────────────────
function riskLevel(pct) {
  if (pct < 30) return 'low';
  if (pct < 60) return 'moderate';
  return 'high';
}

function riskLabel(pct) {
  const l = riskLevel(pct);
  return `<span class="badge badge-${l}">${l.charAt(0).toUpperCase()+l.slice(1)}</span>`;
}

function norwood_label(stage) {
  const m = {1:'Minimal',2:'Early',3:'Moderate',4:'Significant',5:'Advanced',6:'Severe',7:'Complete'};
  return m[stage] || 'Unknown';
}

// ── Navbar init ───────────────────────────────────────────────────────────────
function initNavbar() {
  const user = Auth.getUser();
  const avatarEl = document.getElementById('navbar-avatar');
  const nameEl   = document.getElementById('navbar-name');
  if (avatarEl && user) avatarEl.textContent = user.full_name?.charAt(0).toUpperCase() || 'U';
  if (nameEl   && user) nameEl.textContent   = user.full_name?.split(' ')[0] || 'User';

  // Hamburger
  const ham = document.getElementById('hamburger');
  const sidebar = document.getElementById('sidebar');
  if (ham && sidebar) {
    ham.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', e => {
      if (!sidebar.contains(e.target) && !ham.contains(e.target)) sidebar.classList.remove('open');
    });
  }

  // Active link
  const path = window.location.pathname.replace('/', '') || 'index';
  document.querySelectorAll('.sidebar-link, .navbar-links a').forEach(a => {
    const href = a.getAttribute('href')?.replace('/', '') || '';
    if (href === path || (path === '' && href === 'index')) a.classList.add('active');
  });

  // Logout
  document.getElementById('logout-btn')?.addEventListener('click', () => {
    Auth.clear(); window.location.href = '/login';
  });
}

// ── Format date ───────────────────────────────────────────────────────────────
function fmtDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', { year:'numeric', month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' });
}

// ── Store prediction result for result page ───────────────────────────────────
const PredStore = {
  save: (data) => localStorage.setItem('gt_pred', JSON.stringify(data)),
  load: () => { try { return JSON.parse(localStorage.getItem('gt_pred')); } catch { return null; } },
  clear: () => localStorage.removeItem('gt_pred'),
};

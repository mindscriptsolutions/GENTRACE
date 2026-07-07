function injectLayout(activePage) {
  const style = `
  <style id="gt-layout-style">
  *,*::before,*::after{box-sizing:border-box}
  :root{
    --bg:#0d1117;--surface:#111827;--surface2:#1a2235;
    --border:rgba(255,255,255,.07);--text:#e2e8f0;--muted:rgba(255,255,255,.4);
    --accent:#38bdf8;--accent2:#6366f1;--success:#22c55e;--danger:#ef4444;--warning:#f59e0b;
    --radius:12px;--sidebar:260px;--font:'Inter',system-ui,sans-serif;
  }
  body{font-family:var(--font);background:var(--bg);color:var(--text);margin:0;line-height:1.6}
  a{text-decoration:none;color:inherit}
  h1{font-size:1.6rem;font-weight:700;color:#fff}
  h2{font-size:1.3rem;font-weight:700;color:#fff}
  h3{font-size:1.1rem;font-weight:600;color:#fff}
  h4{font-size:.95rem;font-weight:600;color:#fff}
  p{color:var(--muted);font-size:.9rem}

  /* NAVBAR */
  .gt-nav{position:fixed;top:0;left:0;right:0;height:64px;background:rgba(13,17,23,.9);backdrop-filter:blur(16px);border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 1.5rem 0 calc(var(--sidebar) + 1.5rem);z-index:200}
  .gt-nav-brand{font-size:1.1rem;font-weight:800;color:#fff;display:flex;align-items:center;gap:.4rem}
  .gt-nav-brand span{color:var(--accent)}
  .gt-nav-right{display:flex;align-items:center;gap:.75rem}
  .gt-nav-name{color:var(--muted);font-size:.85rem}
  .gt-avatar{width:34px;height:34px;border-radius:50%;background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;font-weight:700;font-size:.85rem;display:flex;align-items:center;justify-content:center;cursor:pointer}
  .gt-logout{background:rgba(255,255,255,.05);border:1px solid var(--border);color:var(--muted);padding:.3rem .8rem;border-radius:8px;font-size:.8rem;cursor:pointer;font-family:var(--font);transition:all .2s}
  .gt-logout:hover{background:rgba(239,68,68,.1);border-color:rgba(239,68,68,.3);color:#fca5a5}
  .gt-hamburger{display:none;background:none;border:none;color:#fff;font-size:1.3rem;cursor:pointer}

  /* SIDEBAR */
  .gt-sidebar{position:fixed;top:64px;left:0;bottom:0;width:var(--sidebar);background:var(--surface);border-right:1px solid var(--border);overflow-y:auto;z-index:150;transition:transform .3s;padding:1rem 0}
  .gt-sidebar::-webkit-scrollbar{width:4px}
  .gt-sidebar::-webkit-scrollbar-track{background:transparent}
  .gt-sidebar::-webkit-scrollbar-thumb{background:rgba(255,255,255,.1);border-radius:99px}
  .gt-section-label{padding:.5rem 1.25rem;font-size:.68rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:rgba(255,255,255,.25);margin-top:.5rem}
  .gt-link{display:flex;align-items:center;gap:.75rem;padding:.6rem 1.25rem;color:rgba(255,255,255,.5);font-size:.875rem;font-weight:500;transition:all .2s;border-left:3px solid transparent;cursor:pointer;background:none;border-top:none;border-right:none;border-bottom:none;width:100%;text-align:left;font-family:var(--font)}
  .gt-link:hover{background:rgba(255,255,255,.04);color:rgba(255,255,255,.85);border-left-color:rgba(56,189,248,.4)}
  .gt-link.active{background:rgba(56,189,248,.08);color:var(--accent);border-left-color:var(--accent);font-weight:600}
  .gt-link .ico{width:18px;text-align:center;font-size:1rem;flex-shrink:0}

  /* LAYOUT */
  .gt-layout{display:flex;padding-top:64px;min-height:100vh}
  .gt-main{margin-left:var(--sidebar);flex:1;padding:2rem;min-height:calc(100vh - 64px)}

  /* PAGE HEADER */
  .page-header{margin-bottom:1.75rem}
  .page-header h1{font-size:1.5rem;color:#fff;font-weight:700}
  .page-header p{color:var(--muted);margin-top:.2rem;font-size:.88rem}
  .breadcrumb{display:flex;align-items:center;gap:.4rem;font-size:.78rem;color:var(--muted);margin-bottom:.4rem}
  .breadcrumb a{color:var(--accent)}

  /* CARDS */
  .card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem}
  .card-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:1rem;padding-bottom:.75rem;border-bottom:1px solid var(--border)}
  .card-title{font-size:1rem;font-weight:600;color:#fff}
  .mb-2{margin-bottom:1rem}.mb-3{margin-bottom:1.5rem}.mt-2{margin-top:1rem}.mt-3{margin-top:1.5rem}
  .hidden{display:none!important}

  /* BUTTONS */
  .btn{display:inline-flex;align-items:center;gap:.4rem;padding:.55rem 1.25rem;border-radius:8px;border:none;font-size:.875rem;font-weight:600;cursor:pointer;transition:all .2s;font-family:var(--font);white-space:nowrap}
  .btn-primary{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff}
  .btn-primary:hover{transform:translateY(-1px);box-shadow:0 6px 20px rgba(56,189,248,.3)}
  .btn-accent{background:linear-gradient(135deg,#a78bfa,#ec4899);color:#fff}
  .btn-accent:hover{transform:translateY(-1px)}
  .btn-success{background:rgba(34,197,94,.15);color:#4ade80;border:1px solid rgba(34,197,94,.25)}
  .btn-success:hover{background:rgba(34,197,94,.25)}
  .btn-danger{background:rgba(239,68,68,.15);color:#f87171;border:1px solid rgba(239,68,68,.25)}
  .btn-danger:hover{background:rgba(239,68,68,.25)}
  .btn-outline{background:transparent;border:1.5px solid var(--border);color:var(--muted)}
  .btn-outline:hover{border-color:var(--accent);color:var(--accent)}
  .btn-ghost{background:transparent;color:var(--muted)}
  .btn-ghost:hover{background:rgba(255,255,255,.05);color:#fff}
  .btn-sm{padding:.3rem .75rem;font-size:.78rem}
  .btn-lg{padding:.75rem 1.75rem;font-size:1rem}
  .btn-block{width:100%;justify-content:center}
  .btn:disabled{opacity:.4;cursor:not-allowed;transform:none!important}

  /* FORMS */
  .form-group{margin-bottom:1.1rem}
  .form-label{display:block;font-size:.8rem;font-weight:600;color:rgba(255,255,255,.6);margin-bottom:.35rem;letter-spacing:.02em}
  .form-control{width:100%;padding:.65rem .9rem;background:rgba(255,255,255,.04);border:1.5px solid var(--border);border-radius:8px;font-size:.875rem;color:#fff;font-family:var(--font);transition:all .2s;outline:none}
  .form-control::placeholder{color:rgba(255,255,255,.2)}
  .form-control:focus{border-color:var(--accent);background:rgba(56,189,248,.04);box-shadow:0 0 0 3px rgba(56,189,248,.1)}
  select.form-control option{background:#1a2235;color:#fff}
  .form-row{display:grid;grid-template-columns:1fr 1fr;gap:1rem}
  .form-row-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:1rem}
  .form-hint{font-size:.75rem;color:var(--muted);margin-top:.2rem}

  /* BADGES */
  .badge{display:inline-block;padding:.2rem .6rem;border-radius:99px;font-size:.72rem;font-weight:700}
  .badge-low{background:rgba(34,197,94,.12);color:#4ade80;border:1px solid rgba(34,197,94,.2)}
  .badge-moderate{background:rgba(245,158,11,.12);color:#fbbf24;border:1px solid rgba(245,158,11,.2)}
  .badge-high{background:rgba(239,68,68,.12);color:#f87171;border:1px solid rgba(239,68,68,.2)}
  .badge-info{background:rgba(56,189,248,.12);color:#7dd3fc;border:1px solid rgba(56,189,248,.2)}

  /* ALERTS */
  .alert{padding:.75rem 1rem;border-radius:8px;font-size:.85rem;display:flex;align-items:flex-start;gap:.5rem;margin-bottom:1rem}
  .alert-danger{background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.2);color:#fca5a5}
  .alert-success{background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.2);color:#86efac}
  .alert-warning{background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.2);color:#fcd34d}
  .alert-info{background:rgba(56,189,248,.08);border:1px solid rgba(56,189,248,.2);color:#7dd3fc}

  /* STATS */
  .stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:1rem;margin-bottom:1.5rem}
  .stat-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem;display:flex;align-items:center;gap:1rem;position:relative;overflow:hidden}
  .stat-card::before{content:'';position:absolute;top:0;left:0;bottom:0;width:3px;background:linear-gradient(180deg,var(--accent),var(--accent2))}
  .stat-card.danger::before{background:linear-gradient(180deg,var(--danger),#f97316)}
  .stat-card.warning::before{background:linear-gradient(180deg,var(--warning),#f97316)}
  .stat-card.success::before{background:linear-gradient(180deg,var(--success),#10b981)}
  .stat-icon{font-size:1.75rem}
  .stat-info h3{font-size:1.5rem;font-weight:700;color:#fff;line-height:1}
  .stat-info p{font-size:.75rem;color:var(--muted);margin-top:.15rem}

  /* RISK CARDS */
  .risk-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:1rem}
  .risk-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.5rem;text-align:center;position:relative;overflow:hidden;transition:transform .2s}
  .risk-card:hover{transform:translateY(-2px)}
  .risk-card::after{content:'';position:absolute;bottom:0;left:0;right:0;height:3px}
  .risk-card.low::after{background:linear-gradient(90deg,#22c55e,#10b981)}
  .risk-card.moderate::after{background:linear-gradient(90deg,#f59e0b,#f97316)}
  .risk-card.high::after{background:linear-gradient(90deg,#ef4444,#dc2626)}
  .risk-icon{font-size:2.2rem;margin-bottom:.5rem}
  .risk-name{font-size:.75rem;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.06em}
  .risk-pct{font-size:2rem;font-weight:800;line-height:1.1;margin:.3rem 0}
  .risk-pct.low{color:#4ade80}.risk-pct.moderate{color:#fbbf24}.risk-pct.high{color:#f87171}

  /* PROGRESS */
  .progress-wrap{margin-bottom:.75rem}
  .progress-label{display:flex;justify-content:space-between;font-size:.8rem;color:var(--muted);margin-bottom:.3rem}
  .progress-bar-bg{background:rgba(255,255,255,.06);border-radius:99px;height:8px;overflow:hidden}
  .progress-bar-fill{height:100%;border-radius:99px;transition:width 1s cubic-bezier(.4,0,.2,1)}
  .fill-low{background:linear-gradient(90deg,#22c55e,#10b981)}
  .fill-moderate{background:linear-gradient(90deg,#f59e0b,#f97316)}
  .fill-high{background:linear-gradient(90deg,#ef4444,#dc2626)}

  /* TABLE */
  .table-wrap{overflow-x:auto}
  table{width:100%;border-collapse:collapse;font-size:.85rem}
  thead th{background:rgba(255,255,255,.04);color:rgba(255,255,255,.5);padding:.7rem 1rem;text-align:left;font-weight:600;font-size:.75rem;text-transform:uppercase;letter-spacing:.05em;border-bottom:1px solid var(--border)}
  tbody tr{border-bottom:1px solid rgba(255,255,255,.04);transition:background .15s}
  tbody tr:hover{background:rgba(255,255,255,.02)}
  tbody td{padding:.7rem 1rem;color:var(--text)}

  /* MODAL */
  .modal-overlay{position:fixed;inset:0;background:rgba(0,0,0,.7);backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center;z-index:500;padding:1rem}
  .modal{background:var(--surface);border:1px solid var(--border);border-radius:16px;width:100%;max-width:520px;max-height:90vh;overflow-y:auto}
  .modal-header{display:flex;align-items:center;justify-content:space-between;padding:1.25rem 1.5rem;border-bottom:1px solid var(--border)}
  .modal-body{padding:1.5rem}
  .modal-footer{padding:1rem 1.5rem;border-top:1px solid var(--border);display:flex;gap:.75rem;justify-content:flex-end}
  .modal-close{background:none;border:none;font-size:1.2rem;cursor:pointer;color:var(--muted)}

  /* SPINNER */
  .spinner{width:18px;height:18px;border:2px solid rgba(255,255,255,.2);border-top-color:#fff;border-radius:50%;animation:spin .7s linear infinite;display:inline-block}
  @keyframes spin{to{transform:rotate(360deg)}}
  .loading-overlay{position:fixed;inset:0;background:rgba(10,15,30,.85);backdrop-filter:blur(8px);display:flex;flex-direction:column;align-items:center;justify-content:center;z-index:999;gap:1rem}
  .loading-overlay .spinner{width:40px;height:40px;border-width:3px}
  .loading-overlay p{color:var(--accent);font-weight:600}

  /* REC CARDS */
  .rec-card{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:1.25rem 1.5rem;margin-bottom:1rem;border-left:3px solid var(--accent)}
  .rec-card.danger{border-left-color:var(--danger)}
  .rec-card.warning{border-left-color:var(--warning)}
  .rec-card.success{border-left-color:var(--success)}
  .rec-card h4{color:#fff;margin-bottom:.4rem}

  /* STEPPER */
  .stepper{display:flex;align-items:center;margin-bottom:2rem}
  .step{display:flex;flex-direction:column;align-items:center;flex:1;position:relative}
  .step:not(:last-child)::after{content:'';position:absolute;top:18px;left:50%;width:100%;height:2px;background:var(--border);z-index:0}
  .step.done:not(:last-child)::after{background:var(--success)}
  .step-circle{width:36px;height:36px;border-radius:50%;border:2px solid var(--border);background:var(--surface);display:flex;align-items:center;justify-content:center;font-weight:700;font-size:.85rem;z-index:1;transition:all .3s;color:var(--muted)}
  .step.active .step-circle{border-color:var(--accent);background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff}
  .step.done .step-circle{border-color:var(--success);background:var(--success);color:#fff}
  .step-label{font-size:.72rem;margin-top:.4rem;color:var(--muted);text-align:center}
  .step.active .step-label{color:var(--accent);font-weight:600}

  /* TOGGLE BUTTONS */
  .toggle-group{display:flex;gap:.4rem;flex-wrap:wrap}
  .toggle-btn{padding:.3rem .8rem;border-radius:6px;border:1.5px solid var(--border);background:transparent;cursor:pointer;font-size:.8rem;font-weight:600;transition:all .2s;color:var(--muted);font-family:var(--font)}
  .toggle-btn.active{background:linear-gradient(135deg,var(--accent),var(--accent2));color:#fff;border-color:transparent}

  /* MISC */
  .text-center{text-align:center}
  .flex{display:flex}.gap-1{gap:.5rem}.gap-2{gap:1rem}

  @media(max-width:900px){
    .gt-sidebar{transform:translateX(-100%)}
    .gt-sidebar.open{transform:translateX(0)}
    .gt-main{margin-left:0}
    .gt-nav{padding-left:1.5rem}
    .gt-hamburger{display:block}
    .form-row,.form-row-3{grid-template-columns:1fr}
  }
  @media(max-width:600px){
    .stats-grid{grid-template-columns:1fr 1fr}
    .risk-grid{grid-template-columns:1fr 1fr}
    h1{font-size:1.3rem}
  }
  </style>`;

  const links = [
    { href:'/dashboard',       ico:'📊', label:'Dashboard' },
    { href:'/family',          ico:'👨‍👩‍👧', label:'Family History' },
    { href:'/personal',        ico:'👤', label:'Personal Info' },
    { href:'/result',          ico:'🎯', label:'Prediction Result' },
    { href:'/explainability',  ico:'🔍', label:'Explainable AI' },
    { href:'/recommendations', ico:'💊', label:'Recommendations' },
    { href:'/history',         ico:'📋', label:'History' },
    { href:'/profile',         ico:'⚙️', label:'Profile' },
    { href:'/about',           ico:'ℹ️', label:'About' },
  ];

  const sidebarLinks = links.map(l =>
    `<a href="${l.href}" class="gt-link${activePage===l.href?' active':''}">
       <span class="ico">${l.ico}</span>${l.label}
     </a>`
  ).join('');

  const nav = `<nav class="gt-nav">
    <div style="display:flex;align-items:center;gap:.75rem;">
      <button class="gt-hamburger" id="gt-ham">☰</button>
      <div class="gt-nav-brand">🧬 Gene<span>Trace</span></div>
    </div>
    <div class="gt-nav-right">
      <span class="gt-nav-name" id="navbar-name"></span>
      <div class="gt-avatar" id="navbar-avatar">U</div>
      <button class="gt-logout" id="logout-btn">Logout</button>
    </div>
  </nav>`;

  const sidebar = `<aside class="gt-sidebar" id="gt-sidebar">
    <div class="gt-section-label">Main Menu</div>
    ${sidebarLinks}
    <div class="gt-section-label" style="margin-top:1rem;">Account</div>
    <button class="gt-link" id="logout-btn-side"><span class="ico">🚪</span>Logout</button>
  </aside>`;

  document.head.insertAdjacentHTML('beforeend', style);
  document.body.insertAdjacentHTML('afterbegin', nav + '<div class="gt-layout">' + sidebar + '<main class="gt-main" id="gt-main">');
  document.body.insertAdjacentHTML('beforeend', '</main></div>');

  const main = document.getElementById('gt-main');
  Array.from(document.body.children).forEach(el => {
    if (!el.classList?.contains('gt-layout') && el.tagName !== 'NAV' && el.id !== 'gt-loading' && el.id !== 'gt-layout-style') {
      main.appendChild(el);
    }
  });

  document.getElementById('logout-btn')?.addEventListener('click', () => { Auth.clear(); window.location.href = '/login'; });
  document.getElementById('logout-btn-side')?.addEventListener('click', () => { Auth.clear(); window.location.href = '/login'; });

  const ham = document.getElementById('gt-ham');
  const sb  = document.getElementById('gt-sidebar');
  if (ham && sb) {
    ham.addEventListener('click', () => sb.classList.toggle('open'));
    document.addEventListener('click', e => { if (!sb.contains(e.target) && !ham.contains(e.target)) sb.classList.remove('open'); });
  }

  const user = Auth.getUser();
  const avatarEl = document.getElementById('navbar-avatar');
  const nameEl   = document.getElementById('navbar-name');
  if (avatarEl && user) avatarEl.textContent = user.full_name?.charAt(0).toUpperCase() || 'U';
  if (nameEl   && user) nameEl.textContent   = user.full_name?.split(' ')[0] || 'User';
}

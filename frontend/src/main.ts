// Entry point — renders the persistent shell, registers routes, and boots the
// client-side router.

import './styles/global.css';
import { addRoute, setContentElement, navigate, updateActiveNav, updateShell } from './router';
import { render as renderLanding } from './pages/landing';
import { render as renderWorkspace } from './pages/workspace';
import { render as renderModels } from './pages/models';
import { render as renderSimulations } from './pages/simulations';
import { render as renderFinances } from './pages/finances';

export { navigate };
export { showLoadingOverlay, hideLoadingOverlay } from './overlay';

// ---------------------------------------------------------------------------
// Register routes
// ---------------------------------------------------------------------------
addRoute('/', renderLanding);
addRoute('/workspace', renderWorkspace);
addRoute('/workspace/models', renderModels);
addRoute('/workspace/simulations', renderSimulations);
addRoute('/workspace/simulations/:model_id', renderSimulations);
addRoute('/workspace/finances', renderFinances);
addRoute('/workspace/finances/:model_id', renderFinances);

// ---------------------------------------------------------------------------
// Render persistent shell
// ---------------------------------------------------------------------------
const app = document.getElementById('app')!;

app.innerHTML = `
  <!-- Top navigation bar — always visible -->
  <nav id="topnav">
    <a href="/" class="topnav-logo" data-link data-nav="home">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
           fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
        <path d="M4 20c0-8 5-14 16-16C18 12 12 18 4 20z"/>
        <path d="M4 20C8 14 12 11 17 10"/>
      </svg>
      <span>Ferntree</span>
    </a>
  </nav>

  <!-- Shell: sidenav (workspace only) + main content -->
  <div id="shell">
    <nav id="sidenav">
      <a href="/workspace" class="nav-logo" data-link data-href="/workspace">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0" aria-hidden="true">
          <path d="M4 20c0-8 5-14 16-16C18 12 12 18 4 20z"/>
          <path d="M4 20C8 14 12 11 17 10"/>
        </svg>
        <span class="nav-label">Ferntree</span>
      </a>

      <a href="/workspace/models" class="nav-link" data-link data-href="/workspace/models">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
             fill="currentColor" style="flex-shrink:0">
          <path d="M3 13h8V3H3v10zm0 8h8v-6H3v6zm10 0h8V11h-8v10zm0-18v6h8V3h-8z"/>
        </svg>
        <span class="nav-label">Models</span>
      </a>

      <a href="/workspace/simulations" class="nav-link" data-link data-href="/workspace/simulations">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
              fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" style="flex-shrink:0" aria-hidden="true">
          <circle cx="12" cy="12" r="4"/>
          <path d="M12 2.5v2M12 19.5v2M2.5 12h2M19.5 12h2M5.3 5.3l1.4 1.4M17.3 17.3l1.4 1.4M18.7 5.3l-1.4 1.4M6.7 17.3l-1.4 1.4"/>
        </svg>
        <span class="nav-label">Simulations</span>
      </a>

      <a href="/workspace/finances" class="nav-link" data-link data-href="/workspace/finances">
        <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24"
             fill="currentColor" style="flex-shrink:0">
          <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/>
        </svg>
        <span class="nav-label">Finances</span>
      </a>
    </nav>

    <main id="content"></main>
  </div>
`;

// ---------------------------------------------------------------------------
// Wire up the router
// ---------------------------------------------------------------------------
const content = document.getElementById('content')!;
setContentElement(content);

// Intercept all [data-link] clicks — prevent browser navigation, use router.
document.addEventListener('click', (e) => {
  const target = (e.target as HTMLElement).closest<HTMLAnchorElement>('a[data-link]');
  if (!target) return;
  e.preventDefault();
  const href = target.getAttribute('href');
  if (href) navigate(href);
});

// Boot: render the page for the current URL and set initial shell state.
const initialPath = window.location.pathname;
updateShell(initialPath);
updateActiveNav(initialPath);
navigate(initialPath, false);

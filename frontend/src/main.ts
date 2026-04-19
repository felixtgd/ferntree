// Entry point — renders the persistent shell, registers routes, and boots the
// client-side router.

import './styles/global.css';
import { addRoute, setContentElement, navigate } from './router';
import { render as renderWorkspace } from './pages/workspace';
import { render as renderModels } from './pages/models';
import { render as renderSimulations } from './pages/simulations';
import { render as renderFinances } from './pages/finances';

export { navigate };
export { showLoadingOverlay, hideLoadingOverlay } from './overlay';

// ---------------------------------------------------------------------------
// Register routes
// ---------------------------------------------------------------------------
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
  <nav id="sidenav">
    <a href="/workspace" class="nav-logo" data-link data-href="/workspace">
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24"
           fill="currentColor" style="flex-shrink:0">
        <path d="M11 2.05V13h-1a8 8 0 1 0 8 8h-7.95c-.55 0-1.05-.5-1.05-1.05V2.05zM13 2.05V11h8.95c.55 0 1.05.5 1.05 1.05C23 17.08 18.08 22 12 22A10 10 0 0 1 13 2.05z"/>
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
           fill="currentColor" style="flex-shrink:0">
        <path d="M13 2.05v2.02c3.95.49 7 3.85 7 7.93 0 3.21-1.81 6-4.5 7.54L13 17v5h5l-1.22-1.22C19.91 19.07 22 15.76 22 12c0-5.18-3.95-9.45-9-9.95zM11 2.05C5.95 2.55 2 6.82 2 12c0 3.76 2.09 7.07 5.22 8.78L6 22h5v-5l-2.5 2.47C6.81 18 5 15.21 5 12c0-4.08 3.05-7.44 7-7.93V2.05z"/>
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

// Boot: render the page for the current URL.
navigate(window.location.pathname, false);

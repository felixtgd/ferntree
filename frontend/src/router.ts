// Client-side History API router.
// Maps URL patterns to page render functions and handles navigation without
// full page reloads.

export type RouteParams = Record<string, string>;
export type PageRenderer = (
  container: HTMLElement,
  params?: RouteParams,
) => Promise<void>;

// ---------------------------------------------------------------------------
// Route table
// Each entry is a pattern string where `:param` segments are named captures.
// ---------------------------------------------------------------------------
type Route = {
  pattern: RegExp;
  paramNames: string[];
  render: PageRenderer;
};

const routes: Route[] = [];

export function addRoute(pattern: string, render: PageRenderer): void {
  // Convert "/workspace/simulations/:model_id" → named capture regex
  const paramNames: string[] = [];
  const regexStr = pattern
    .replace(/:([a-zA-Z_]+)/g, (_match, name: string) => {
      paramNames.push(name);
      return '([^/]+)';
    })
    .replace(/\//g, '\\/');
  routes.push({ pattern: new RegExp(`^${regexStr}$`), paramNames, render });
}

// ---------------------------------------------------------------------------
// Core navigate — updates the URL bar and renders the matching page.
// ---------------------------------------------------------------------------
let contentEl: HTMLElement | null = null;

export function setContentElement(el: HTMLElement): void {
  contentEl = el;
}

export function navigate(path: string, pushState = true): void {
  // Navigating to the current URL would re-render the page mid-flight and
  // abort any in-progress async render. Skip silently.
  if (pushState && path === window.location.pathname) return;
  if (pushState) {
    history.pushState({}, '', path);
  }
  dispatch(path);
}

function dispatch(path: string): void {
  if (!contentEl) return;

  // Normalise empty path to root
  const normPath = path === '' ? '/' : path;

  for (const route of routes) {
    const match = normPath.match(route.pattern);
    if (match) {
      const params: RouteParams = {};
      route.paramNames.forEach((name, i) => {
        params[name] = match[i + 1] ?? '';
      });
      route.render(contentEl, params).catch((err: unknown) => {
        console.error('Page render error:', err);
        contentEl!.innerHTML = `<p style="padding:2rem;color:red">Failed to load page.</p>`;
      });
      updateActiveNav(normPath);
      updateShell(normPath);
      return;
    }
  }

  // No match — 404 fallback
  contentEl.innerHTML = `<p style="padding:2rem">Page not found: ${path}</p>`;
  updateActiveNav(normPath);
  updateShell(normPath);
}

// ---------------------------------------------------------------------------
// Active nav highlighting
// Top navbar: exact-prefix matching for Home (/), Blog (/blog), Ferntree (/workspace).
// Sidenav: existing startsWith matching for workspace sub-routes.
// ---------------------------------------------------------------------------
export function updateActiveNav(path: string): void {
  // Top navbar links
  document.querySelectorAll<HTMLAnchorElement>('#topnav a[data-nav]').forEach((link) => {
    const nav = link.dataset.nav ?? '';
    let active = false;
    if (nav === 'home') {
      active = path === '/';
    } else if (nav === 'blog') {
      active = path === '/blog' || path.startsWith('/blog/');
    } else if (nav === 'ferntree') {
      active = path === '/ferntree' || path === '/workspace' || path.startsWith('/workspace/');
    }
    link.classList.toggle('active', active);
  });

  // Sidenav links (workspace sub-navigation)
  document.querySelectorAll<HTMLAnchorElement>('#sidenav a.nav-link').forEach((link) => {
    const href = link.dataset.href ?? '';
    link.classList.toggle('active', href !== '' && path.startsWith(href));
  });
}

// ---------------------------------------------------------------------------
// Shell state — show/hide sidenav based on whether we're in /workspace/*.
// ---------------------------------------------------------------------------
export function updateShell(path: string): void {
  const shell = document.getElementById('shell');
  if (!shell) return;
  const inWorkspace = path === '/workspace' || path.startsWith('/workspace/');
  shell.classList.toggle('has-sidenav', inWorkspace);
}

// ---------------------------------------------------------------------------
// Back / Forward button support
// ---------------------------------------------------------------------------
window.addEventListener('popstate', () => {
  dispatch(window.location.pathname);
});

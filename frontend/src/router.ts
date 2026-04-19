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

  // Root redirect
  if (path === '/' || path === '') {
    navigate('/workspace', true);
    return;
  }

  for (const route of routes) {
    const match = path.match(route.pattern);
    if (match) {
      const params: RouteParams = {};
      route.paramNames.forEach((name, i) => {
        params[name] = match[i + 1] ?? '';
      });
      route.render(contentEl, params).catch((err: unknown) => {
        console.error('Page render error:', err);
        contentEl!.innerHTML = `<p style="padding:2rem;color:red">Failed to load page.</p>`;
      });
      updateActiveNav(path);
      return;
    }
  }

  // No match — 404 fallback
  contentEl.innerHTML = `<p style="padding:2rem">Page not found: ${path}</p>`;
}

// ---------------------------------------------------------------------------
// Active nav highlighting — uses startsWith so sub-routes stay highlighted.
// ---------------------------------------------------------------------------
function updateActiveNav(path: string): void {
  document.querySelectorAll<HTMLAnchorElement>('#sidenav a.nav-link').forEach((link) => {
    const href = link.dataset.href ?? '';
    link.classList.toggle('active', href !== '' && path.startsWith(href));
  });
}

// ---------------------------------------------------------------------------
// Back / Forward button support
// ---------------------------------------------------------------------------
window.addEventListener('popstate', () => {
  dispatch(window.location.pathname);
});

// Loading overlay helpers — shared across all page modules.
// The overlay HTML lives in index.html (outside #app) and is never overwritten.

export function showLoadingOverlay(message: string): void {
  const overlay = document.getElementById('loading-overlay')!;
  const msg = overlay.querySelector<HTMLElement>('.loading-message')!;
  msg.textContent = message;
  overlay.style.display = 'flex';
}

export function hideLoadingOverlay(): void {
  const overlay = document.getElementById('loading-overlay')!;
  overlay.style.display = 'none';
}

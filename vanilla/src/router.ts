// Client-side router — TODO: Phase 3
export type RouteParams = Record<string, string>;
export type PageRenderer = (container: HTMLElement, params?: RouteParams) => Promise<void>;

// placeholder — will be implemented in Phase 3
export function navigate(_path: string): void {
  // no-op placeholder
}

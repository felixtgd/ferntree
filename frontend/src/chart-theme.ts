/**
 * Shared chart theme helpers for the Tinkerer's Grid design system.
 */

export function cssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

export function tooltipTheme() {
  return {
    backgroundColor: cssVar('--bg-surface'),
    titleColor: cssVar('--text-primary'),
    bodyColor: cssVar('--text-secondary'),
    borderColor: cssVar('--border-metal'),
    borderWidth: 1,
  };
}

export function scaleTheme() {
  return {
    ticks: { color: cssVar('--text-secondary') },
    grid: { color: cssVar('--border-metal') },
  };
}

export function legendLabelTheme() {
  return {
    color: cssVar('--text-primary'),
  };
}

export const chartTokens = {
  get copperRaw() {
    return cssVar('--copper-raw');
  },
  get copperHover() {
    return cssVar('--copper-hover');
  },
  get copperOxidized() {
    return cssVar('--copper-oxidized');
  },
  get dangerRed() {
    return cssVar('--danger-red');
  },
  get borderMetal() {
    return cssVar('--border-metal');
  },
  get textSecondary() {
    return cssVar('--text-secondary');
  },
  get textPrimary() {
    return cssVar('--text-primary');
  },
  get bgSurface() {
    return cssVar('--bg-surface');
  },
};

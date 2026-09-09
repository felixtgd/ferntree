/**
 * Shared chart theme helpers for the refined dark design system.
 */

export function cssVar(name: string): string {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

export function tooltipTheme() {
  return {
    backgroundColor: cssVar('--bg-surface'),
    titleColor: cssVar('--text-primary'),
    bodyColor: cssVar('--text-secondary'),
    borderColor: cssVar('--border-strong'),
    borderWidth: 1,
  };
}

export function scaleTheme() {
  return {
    ticks: { color: cssVar('--text-secondary') },
    grid: { color: cssVar('--border-strong') },
  };
}

export function legendLabelTheme() {
  return {
    color: cssVar('--text-primary'),
  };
}

export const chartTokens = {
  get accent() {
    return cssVar('--accent');
  },
  get accentHover() {
    return cssVar('--accent-hover');
  },
  get success() {
    return cssVar('--success');
  },
  get danger() {
    return cssVar('--danger');
  },
  get pvCost() {
    return cssVar('--chart-pv-cost');
  },
  get batteryCost() {
    return cssVar('--chart-battery-cost');
  },
  get costSavings() {
    return cssVar('--chart-cost-savings');
  },
  get feedIn() {
    return cssVar('--chart-feed-in');
  },
  get operationCost() {
    return cssVar('--chart-operation-cost');
  },
  get loan() {
    return cssVar('--chart-loan');
  },
  get borderStrong() {
    return cssVar('--border-strong');
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

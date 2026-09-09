// Root landing page — rendered at /.

import { RouteParams } from '../router';

export async function render(
  container: HTMLElement,
  _params?: RouteParams,
): Promise<void> {
  container.innerHTML = `
    <div class="dontblackout-landing">
      <section class="dbo-hero">
        <div class="dbo-hero-inner">
          <p class="dbo-dont">DON'T</p>
          <p class="dbo-blackout">BLACKOUT</p>
          <p class="dbo-tagline">A tinkerer's guide to energy</p>
          <a href="/workspace" class="dbo-start" data-link>Start</a>
        </div>
      </section>
    </div>
  `;
}

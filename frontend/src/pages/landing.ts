// Root landing page — rendered at /.

import { RouteParams } from '../router';

export async function render(
  container: HTMLElement,
  _params?: RouteParams,
): Promise<void> {
  container.innerHTML = `
    <div class="dontblackout-landing">

      <!-- Dark hero -->
      <section class="dbo-hero">
        <div class="dbo-hero-inner">
          <p class="dbo-dont">DON'T</p>
          <p class="dbo-blackout">BLACKOUT</p>
          <p class="dbo-tagline">A tinkerer's guide to energy</p>
        </div>
      </section>

      <!-- Project cards -->
      <section class="dbo-projects">
        <div class="dbo-project-grid">

          <a href="/ferntree" class="card dbo-project-card" data-link>
            <div class="dbo-project-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"
                   fill="currentColor" aria-hidden="true">
                <path d="M11 2.05V13h-1a8 8 0 1 0 8 8h-7.95c-.55 0-1.05-.5-1.05-1.05V2.05zM13 2.05V11h8.95c.55 0 1.05.5 1.05 1.05C23 17.08 18.08 22 12 22A10 10 0 0 1 13 2.05z"/>
              </svg>
            </div>
            <h2 class="dbo-project-title">Ferntree</h2>
            <p class="dbo-project-desc">
              PV simulation and financial analysis for rooftop solar systems.
              Model your setup, size your battery, and stress-test the economics.
            </p>
            <span class="dbo-project-link">
              Explore Ferntree
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                   fill="currentColor" aria-hidden="true">
                <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6z"/>
              </svg>
            </span>
          </a>

          <a href="/blog" class="card dbo-project-card" data-link>
            <div class="dbo-project-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24"
                   fill="currentColor" aria-hidden="true">
                <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14H7v-2h7v2zm3-4H7v-2h10v2zm0-4H7V7h10v2z"/>
              </svg>
            </div>
            <h2 class="dbo-project-title">Blog</h2>
            <p class="dbo-project-desc">
              Articles on energy systems, power grid topics, simulation methodology,
              and the economics of the energy transition.
            </p>
            <span class="dbo-project-link">
              Read the blog
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                   fill="currentColor" aria-hidden="true">
                <path d="M8.59 16.59L13.17 12 8.59 7.41 10 6l6 6-6 6z"/>
              </svg>
            </span>
          </a>

        </div>
      </section>

    </div>
  `;
}

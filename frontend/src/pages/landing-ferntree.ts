// Ferntree product landing page — rendered at /ferntree.

import { RouteParams } from '../router';

export async function render(
  container: HTMLElement,
  _params?: RouteParams,
): Promise<void> {
  container.innerHTML = `
    <div class="landing">

      <!-- Hero -->
      <section class="landing-hero">
        <div class="landing-hero-inner">
          <div class="landing-hero-badge">Open-source PV simulation</div>
          <h1 class="landing-hero-title">Model your solar system.<br>Understand the numbers.</h1>
          <p class="landing-hero-sub">
            Ferntree runs a full 8&thinsp;760-hour simulation of your photovoltaic system,
            giving you accurate self-consumption rates, battery sizing guidance, and
            lifetime financial projections — all in your browser.
          </p>
          <div class="landing-hero-actions">
            <a href="/workspace" class="btn landing-cta-primary" data-link>
              Launch Ferntree
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24"
                   fill="currentColor" aria-hidden="true">
                <path d="M8 5v14l11-7z"/>
              </svg>
            </a>
            <a href="/blog" class="btn btn-outline" data-link>
              Read the Blog
            </a>
          </div>
        </div>
      </section>

      <!-- Features -->
      <section class="landing-features">
        <h2 class="landing-section-title">What Ferntree does</h2>
        <div class="landing-feature-grid">

          <div class="card landing-feature-card">
            <div class="landing-feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
                <path d="M12 7c-2.76 0-5 2.24-5 5s2.24 5 5 5 5-2.24 5-5-2.24-5-5-5zM2 13h2c.55 0 1-.45 1-1s-.45-1-1-1H2c-.55 0-1 .45-1 1s.45 1 1 1zm18 0h2c.55 0 1-.45 1-1s-.45-1-1-1h-2c-.55 0-1 .45-1 1s.45 1 1 1zM11 2v2c0 .55.45 1 1 1s1-.45 1-1V2c0-.55-.45-1-1-1s-1 .45-1 1zm0 18v2c0 .55.45 1 1 1s1-.45 1-1v-2c0-.55-.45-1-1-1s-1 .45-1 1zM5.99 4.58c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0s.39-1.03 0-1.41L5.99 4.58zm12.37 12.37c-.39-.39-1.03-.39-1.41 0-.39.39-.39 1.03 0 1.41l1.06 1.06c.39.39 1.03.39 1.41 0 .39-.39.39-1.03 0-1.41l-1.06-1.06zm1.06-10.96c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06zM7.05 18.36c.39-.39.39-1.03 0-1.41-.39-.39-1.03-.39-1.41 0l-1.06 1.06c-.39.39-.39 1.03 0 1.41s1.03.39 1.41 0l1.06-1.06z"/>
              </svg>
            </div>
            <h3 class="landing-feature-title">PV Simulation</h3>
            <p class="landing-feature-desc">
              Hourly irradiance data from PVGIS combined with your panel specs and location.
              Get a full year of generation output in seconds.
            </p>
          </div>

          <div class="card landing-feature-card">
            <div class="landing-feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
                <path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4zm-1.67 9h-2v2h-1v-2H9v-1h2v-2h1v2h2v1z"/>
              </svg>
            </div>
            <h3 class="landing-feature-title">Battery Modelling</h3>
            <p class="landing-feature-desc">
              Simulate charge and discharge across all 8&thinsp;760 hours. Understand how
              battery capacity affects self-consumption and grid dependence.
            </p>
          </div>

          <div class="card landing-feature-card">
            <div class="landing-feature-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="28" height="28" viewBox="0 0 24 24" fill="currentColor">
                <path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/>
              </svg>
            </div>
            <h3 class="landing-feature-title">Financial Analysis</h3>
            <p class="landing-feature-desc">
              Compute LCOE, payback period, and lifetime savings. Adjust tariffs,
              system costs, and discount rates to stress-test your investment.
            </p>
          </div>

        </div>
      </section>

      <!-- CTA strip -->
      <section class="landing-cta-strip">
        <h2 class="landing-cta-strip-title">Ready to run your first simulation?</h2>
        <p class="landing-cta-strip-sub">
          No account required. Create a model, run the simulation, and explore the results in minutes.
        </p>
        <a href="/workspace" class="btn btn-blue" data-link>Get started</a>
      </section>

    </div>
  `;
}

// Workspace home page — three workflow step cards linking to Models,
// Simulations, and Finances.

export async function render(container: HTMLElement, _params?: Record<string, string>): Promise<void> {
  container.innerHTML = `
    <div class="workspace-home">
      <div class="workflow-row">

        <a href="/workspace/models" class="workflow-card" data-link data-href="/workspace/models">
          <div class="workflow-badge">1</div>
          <h3 class="workflow-title">Models</h3>
          <p class="workflow-desc">Design your energy system. You can create up to 5 models.</p>
        </a>

        <div class="workflow-arrow" aria-hidden="true">→</div>

        <a href="/workspace/simulations" class="workflow-card" data-link data-href="/workspace/simulations">
          <div class="workflow-badge">2</div>
          <h3 class="workflow-title">Simulations</h3>
          <p class="workflow-desc">Simulate the energy system and examine its operation.</p>
        </a>

        <div class="workflow-arrow" aria-hidden="true">→</div>

        <a href="/workspace/finances" class="workflow-card" data-link data-href="/workspace/finances">
          <div class="workflow-badge">3</div>
          <h3 class="workflow-title">Finances</h3>
          <p class="workflow-desc">Analyze the financial performance of your system.</p>
        </a>

      </div>
    </div>
  `;
}

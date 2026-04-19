// simulations page (also handles /workspace/simulations/:model_id) — TODO: implement in Phase 6
export async function render(container: HTMLElement, params?: Record<string, string>): Promise<void> {
  const model_id = params?.model_id ?? null;
  container.innerHTML = `<p style="padding:2rem">Simulations${model_id ? ` — model: ${model_id}` : ''} — coming soon</p>`;
}

// finances page (also handles /workspace/finances/:model_id) — TODO: implement in Phase 7
export async function render(container: HTMLElement, params?: Record<string, string>): Promise<void> {
  const model_id = params?.model_id ?? null;
  container.innerHTML = `<p style="padding:2rem">Finances${model_id ? ` — model: ${model_id}` : ''} — coming soon</p>`;
}

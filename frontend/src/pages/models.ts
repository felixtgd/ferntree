// Models page — /workspace/models
// Fetches models, renders model cards, Create Model dialog with Zod validation.

import { fetchModels, submitModel, deleteModel, runSimulation, geocodeLocation } from '../api';
import { navigate } from '../router';
import { showLoadingOverlay, hideLoadingOverlay } from '../overlay';
import { ModelData } from '../types';
import { z } from 'zod';

// ---------------------------------------------------------------------------
// Zod schema (mirrors frontend/app/utils/definitions.ts ModelDataSchema)
// ---------------------------------------------------------------------------
const ModelDataSchema = z.object({
  model_name: z.string()
    .min(1, { message: 'Please specify a model name' })
    .max(100, { message: 'Model name must be at most 100 characters long' }),
  location: z.string()
    .min(1, { message: 'Please specify a location' })
    .max(100, { message: 'Location must be at most 100 characters long' }),
  roof_incl: z.coerce.number()
    .gte(0, { message: 'Must be at least 0°' })
    .lte(90, { message: 'Must be at most 90°' }),
  roof_azimuth: z.coerce.number()
    .gte(-180, { message: 'Must be at least -180°' })
    .lte(180, { message: 'Must be at most 180°' }),
  electr_cons: z.coerce.number()
    .gte(0, { message: 'Must be at least 0 kWh' })
    .lte(100000, { message: 'Must be at most 100,000 kWh' }),
  peak_power: z.coerce.number()
    .gte(0, { message: 'Must be at least 0 kWp' })
    .lte(100000, { message: 'Must be at most 100,000 kWp' }),
  battery_cap: z.coerce.number()
    .gte(0, { message: 'Must be at least 0 kWh' })
    .lte(100000, { message: 'Must be at most 100,000 kWh' }),
});

// ---------------------------------------------------------------------------
// SVG icons (inline, sized 18×18)
// ---------------------------------------------------------------------------
const icons = {
  home: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M10 20v-6h4v6h5v-8h3L12 3 2 12h3v8z"/></svg>`,
  roof: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M4 12l1.41-1.41L11 16.17V4h2v12.17l5.58-5.59L20 12l-8 8-8-8z" transform="rotate(180,12,12)"/></svg>`,
  compass: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm-1-13l-3 7 7-3 3-7-7 3z"/></svg>`,
  bulb: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z"/></svg>`,
  sun: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M6.76 4.84l-1.8-1.79-1.41 1.41 1.79 1.79 1.42-1.41zM4 10.5H1v2h3v-2zm9-9.95h-2V3.5h2V.55zm7.45 3.91l-1.41-1.41-1.79 1.79 1.41 1.41 1.79-1.79zm-3.21 13.7l1.79 1.8 1.41-1.41-1.8-1.79-1.4 1.4zM20 10.5v2h3v-2h-3zm-8-5c-3.31 0-6 2.69-6 6s2.69 6 6 6 6-2.69 6-6-2.69-6-6-6zm-1 16.95h2V19.5h-2v2.95zm-7.45-3.91l1.41 1.41 1.79-1.8-1.41-1.41-1.79 1.8z"/></svg>`,
  battery: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M15.67 4H14V2h-4v2H8.33C7.6 4 7 4.6 7 5.33v15.33C7 21.4 7.6 22 8.33 22h7.33c.74 0 1.34-.6 1.34-1.33V5.33C17 4.6 16.4 4 15.67 4zM13 18h-2v-2h2v2zm0-4h-2V9h2v5z"/></svg>`,
  play: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M8 5v14l11-7z"/></svg>`,
  eye: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>`,
  finance: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M11.8 10.9c-2.27-.59-3-1.2-3-2.15 0-1.09 1.01-1.85 2.7-1.85 1.78 0 2.44.85 2.5 2.1h2.21c-.07-1.72-1.12-3.3-3.21-3.81V3h-3v2.16c-1.94.42-3.5 1.68-3.5 3.61 0 2.31 1.91 3.46 4.7 4.13 2.5.6 3 1.48 3 2.41 0 .69-.49 1.79-2.7 1.79-2.06 0-2.87-.92-2.98-2.1h-2.2c.12 2.19 1.76 3.42 3.68 3.83V21h3v-2.15c1.95-.37 3.5-1.5 3.5-3.55 0-2.84-2.43-3.81-4.7-4.4z"/></svg>`,
  delete: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/></svg>`,
  save: `<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M17 3H5c-1.11 0-2 .9-2 2v14c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V7l-4-4zm-5 16c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3zm3-10H5V5h10v4z"/></svg>`,
  tag: `<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor"><path d="M21.41 11.58l-9-9C12.05 2.22 11.55 2 11 2H4c-1.1 0-2 .9-2 2v7c0 .55.22 1.05.59 1.42l9 9c.36.36.86.58 1.41.58.55 0 1.05-.22 1.41-.59l7-7c.37-.36.59-.86.59-1.41 0-.55-.23-1.06-.59-1.42zM5.5 7C4.67 7 4 6.33 4 5.5S4.67 4 5.5 4 7 4.67 7 5.5 6.33 7 5.5 7z"/></svg>`,
};

// ---------------------------------------------------------------------------
// HTML builders
// ---------------------------------------------------------------------------
function modelCardHTML(m: ModelData): string {
  const locationDisplay = m.coordinates?.display_name ?? m.location;
  const hasSim = !!m.sim_id;
  const mid = m.model_id!;

  const buttons = hasSim
    ? `
      <button class="btn btn-green model-btn" data-action="view-sim" data-model-id="${mid}">
        ${icons.eye} View Simulation Results
      </button>
      <button class="btn btn-orange model-btn" data-action="go-fin" data-model-id="${mid}">
        ${icons.finance} Go to Finances
      </button>`
    : `
      <button class="btn btn-blue model-btn" data-action="run-sim" data-model-id="${mid}">
        ${icons.play} Run Simulation
      </button>`;

  return `
    <div class="model-card card" data-model-id="${mid}">
      <div class="card-header"></div>
      <div class="card-body">
        <h2 class="model-card-title">${m.model_name}</h2>
        <div class="model-params">
          <ul class="param-list">
            <li class="param-row">
              <span class="param-label">${icons.home} Location</span>
              <span class="param-value truncate" title="${locationDisplay}">${locationDisplay}</span>
            </li>
            <li class="param-row">
              <span class="param-label">${icons.roof} Roof inclination</span>
              <span class="param-value">${m.roof_incl}°</span>
            </li>
            <li class="param-row">
              <span class="param-label">${icons.compass} Roof orientation</span>
              <span class="param-value">${m.roof_azimuth}°</span>
            </li>
          </ul>
          <ul class="param-list">
            <li class="param-row">
              <span class="param-label">${icons.bulb} Consumption</span>
              <span class="param-value">${m.electr_cons} kWh</span>
            </li>
            <li class="param-row">
              <span class="param-label">${icons.sun} PV peak power</span>
              <span class="param-value">${m.peak_power} kWp</span>
            </li>
            <li class="param-row">
              <span class="param-label">${icons.battery} Battery capacity</span>
              <span class="param-value">${m.battery_cap} kWh</span>
            </li>
          </ul>
        </div>
        <div class="model-actions">
          ${buttons}
          <button class="btn btn-red model-btn" data-action="delete" data-model-id="${mid}">
            ${icons.delete} Delete Model
          </button>
        </div>
      </div>
    </div>`;
}

function emptyStateHTML(): string {
  return `
    <div class="empty-state">
      <svg class="empty-arrow" fill="none" viewBox="0 0 100 50" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1"
              d="M0 35 C45 35, 85 25, 95 5 L89 10 M95 5 L93 13"/>
        <text x="1" y="45" fill="currentColor" font-size="4" font-weight="300" stroke-width="0.2">
          Start by creating a model
        </text>
      </svg>
    </div>`;
}

function createModelDialogHTML(): string {
  return `
    <dialog id="create-model-dialog">
      <div class="dialog-header">
        <h2>Create a new model</h2>
        <button class="btn btn-outline" id="dialog-close-btn">Close</button>
      </div>
      <div class="dialog-body">
        <form id="create-model-form">

          <div class="form-group">
            <label class="form-label" for="f-model_name">
              <span class="field-icon">${icons.tag}</span> Model name
            </label>
            <input class="form-input" id="f-model_name" name="model_name"
                   type="text" placeholder="Enter model name" required />
            <span class="form-error" id="err-model_name"></span>
          </div>

          <div class="form-group">
            <label class="form-label" for="f-location">
              <span class="field-icon">${icons.home}</span> Location
            </label>
            <input class="form-input" id="f-location" name="location"
                   type="text" placeholder="Enter location" required />
            <span class="form-error" id="err-location"></span>
          </div>

          <div class="form-group">
            <label class="form-label" for="f-roof_incl">
              <span class="field-icon">${icons.roof}</span> Roof inclination
            </label>
            <select class="form-input" id="f-roof_incl" name="roof_incl" required>
              <option value="">Select inclination</option>
              <option value="0">0°</option>
              <option value="30">30°</option>
              <option value="45">45°</option>
            </select>
            <span class="form-error" id="err-roof_incl"></span>
          </div>

          <div class="form-group">
            <label class="form-label" for="f-roof_azimuth">
              <span class="field-icon">${icons.compass}</span> Roof orientation
            </label>
            <select class="form-input" id="f-roof_azimuth" name="roof_azimuth" required>
              <option value="">Select orientation</option>
              <option value="0">South</option>
              <option value="-45">South-East</option>
              <option value="45">South-West</option>
              <option value="-90">East</option>
              <option value="90">West</option>
              <option value="-135">North-East</option>
              <option value="135">North-West</option>
              <option value="180">North</option>
            </select>
            <span class="form-error" id="err-roof_azimuth"></span>
          </div>

          <div class="form-group">
            <label class="form-label" for="f-electr_cons">
              <span class="field-icon">${icons.bulb}</span>
              Electricity consumption <span class="unit-hint">kWh/a</span>
            </label>
            <input class="form-input" id="f-electr_cons" name="electr_cons"
                   type="number" step="1"
                   placeholder="Set annual consumption in kWh, e.g. 3,000" required />
            <span class="form-error" id="err-electr_cons"></span>
          </div>

          <div class="form-group">
            <label class="form-label" for="f-peak_power">
              <span class="field-icon">${icons.sun}</span>
              PV peak power <span class="unit-hint">kWp</span>
            </label>
            <input class="form-input" id="f-peak_power" name="peak_power"
                   type="number" step="0.1"
                   placeholder="Set peak power in kWp, e.g. 10" required />
            <span class="form-error" id="err-peak_power"></span>
          </div>

          <div class="form-group">
            <label class="form-label" for="f-battery_cap">
              <span class="field-icon">${icons.battery}</span>
              Battery capacity <span class="unit-hint">kWh</span>
            </label>
            <input class="form-input" id="f-battery_cap" name="battery_cap"
                   type="number" step="0.1"
                   placeholder="Set capacity in kWh, e.g. 10" required />
            <span class="form-error" id="err-battery_cap"></span>
          </div>

          <div class="dialog-footer">
            <button class="btn btn-blue" type="submit" id="save-model-btn">
              ${icons.save} Save Model
            </button>
          </div>
        </form>
      </div>
    </dialog>`;
}

// ---------------------------------------------------------------------------
// Render model list section only (re-used after delete / create)
// ---------------------------------------------------------------------------
function renderModelList(container: HTMLElement, models: ModelData[]): void {
  const listEl = container.querySelector<HTMLElement>('#model-list')!;
  listEl.innerHTML = models.length === 0
    ? emptyStateHTML()
    : models.map(modelCardHTML).join('');
}

// ---------------------------------------------------------------------------
// Show / clear field errors
// ---------------------------------------------------------------------------
function clearErrors(form: HTMLFormElement): void {
  form.querySelectorAll<HTMLSpanElement>('.form-error').forEach(el => { el.textContent = ''; });
  form.querySelectorAll<HTMLElement>('.form-input').forEach(el => el.classList.remove('error'));
}

function showFieldError(fieldName: string, message: string): void {
  const errEl = document.getElementById(`err-${fieldName}`);
  const inputEl = document.getElementById(`f-${fieldName}`);
  if (errEl) errEl.textContent = message;
  if (inputEl) inputEl.classList.add('error');
}

// ---------------------------------------------------------------------------
// Main render entry point
// ---------------------------------------------------------------------------
export async function render(container: HTMLElement, _params?: Record<string, string>): Promise<void> {
  // Render the shell immediately so the page is never blank.
  container.innerHTML = `
    <div class="models-page">
      <h1 class="page-heading">Models</h1>
      <div class="models-header">
        <button class="btn btn-blue" id="create-model-btn" disabled title="Loading...">
          + Create Model
        </button>
      </div>
      <div id="model-list">
        <p class="status-text">Loading models…</p>
      </div>
    </div>
    ${createModelDialogHTML()}
  `;

  let models: ModelData[];
  try {
    models = await fetchModels();
  } catch (err) {
    console.error('Failed to fetch models:', err);
    document.querySelector<HTMLElement>('#model-list')!.innerHTML =
      `<p class="status-text status-text--error">Failed to load models. Is the backend running?</p>`;
    return;
  }

  renderModelList(container, models);

  const dialog = container.querySelector<HTMLDialogElement>('#create-model-dialog')!;
  const createBtn = container.querySelector<HTMLButtonElement>('#create-model-btn')!;

  // Set initial Create Model button state based on loaded model count.
  createBtn.disabled = models.length >= 5;
  createBtn.title = models.length >= 5
    ? 'You have reached the maximum number of models. Delete a model to create a new one.'
    : 'Create a new model';
  const closeBtn = container.querySelector<HTMLButtonElement>('#dialog-close-btn')!;
  const form = container.querySelector<HTMLFormElement>('#create-model-form')!;
  const saveBtn = container.querySelector<HTMLButtonElement>('#save-model-btn')!;

  // ---- Open / close dialog ------------------------------------------------
  createBtn.addEventListener('click', () => dialog.showModal());
  closeBtn.addEventListener('click', () => {
    dialog.close();
    form.reset();
    clearErrors(form);
  });
  // Prevent Escape key from closing the dialog (static dialog behaviour).
  dialog.addEventListener('cancel', (e) => e.preventDefault());

  // ---- Form submission -----------------------------------------------------
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    clearErrors(form);

    const data = Object.fromEntries(new FormData(form));
    const result = ModelDataSchema.safeParse(data);

    if (!result.success) {
      const fieldErrors = result.error.flatten().fieldErrors;
      for (const [field, msgs] of Object.entries(fieldErrors)) {
        if (msgs && msgs.length > 0) showFieldError(field, msgs[0]);
      }
      return;
    }

    // Geocode location
    saveBtn.disabled = true;
    const coords = await geocodeLocation(result.data.location);
    if (!coords) {
      showFieldError('location', 'Location could not be validated. Please check if the address is correct.');
      saveBtn.disabled = false;
      return;
    }

    // Submit to backend
    try {
      const timestamp = new Date().toISOString();
      await submitModel({ ...result.data, coordinates: coords, time_created: timestamp });

      dialog.close();
      form.reset();
      // Re-fetch and re-render model list
      models = await fetchModels();
      renderModelList(container, models);
      // Update Create Model button state
      createBtn.disabled = models.length >= 5;
      createBtn.title = models.length >= 5
        ? 'You have reached the maximum number of models. Delete a model to create a new one.'
        : 'Create a new model';
    } catch (err) {
      console.error('Failed to submit model:', err);
      showFieldError('model_name', 'Failed to save model. Please try again.');
    } finally {
      saveBtn.disabled = false;
    }
  });

  // ---- Model card actions (event delegation) --------------------------------
  container.addEventListener('click', async (e) => {
    const btn = (e.target as HTMLElement).closest<HTMLButtonElement>('[data-action]');
    if (!btn) return;

    const action = btn.dataset.action!;
    const modelId = btn.dataset.modelId!;

    if (action === 'view-sim') {
      navigate(`/workspace/simulations/${modelId}`);
      return;
    }

    if (action === 'go-fin') {
      navigate(`/workspace/finances/${modelId}`);
      return;
    }

    if (action === 'delete') {
      try {
        await deleteModel(modelId);
        models = models.filter(m => m.model_id !== modelId);
        renderModelList(container, models);
        createBtn.disabled = models.length >= 5;
        createBtn.title = models.length >= 5
          ? 'You have reached the maximum number of models. Delete a model to create a new one.'
          : 'Create a new model';
      } catch (err) {
        console.error('Failed to delete model:', err);
      }
      return;
    }

    if (action === 'run-sim') {
      showLoadingOverlay('Simulating your energy system ...');
      try {
        const res = await runSimulation(modelId);
        if (res.run_successful) {
          hideLoadingOverlay();
          navigate(`/workspace/simulations/${modelId}`);
        } else {
          hideLoadingOverlay();
          // Re-render in place on failure
          models = await fetchModels();
          renderModelList(container, models);
        }
      } catch (err) {
        console.error('Simulation failed:', err);
        hideLoadingOverlay();
        models = await fetchModels();
        renderModelList(container, models);
      }
    }
  });
}

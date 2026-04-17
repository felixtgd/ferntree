# NextJS Frontend — Behavioural Checklist

Use this checklist to verify that a replacement frontend behaves identically to the NextJS MVP.
Each item describes an observable outcome — something a tester can confirm by looking at or interacting with the running app.

---

## 1. Navigation & Layout

### Sidenav (visible on all `/workspace` routes)
- [ ] Sidenav is a vertical left-hand sidebar visible on every workspace page
- [ ] Top of sidenav contains the text "Ferntree" as a link; clicking it navigates to `/workspace`
- [ ] Three navigation links are listed below the logo: **Models**, **Simulations**, **Finances**
- [ ] Each link shows an icon; on screens `md` and wider, a text label is shown alongside the icon; on narrow screens, only the icon is shown
 - [ ] The active link is highlighted with a light blue background and blue text; matching uses `startsWith` so any sub-route keeps the parent link highlighted
   - `/workspace/models` and `/workspace/models/anything` both highlight Models
   - `/workspace/simulations` and `/workspace/simulations/[model_id]` both highlight Simulations
   - `/workspace/finances` and `/workspace/finances/[model_id]` both highlight Finances

### Root redirect
- [ ] Navigating to `/` immediately redirects to `/workspace` with no intermediate page rendered

---

## 2. Workspace Home (`/workspace`)

- [ ] Page renders three cards arranged horizontally on `md`+ screens, stacked vertically on narrow screens
- [ ] Between each pair of cards on desktop, a blue `→` arrow is visible; arrows are hidden on mobile
- [ ] **Card 1 — Models**: numbered badge "1"; heading "Models"; description "Design your energy system. You can create up to 5 models."; clicking navigates to `/workspace/models`
- [ ] **Card 2 — Simulations**: numbered badge "2"; heading "Simulations"; description "Simulate the energy system and examine its operation."; clicking navigates to `/workspace/simulations`
- [ ] **Card 3 — Finances**: numbered badge "3"; heading "Finances"; description "Analyze the financial performance of your system."; clicking navigates to `/workspace/finances`
- [ ] Each card starts with a light blue background (`bg-blue-100`) and changes to a darker blue (`bg-blue-300`) on hover
- [ ] No data is fetched on this page; no loading state exists

---

## 3. Models (`/workspace/models`)

### Page structure
- [ ] Page heading "Models" is rendered at the top, centred
- [ ] A "Create Model" button is visible in the top-right area

### Empty state (no models exist)
- [ ] When no models exist, an SVG arrow pointing upper-right is rendered with the text "Start by creating a model" overlaid
- [ ] No model cards are rendered

### Model card (one per model)
- [ ] Each model renders a card with the model name as a centred heading
- [ ] Card shows two columns of three parameters each:
  - Left column: Location (shows `coordinates.display_name` if geocoding succeeded, otherwise the raw input string), Roof inclination in degrees (`{n}°`), Roof orientation in degrees (`{n}°`)
  - Right column: Annual consumption in kWh (`{n} kWh`), PV peak power in kWp (`{n} kWp`), Battery capacity in kWh (`{n} kWh`)
- [ ] Each parameter row has an icon to its left
- [ ] The location value has a native browser tooltip (via `title` attribute) showing the full location display name on hover

#### Buttons on model card — no simulation run yet
- [ ] A blue **Run Simulation** button (play icon) is shown
- [ ] A red **Delete Model** button (bin icon) is shown
- [ ] No View Results or Go to Finances buttons are shown

#### Buttons on model card — simulation exists
- [ ] A green **View Simulation Results** button (eye icon) is shown; clicking navigates to `/workspace/simulations/{model_id}`
- [ ] An orange **Go to Finances** button (dollar-arrows icon) is shown; clicking navigates to `/workspace/finances/{model_id}`
- [ ] A red **Delete Model** button (bin icon) is shown
- [ ] No Run Simulation button is shown

#### Run Simulation button behaviour
- [ ] Clicking **Run Simulation** immediately shows a full-screen loading overlay with the message "Simulating your energy system ..." and a blue spinning circle
- [ ] The overlay remains visible until the backend responds
- [ ] On success, the app navigates to `/workspace/simulations/{model_id}`
- [ ] On failure, the page refreshes in place (no navigation)

#### Delete Model button behaviour
- [ ] Clicking **Delete** removes the model; the model list re-renders without it
- [ ] No confirmation dialog is shown before deletion

### Create Model button
- [ ] When fewer than 5 models exist: button is enabled
- [ ] When 5 models exist: button is disabled; hovering shows tooltip "You have reached the maximum number of models. Delete a model to create a new one."

### Create Model dialog
- [ ] Clicking the enabled "Create Model" button opens a modal dialog
- [ ] Dialog header reads "Create a new model" and contains a "Close" button; clicking "Close" dismisses the dialog
- [ ] Clicking outside the dialog does **not** close it (static dialog)

### Model form (inside dialog)
- [ ] Form contains seven fields:

| Field | Input type | Placeholder / options |
|---|---|---|
| Model name | Text input | "Enter model name" |
| Location | Text input | "Enter location" |
| Roof inclination | Dropdown | 0°, 30°, 45° |
| Roof orientation | Dropdown | South, South-East, South-West, East, West, North-East, North-West, North |
| Annual consumption | Number input (step=1) | "Set annual consumption in kWh, e.g. 3,000" |
| PV peak power | Number input (step=0.1) | "Set peak power in kWp, e.g. 10" |
| Battery capacity | Number input (step=0.1) | "Set capacity in kWh, e.g. 10" |

- [ ] Each field has an icon to its left
- [ ] A "Save Model" button (save icon) is shown at the bottom of the form

#### Form validation — client side
- [ ] All fields are required; the browser prevents submission if any are empty

#### Form validation — server side (errors shown below each field)
- [ ] `model_name`: error if empty or longer than 100 characters
- [ ] `location`: error if empty or longer than 100 characters; additionally, error "Location could not be validated. Please check if the address is correct." if Nominatim returns no result
- [ ] `roof_incl`: error if not a number between 0 and 90
- [ ] `roof_azimuth`: error if not a number between -180 and 180
- [ ] `electr_cons`: error if not a number between 0 and 100,000
- [ ] `peak_power`: error if not a number between 0 and 100,000
- [ ] `battery_cap`: error if not a number between 0 and 100,000
- [ ] Each field's error message appears directly below that field in red text
- [ ] The "Save Model" button is disabled while the form submission is in flight

#### Successful submission
- [ ] On success the dialog closes automatically
- [ ] The new model card appears in the model list without a full page reload

---

## 4. Simulations (`/workspace/simulations`)

### Layout
- [ ] Page heading "Simulations" is rendered at the top, centred
- [ ] Page is split into a narrow left column (model selector sidebar) and a wide right content area

### Model selector sidebar
- [ ] Sidebar contains a dropdown listing all models by name
- [ ] Below the dropdown, six parameters of the currently selected model are shown: Location, Roof inclination (`{n}°`), Roof orientation (`{n}°`), Consumption (`{n} kWh`), PV peak power (`{n} kWp`), Battery capacity (`{n} kWh`)
- [ ] Each parameter label is an icon
- [ ] If a simulation exists for the selected model: **View Simulation Results** (green eye) and **Go to Finances** (orange dollar) buttons are shown
- [ ] If no simulation exists: **Run Simulation** (blue play) button is shown
- [ ] Run Simulation, View Simulation Results, and Go to Finances buttons behave identically to those on the Models page

#### Empty model list state
- [ ] If no models exist, the sidebar shows the text "Please" followed by a blue "create a model" link to `/workspace/models` followed by "first." — no dropdown or parameter list is shown

### Default page (`/workspace/simulations` with no model selected)
- [ ] Right content area shows a card with the centred text "Run a simulation to view results"

### URL-driven model selection
- [ ] Navigating directly to `/workspace/simulations/{model_id}` causes the sidebar dropdown to automatically select the model matching `model_id`

---

## 5. Simulation Results (`/workspace/simulations/[model_id]`)

### Layout
- [ ] Right content area shows a 3-column, 3-row grid:
  - Row 1, col 1: Consumption donut chart
  - Row 1, col 2: PV Generation donut chart
  - Row 1, col 3: Monthly PV Generation bar chart
  - Rows 2–3, full width: Power Profiles line chart

### No-results state (simulation not yet run)
- [ ] If no simulation results exist for the model, each chart section shows a card with the text "No results found. Run a simulation to get results."

### Consumption donut chart
- [ ] Card title reads "Consumption: {total} kWh" where `total` is the annual consumption
- [ ] Donut chart shows two segments: **PV** (self-consumption from PV) and **Grid** (consumption from the grid)
- [ ] The value in the centre of the donut shows the self-sufficiency rate as a percentage
- [ ] Below the chart, a legend list shows each segment's name, kWh value, and percentage share
- [ ] Each legend row has a coloured square swatch matching the segment colour
- [ ] Hovering a legend row's info icon shows a tooltip describing the segment

### PV Generation donut chart
- [ ] Card title reads "PV Generation: {total} kWh" where `total` is total PV generation
- [ ] Donut chart shows two segments: **Self-cons.** (self-consumption) and **Grid feed-in**
- [ ] The value in the centre of the donut shows the self-consumption rate as a percentage
- [ ] Legend list and tooltip behaviour identical to Consumption chart

### Monthly PV Generation bar chart
- [ ] Card title reads "Monthly PV Generation"
- [ ] Bar chart shows 12 amber bars, one per month, labelled by month name on the X axis
- [ ] Y axis values are formatted as `"{n} kWh"`

### Power Profiles line chart
- [ ] Chart section spans the full width of the content area
- [ ] Two plain `<input type="date">` fields are shown above the charts for selecting a date range; default values are **2023-06-19** (from) and **2023-06-24** (to)
- [ ] Changing either date input updates the chart data for the new range without a full page reload
- [ ] The upper chart is labelled "Power Profiles" and shows four lines: **Load** (rose), **PV** (amber), **Battery** (teal), **Total** (indigo); Y axis is formatted as `"{n} kW"`
- [ ] The lower chart is labelled "Battery State of Charge" and shows a single teal line; Y axis range is fixed 0–100, formatted as `"{n}%"`
- [ ] Both charts share the same X axis (time); only start and end tick labels are shown on the X axis

---

## 6. Finances (`/workspace/finances`)

### Layout
- [ ] Page heading "Finances" is rendered at the top, centred
- [ ] Page is split into a narrow left column (finances configuration sidebar) and a wide right content area

### Default page (`/workspace/finances` with no model selected)
- [ ] Right content area shows a card with the centred text "Set up finances to view results"

### Finances configuration sidebar — empty model list state
- [ ] If no models exist, sidebar shows "Please" + blue "create a model" link to `/workspace/models` + "first."

### Finances configuration form
- [ ] A model dropdown is shown at the top of the sidebar, listing all models by name
- [ ] Below the dropdown, all eleven input fields are always visible:

| Field | Label | Unit | Step |
|---|---|---|---|
| `electr_price` | Electricity price | ct/kWh | 0.1 |
| `feed_in_tariff` | Feed-in tariff | ct/kWh | 0.1 |
| `pv_price` | PV price | €/kWp | 1 |
| `battery_price` | Battery price | €/kWh | 1 |
| `useful_life` | Useful life | years | 1 |
| `module_deg` | Module degradation | % | 0.1 |
| `inflation` | Inflation | % | 0.1 |
| `op_cost` | Operation cost | % | 0.1 |
| `down_payment` | Down payment | % | 0.1 |
| `pay_off_rate` | Pay off rate | % | 0.1 |
| `interest_rate` | Interest rate | % | 0.1 |

- [ ] Each field has an icon to its left
- [ ] When a model is selected that has previously submitted financial data, the form fields are pre-populated with the saved values
- [ ] When a model with no saved financial data is selected, the form pre-populates with these defaults: electricity price 45, feed-in tariff 8, PV price 1500, battery price 650, useful life 20, module degradation 0.5, inflation 3, operation cost 1, down payment 25, pay-off rate 10, interest rate 5
- [ ] Changing the model dropdown updates the form fields to reflect that model's saved data (or defaults)

#### No-simulation warning
- [ ] If the selected model has no simulation run yet, a warning message is shown: "Please run a simulation before calculating finances." with a bold link to `/workspace/simulations/{model_id}`
- [ ] The **Calculate Finances** submit button is disabled when no simulation exists for the selected model

#### Submit button behaviour
- [ ] The **Calculate Finances** button shows a play icon and the label "Calculate Finances"
- [ ] Clicking the button (when enabled) immediately shows a full-screen loading overlay with the message "Calculating your system's finances ..." and a blue spinning circle
- [ ] The overlay remains until the backend responds
- [ ] On success, the app navigates to `/workspace/finances/{model_id}` and the finance results are displayed

#### Form validation — server side
- [ ] `electr_price`: error if not a number between 0 and 1000
- [ ] `feed_in_tariff`: error if not a number between 0 and 1000
- [ ] `pv_price`: error if not a number between 0 and 10,000
- [ ] `battery_price`: error if not a number between 0 and 10,000
- [ ] `useful_life`: error if not a number between 0 and 50
- [ ] `module_deg`: error if not a number between 0 and 100 (exclusive)
- [ ] `inflation`: error if not a number between 0 and 100
- [ ] `op_cost`: error if not a number between 0 and 100
- [ ] `down_payment`: error if not a number between 0 and 100
- [ ] `pay_off_rate`: error if not a number between 0 and 100
- [ ] `interest_rate`: error if not a number between 0 and 100
- [ ] Field error messages appear in red directly below the relevant field

#### View simulation link
- [ ] If a simulation exists for the selected model, a green **View Simulation Results** button is shown below the form; clicking navigates to `/workspace/simulations/{model_id}`

### URL-driven model selection
- [ ] Navigating directly to `/workspace/finances/{model_id}` causes the sidebar dropdown to auto-select the matching model and populate the form with that model's saved financial data (or defaults)

---

## 7. Finance Results (`/workspace/finances/[model_id]`)

### Layout
- [ ] Right content area shows a 3-column, 2-row grid:
  - Row 1, col 1: Model Summary card
  - Row 1, col 2: Key Performance Indicators card
  - Row 1, col 3: Performance over Lifetime bar chart
  - Row 2, full width: Financial Performance line chart

### No-results state (finances not yet calculated)
- [ ] If no finance results exist, each chart/KPI section shows a card with the text "No results found. Calculate finances to get results."

### Model Summary card
- [ ] Card title reads "Model Summary"
- [ ] Two-column list showing: Location, Roof inclination (`{n}°`), Roof orientation (named direction — see mapping below), Consumption (`{n} kWh`), PV peak power (`{n} kWp`), Battery capacity (`{n} kWh`)
- [ ] Roof orientation is displayed as a direction name, not a number:
  - 0° → South, 45° → South-West, 90° → West, 135° → North-West, 180° → North
  - -45° → South-East, -90° → East, -135° → North-East
  - Any other value → "Unknown Orientation"

### Key Performance Indicators card
- [ ] Card title reads "Key Performance Indicators"
- [ ] Seven rows, each with a label (icon) and a formatted value:

| Label | Format |
|---|---|
| Total investment | `€ {n}` |
| Cum. profit | `€ {n}` |
| Break-even | `{n.1} years` |
| Total loan | `€ {n}` |
| Loan paid off | `{n.1} years` |
| LCOE | `{n.1} ct/kWh` |
| ROI | `{n.1} %` |

### Performance over Lifetime bar chart
- [ ] Card title reads "Performance over Lifetime"
- [ ] Two grouped bars: **Investment** and **Revenue**
- [ ] Investment bar is stacked: PV cost (darker red) + Battery cost (lighter red)
- [ ] Revenue bar is stacked: Operation costs (green, displayed as a negative value), Feed-in revenue (medium green), Cost savings (light green)
- [ ] Y axis values are formatted as `"€ {n}"`

### Financial Performance line chart
- [ ] Card title area reads "Financial Performance"
- [ ] Line chart shows four lines over calendar years: **Cum. Profit** (dark green), **Investment** (red, flat horizontal line), **Cum. Cash Flow** (blue), **Loan** (orange)
- [ ] X axis shows individual year labels (not just start/end)
- [ ] Y axis is formatted as `"€ {n}"`

---

## 8. Loading Overlay

- [ ] A full-screen semi-transparent black overlay with a centred white card appears during:
  - Running a simulation (triggered from Run Simulation button, anywhere it appears)
  - Submitting the finances form (triggered from Calculate Finances button)
- [ ] The white card contains a message string (specific to the action — see above) and a blue spinning circle (64×64 px)
- [ ] The overlay sits above all other page content (highest z-index)
- [ ] The overlay disappears automatically when the action completes

---

## 9. Backend API Calls

All requests use `user_id=mvp-user` as the query parameter.

| # | Method | Endpoint | Triggered by | Expected response |
|---|---|---|---|---|
| 1 | GET | `/workspace/models/fetch-models?user_id=mvp-user` | Models page load, Simulations sidebar load, Finances sidebar load, Finance results model summary | Array of `ModelData` objects |
| 2 | POST | `/workspace/models/submit-model?user_id=mvp-user` | Model form submission | New `model_id` string |
| 3 | DELETE | `/workspace/models/delete-model?user_id=mvp-user&model_id={id}` | Delete model button | Boolean `true` (acknowledged) |
| 4 | GET | `/workspace/simulations/run-sim?user_id=mvp-user&model_id={id}` | Run Simulation button | `{ run_successful: boolean }` |
| 5 | GET | `/workspace/simulations/fetch-sim-results?user_id=mvp-user&model_id={id}` | Simulation results page (donut charts, bar chart) | `SimResultsEval` object |
| 6 | POST | `/workspace/simulations/fetch-sim-timeseries?user_id=mvp-user&model_id={id}` | Power chart (on page load and date range change) | Array of `SimTimestep` objects |
| 7 | GET | `/workspace/finances/fetch-fin-form-data?user_id=mvp-user` | Finances sidebar load | Array of `FinData` objects |
| 8 | POST | `/workspace/finances/submit-fin-form-data?user_id=mvp-user` | Calculate Finances button | `model_id` string |
| 9 | GET | `/workspace/finances/fetch-fin-results?user_id=mvp-user&model_id={id}` | Finance results page (KPIs, charts) | `FinResults` object |
| 10 | GET | `https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1` | Model form submission (geocoding) | Array; first item has `lat`, `lon`, `display_name` |

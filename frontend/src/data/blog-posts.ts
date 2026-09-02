// Static blog post data. Add new posts to the top of the array.

export interface BlogPost {
  slug: string;
  title: string;
  date: string; // ISO date string, e.g. "2025-03-15"
  preview: string; // plain-text excerpt shown on the listing card
  content: string; // full post as an HTML string
}

export const BLOG_POSTS: BlogPost[] = [
  {
    slug: 'understanding-pv-self-consumption',
    title: 'Understanding PV Self-Consumption',
    date: '2025-04-01',
    preview:
      'Self-consumption is the share of solar energy your household uses directly, without exporting it to the grid. Learn why it matters and how battery storage can push it above 80%.',
    content: `
      <p>When your solar panels generate electricity, two things can happen: you use it immediately in your home, or you export it to the grid. The fraction you consume yourself is called <strong>self-consumption</strong>. In most markets, the feed-in tariff for exported electricity is well below the retail price you pay for imports, so maximising self-consumption directly reduces your electricity bill.</p>

      <h2>Why self-consumption varies</h2>
      <p>A household with a 5 kWp system in central Europe will typically see self-consumption rates of 25–35% without a battery. The mismatch is simple: solar peaks around midday, but household demand peaks in the morning and evening. The sun doesn't care about your schedule.</p>

      <h2>The battery effect</h2>
      <p>Adding even a modest battery — say 5 kWh — shifts excess midday generation into the evening demand peak. Ferntree's simulations consistently show self-consumption rising to 60–75% with a correctly sized battery, and approaching 85% for well-matched systems.</p>

      <h2>Diminishing returns</h2>
      <p>Beyond a certain battery size, each additional kilowatt-hour of capacity yields smaller self-consumption gains. Ferntree's financial analysis module helps you find the economic sweet spot: the battery size where the lifetime electricity savings justify the upfront cost.</p>

      <p>Run your own numbers in the <a href="/workspace" data-link>Ferntree simulation app</a>.</p>
    `,
  },
  {
    slug: 'how-ferntree-models-a-full-year',
    title: 'How Ferntree Models a Full Year of Solar',
    date: '2025-03-15',
    preview:
      'Ferntree runs an hourly simulation over 8,760 time steps to produce accurate energy balance results. Here is a look at the data sources and assumptions behind the numbers.',
    content: `
      <p>Accurate PV simulation requires two things: realistic solar irradiance data and a faithful model of how panels, inverters, and batteries interact hour by hour. Ferntree tackles both.</p>

      <h2>Irradiance data from PVGIS</h2>
      <p>Ferntree queries the EU's <a href="https://re.jrc.ec.europa.eu/pvg_tools/" target="_blank" rel="noopener">PVGIS</a> database for your location. PVGIS provides hourly global horizontal irradiance derived from satellite observations, covering Europe, Africa, and large parts of Asia. You supply an address; Ferntree geocodes it via Nominatim and fetches the closest long-term average hourly profile.</p>

      <h2>The 8,760-step simulation</h2>
      <p>For each hour of a representative year, Ferntree computes:</p>
      <ol>
        <li>PV output from panel efficiency, tilt, azimuth, and irradiance.</li>
        <li>Net load = household consumption minus PV output.</li>
        <li>Battery charge/discharge decision based on net load and state of charge.</li>
        <li>Grid import or export for the remaining balance.</li>
      </ol>
      <p>The result is an 8,760-row time series you can explore in the Simulations page, with configurable date ranges.</p>

      <h2>What it does not model</h2>
      <p>Ferntree uses a simplified single-diode model and does not account for module degradation, soiling, or shading from nearby objects. For a first-pass feasibility study, these simplifications are acceptable; for detailed engineering, a dedicated tool like PVsyst is appropriate.</p>
    `,
  },
  {
    slug: 'levelised-cost-of-solar-explained',
    title: 'Levelised Cost of Solar Explained',
    date: '2025-02-20',
    preview:
      'The levelised cost of energy (LCOE) lets you compare solar against grid electricity on a fair, lifetime basis. Here is how to interpret the number Ferntree calculates for your system.',
    content: `
      <p>Solar panels are an upfront investment that pays back over 20–30 years. To compare this investment fairly against simply buying electricity from the grid, we use the <strong>levelised cost of energy (LCOE)</strong>: the total lifetime cost of the system divided by the total energy it produces, expressed in €/kWh.</p>

      <h2>The formula</h2>
      <p>In its simplest form:</p>
      <pre><code>LCOE = (Capex + NPV of Opex) / Lifetime energy production</code></pre>
      <p>Ferntree's financial module asks you for system cost, annual maintenance, a discount rate, and your current electricity tariff. It then computes the LCOE and compares it to your tariff to estimate net savings.</p>

      <h2>Interpreting the result</h2>
      <p>If your LCOE is lower than the grid tariff, the system pays for itself over its lifetime. The gap between the two is your margin of safety — a wider gap means the investment is more robust to rising installation costs or falling tariffs.</p>

      <h2>The role of self-consumption</h2>
      <p>LCOE is only part of the picture. A system with high self-consumption displaces expensive grid imports; one with low self-consumption exports at a low feed-in rate. Ferntree combines both metrics — LCOE and self-consumption — to give you a complete financial picture.</p>

      <p>Try the financial analysis for your own model in the <a href="/workspace/finances" data-link>Finances section</a>.</p>
    `,
  },
];

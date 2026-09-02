-- PostgreSQL schema for the Ferntree backend (migrated from MongoDB).
-- Idempotent: safe to run multiple times.

-- =========================================================================
-- users  (auth descoped; single seeded dummy user)
-- =========================================================================
CREATE TABLE IF NOT EXISTS users (
    id             BIGSERIAL PRIMARY KEY,
    username       TEXT NOT NULL UNIQUE,
    name           TEXT,
    email          TEXT,
    image          TEXT,
    email_verified TIMESTAMPTZ
);

-- =========================================================================
-- models
-- =========================================================================
CREATE TABLE IF NOT EXISTS models (
    id                  BIGSERIAL PRIMARY KEY,
    user_id             BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    model_name          TEXT NOT NULL,
    location            TEXT NOT NULL,
    roof_incl           INTEGER NOT NULL,
    roof_azimuth        INTEGER NOT NULL,
    electr_cons         DOUBLE PRECISION NOT NULL,
    peak_power          DOUBLE PRECISION NOT NULL,
    battery_cap         DOUBLE PRECISION NOT NULL,
    time_created        TIMESTAMPTZ,
    sim_id              BIGINT,
    coord_lat           TEXT,
    coord_lon           TEXT,
    coord_display_name  TEXT
);
CREATE INDEX IF NOT EXISTS idx_models_user_id ON models(user_id);

-- =========================================================================
-- simulations  (1:1 with models; SystemSettings flattened)
-- =========================================================================
CREATE TABLE IF NOT EXISTS simulations (
    id                          BIGSERIAL PRIMARY KEY,
    model_id                    BIGINT NOT NULL UNIQUE REFERENCES models(id) ON DELETE CASCADE,
    run_time                    TIMESTAMPTZ,
    timezone                    TEXT,
    timebase                    INTEGER,
    planning_horizon            INTEGER,
    t_amb                       DOUBLE PRECISION[],
    g_i                         DOUBLE PRECISION[],
    coord_lat                   TEXT,
    coord_lon                   TEXT,
    coord_display_name          TEXT,
    baseload_annual_consumption DOUBLE PRECISION,
    baseload_profile_id         INTEGER,
    pv_roof_tilt                INTEGER,
    pv_roof_azimuth             INTEGER,
    pv_peak_power               DOUBLE PRECISION,
    battery_capacity            DOUBLE PRECISION,
    battery_max_power           DOUBLE PRECISION,
    battery_soc_init            DOUBLE PRECISION,
    batctrl_planning_horizon    INTEGER,
    batctrl_useable_capacity    DOUBLE PRECISION,
    batctrl_greedy              BOOLEAN,
    batctrl_opt_fill            BOOLEAN
);

-- =========================================================================
-- sim_timesteps  (was sim_results_ts.timeseries; 1 row per timestep)
-- =========================================================================
CREATE TABLE IF NOT EXISTS sim_timesteps (
    id           BIGSERIAL PRIMARY KEY,
    sim_id       BIGINT NOT NULL REFERENCES simulations(id) ON DELETE CASCADE,
    time         DOUBLE PRECISION NOT NULL,
    t_amb        DOUBLE PRECISION,
    p_solar      DOUBLE PRECISION,
    p_base       DOUBLE PRECISION,
    p_pv         DOUBLE PRECISION,
    p_bat        DOUBLE PRECISION,
    soc_bat      DOUBLE PRECISION,
    fill_level   DOUBLE PRECISION,
    p_load_pred  DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_sim_timesteps_sim_time ON sim_timesteps(sim_id, time);

-- =========================================================================
-- sim_results_eval  (1:1 with models; EnergyKPIs flattened)
-- =========================================================================
CREATE TABLE IF NOT EXISTS sim_results_eval (
    id                    BIGSERIAL PRIMARY KEY,
    model_id              BIGINT NOT NULL UNIQUE REFERENCES models(id) ON DELETE CASCADE,
    annual_consumption    DOUBLE PRECISION,
    pv_generation         DOUBLE PRECISION,
    grid_consumption      DOUBLE PRECISION,
    grid_feed_in          DOUBLE PRECISION,
    self_consumption      DOUBLE PRECISION,
    self_consumption_rate DOUBLE PRECISION,
    self_sufficiency      DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS pv_monthly_gen (
    id            BIGSERIAL PRIMARY KEY,
    eval_id       BIGINT NOT NULL REFERENCES sim_results_eval(id) ON DELETE CASCADE,
    month         TEXT NOT NULL,
    pv_generation DOUBLE PRECISION NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_pv_monthly_gen_eval ON pv_monthly_gen(eval_id);

-- =========================================================================
-- finances  (1:1 with models; FinFormData)
-- =========================================================================
CREATE TABLE IF NOT EXISTS finances (
    id             BIGSERIAL PRIMARY KEY,
    model_id       BIGINT NOT NULL UNIQUE REFERENCES models(id) ON DELETE CASCADE,
    electr_price   DOUBLE PRECISION,
    feed_in_tariff DOUBLE PRECISION,
    pv_price       DOUBLE PRECISION,
    battery_price  DOUBLE PRECISION,
    useful_life    INTEGER,
    module_deg     DOUBLE PRECISION,
    inflation      DOUBLE PRECISION,
    op_cost        DOUBLE PRECISION,
    down_payment   DOUBLE PRECISION,
    pay_off_rate   DOUBLE PRECISION,
    interest_rate  DOUBLE PRECISION
);

-- =========================================================================
-- fin_results  (1:1 with models; FinKPIs + FinInvestment flattened)
-- =========================================================================
CREATE TABLE IF NOT EXISTS fin_results (
    id                   BIGSERIAL PRIMARY KEY,
    model_id             BIGINT NOT NULL UNIQUE REFERENCES models(id) ON DELETE CASCADE,
    investment_pv        DOUBLE PRECISION,
    investment_battery   DOUBLE PRECISION,
    investment_total     DOUBLE PRECISION,
    break_even_year      DOUBLE PRECISION,
    cum_profit           DOUBLE PRECISION,
    cum_cost_savings     DOUBLE PRECISION,
    cum_feed_in_revenue  DOUBLE PRECISION,
    cum_operation_costs  DOUBLE PRECISION,
    lcoe                 DOUBLE PRECISION,
    solar_interest_rate  DOUBLE PRECISION,
    loan                 DOUBLE PRECISION,
    loan_paid_off        DOUBLE PRECISION
);

CREATE TABLE IF NOT EXISTS fin_yearly_data (
    id             BIGSERIAL PRIMARY KEY,
    fin_results_id BIGINT NOT NULL REFERENCES fin_results(id) ON DELETE CASCADE,
    year           INTEGER NOT NULL,
    cum_profit     DOUBLE PRECISION,
    cum_cash_flow  DOUBLE PRECISION,
    loan           DOUBLE PRECISION
);
CREATE INDEX IF NOT EXISTS idx_fin_yearly_data_parent ON fin_yearly_data(fin_results_id);

-- =========================================================================
-- loadprofiles  (reference data; load_profile array read whole)
-- =========================================================================
CREATE TABLE IF NOT EXISTS loadprofiles (
    id           BIGSERIAL PRIMARY KEY,
    profile_id   INTEGER NOT NULL UNIQUE,
    type         TEXT,
    load_profile DOUBLE PRECISION[] NOT NULL
);

-- =========================================================================
-- Seed the dummy user (auth descoped)
-- =========================================================================
INSERT INTO users (username, name, email, image, email_verified)
VALUES ('mvp-user', 'MVP User', 'mvp@example.com', '', NULL)
ON CONFLICT (username) DO NOTHING;

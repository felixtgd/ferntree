// Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

'use server';

import { redirect } from 'next/navigation'
import { z } from "zod";

const loadBackendBaseUri = () => {
    // Load backend base URI
    const BACKEND_BASE_URI = process.env.BACKEND_BASE_URI;
    if (!BACKEND_BASE_URI) {
        console.error('BACKEND_BASE_URI is not defined');
        throw new Error('Backend base URI is not defined.');
    }
    return BACKEND_BASE_URI;
}

const formSchema = z.object({
    location: z.string()
        .max(100, { message: 'Location must be at most 100 characters long' })
        .min(1, { message: 'Please specify a location' }),
    roof_incl: z.coerce
        .number()
        .gte(0, { message: 'Must be at least 0°' })
        .lte(90, { message: 'Must be at most 90°' }),
    roof_azimuth: z.coerce
        .number()
        .gte(-180, { message: 'Must be at least -180°' })
        .lte(180, { message: 'Must be at most 180°' }),
    electr_cons: z.coerce
        .number()
        .gte(0, { message: 'Must be at least 0 kWh' })
        .lte(100000, { message: 'Must be at most 100,000 kWh' }),
    peak_power: z.coerce
        .number()
        .gte(0, { message: 'Must be at least 0 kWp' })
        .lte(100000, { message: 'Must be at most 100,000 kWp' }),
    battery_cap: z.coerce
        .number()
        .gte(0, { message: 'Must be at least 0 kWh' })
        .lte(100000, { message: 'Must be at most 100,000 kWh' }),
    electr_price: z.coerce
        .number()
        .gte(0, { message: 'Must be at least 0 cents/kWh' })
        .lte(100, { message: 'Must be at most 1,000 cents/kWh' }),
    down_payment: z.coerce
        .number()
        .gte(0, { message: 'Must be at least 0%' })
        .lte(100, { message: 'Must be at most 100%' }),
    pay_off_rate: z.coerce
        .number()
        .gte(0, { message: 'Must be at least 0%' })
        .lte(100, { message: 'Must be at most 100%' }),
    interest_rate: z.coerce
        .number()
        .gte(0, { message: 'Must be at least 0%' })
        .lte(100, { message: 'Must be at most 100%' }),
});

export type State = {
    errors?: Record<string, string[]>;
    message?: string | null;
};

export async function submitForm(prevState: State, formData: FormData) {
    // When invoked in a form, the action automatically receives the FormData object.
    // You don't need to use React useState to manage fields, instead, you can extract
    // the data using the native FormData methods.

    // Validate that formData has schema of SimulationModel
    const validatedFields = formSchema.safeParse({
        location:       formData.get('location'),
        roof_incl:      formData.get('roof_incl'),
        roof_azimuth:   formData.get('roof_azimuth'),
        electr_cons:    formData.get('electr_cons'),
        peak_power:     formData.get('peak_power'),
        battery_cap:    formData.get('battery_cap'),
        electr_price:   formData.get('electr_price'),
        down_payment:   formData.get('down_payment'),
        pay_off_rate:   formData.get('pay_off_rate'),
        interest_rate:  formData.get('interest_rate'),
    });

    if (!validatedFields.success) {
        console.error(`Invalid form data: ${validatedFields.error}`);
        return {
            errors: validatedFields.error.flatten().fieldErrors,
            message: 'Missing Fields. Failed to submit form.',
          };
    }

    let model_id;
    let sim_run_success;

    try {
        // Submit user input form with model parameters
        const BACKEND_BASE_URI = loadBackendBaseUri();
        const response_submit_form = await fetch(`${BACKEND_BASE_URI}/dashboard/submit-model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(validatedFields.data),
        });
        model_id = await response_submit_form.json();

        console.log(`POST dashboard/submit-model: PV form submitted (${response_submit_form.status}). Model ID: ${model_id}`);

        // TEMPORARY: there must be a better place fir this fetch
        // Start simulation of model
        const response_sim_run = await fetch(`${BACKEND_BASE_URI}/dashboard/run-simulation?model_id=${model_id}`).then((res) => res.json());
        sim_run_success = response_sim_run.sim_run_success;
        if (sim_run_success) {
            console.log(`GET dashboard/run-simulation: Simulation run successful for model ID: ${model_id}`);
        } else {
            console.error(`GET dashboard/run-simulation: Simulation run failed for model ID: ${model_id}`);
        }

    } catch (error) {
        console.error(`Failed to submit form: ${error}`);
    }

    if (sim_run_success) {
        redirect(`/dashboard/${model_id}`)
    } else {
        redirect('/dashboard')
    }
};

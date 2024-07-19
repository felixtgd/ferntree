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
    location: z.string(),
    electr_cons: z.number(),
    roof_incl: z.number(),
    roof_azimuth: z.number(),
    peak_power: z.number(),
    battery_cap: z.number(),
    electr_price: z.number(),
    down_payment: z.number(),
    pay_off_rate: z.number(),
    interest_rate: z.number(),
  });

export async function submitForm(formData: FormData) {
    // When invoked in a form, the action automatically receives the FormData object.
    // You don't need to use React useState to manage fields, instead, you can extract
    // the data using the native FormData methods.

    // Validate that formData has schema of SimulationModel
    const validatedFields = formSchema.safeParse({
        location: formData.get('location'),
        electr_cons: Number(formData.get('electr_cons')),
        roof_incl: Number(formData.get('roof_incl')),
        roof_azimuth: Number(formData.get('roof_azimuth')),
        peak_power: Number(formData.get('peak_power')),
        battery_cap: Number(formData.get('battery_cap')),
        electr_price: Number(formData.get('electr_price')),
        down_payment: Number(formData.get('down_payment')),
        pay_off_rate: Number(formData.get('pay_off_rate')),
        interest_rate: Number(formData.get('interest_rate')),
    });

    if (!validatedFields.success) {
        console.error(`Invalid form data: ${validatedFields.error}`);
        return;
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

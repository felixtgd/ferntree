// Server Actions: https://nextjs.org/docs/app/building-your-application/data-fetching/server-actions-and-mutations

'use server';

// import { revalidatePath } from "next/cache";
import { redirect } from 'next/navigation'
import { z } from "zod";

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

    // Log the form data and print types of each field
    // formData.forEach((value, key) => {
    //     console.log(`${key}: ${value} (${typeof value})`);
    // });

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

    try {
        const response = await fetch('http://localhost:8000/dashboard/submit-model', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(validatedFields),
        });
        model_id = await response.json();

        console.log(`PV form submitted. Model ID: ${model_id}`);
        console.log(`Response status: ${response.status}`);

    } catch (error) {
        console.error(`Failed to submit form: ${error}`);
    }

    // revalidatePath('/dashboard');
    // redirect user to dashboard/{model_id}
    redirect(`/dashboard/${model_id}`)

};

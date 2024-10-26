'use server'

import { auth } from "@/auth"
import { Session, User } from "next-auth"
import { EmailDataSchema, FormState, ModelData } from "@/app/utils/definitions"
import { cache } from "react";
import nodemailer from 'nodemailer';


export async function loadBackendBaseUri() {
    // Load backend base URI
    const BACKEND_BASE_URI = process.env.BACKEND_BASE_URI;
    if (!BACKEND_BASE_URI) {
        throw new Error('Backend base URI is not defined.');
    }
    return BACKEND_BASE_URI;
}

export async function getUser() {
    // Get the user of the current session
    const session: Session | null = await auth()
    if (!session || !session.user) {
        throw new Error('No active session');
    }
    return session.user
}

export async function getUserID() {
    // Get the user ID
    const user: User | null = await getUser()
    if (!user || !user?.id) {
        throw new Error('User is not defined');
    }
    return user.id
}

export const fetchModels = cache(async (): Promise<ModelData[]> => {

    // Get the user ID
    const user_id = await getUserID();

    // Fetch models of user
    const BACKEND_BASE_URI = await loadBackendBaseUri();
    const response_load_models = await fetch(`${BACKEND_BASE_URI}/workspace/models/fetch-models?user_id=${user_id}`);
    const models: ModelData[] = await response_load_models.json();

    console.log(`GET workspace/models/fetch-models: Models loaded (${response_load_models.status}).`);

    return models;
})


export async function sendEmail(prev_state: FormState, form_data: FormData) {

    // Validate that formData has schema of ModelDataSchema
    const validated_fields = EmailDataSchema.safeParse(Object.fromEntries(form_data));

    let state: FormState = prev_state;
    if (!validated_fields.success) {
        console.error(`Invalid form data: ${validated_fields.error}`);
        state = {
            errors: validated_fields.error.flatten().fieldErrors,
            message: 'Invalid Fields. Failed to submit form.',
          };
        return state;
    }

    const sanitized_message = `From: ${validated_fields.data.name} (${validated_fields.data.email})\n${validated_fields.data.message}`;

    const transporter = nodemailer.createTransport({
        host: process.env.EMAIL_HOST,
        port: process.env.EMAIL_PORT,
        secure: false,
        auth: {
            user: process.env.EMAIL_SENDER,
            pass: process.env.EMAIL_PASS
        }
    } as nodemailer.TransportOptions);

    try {
        const info = await transporter.sendMail({
            from: process.env.EMAIL_SENDER,
            to: process.env.EMAIL_RECEIVER,
            subject: validated_fields.data.category,
            text: sanitized_message,
        })
        console.log("Message sent: %s", info.messageId);
        state = {
            errors: {},
            message: 'success',
        };
    } catch (error) {
        console.error("Error sending email: %s", error);
        state = {
            errors: {},
            message: 'Failed to submit form.',
        };
    }

    return state;
}

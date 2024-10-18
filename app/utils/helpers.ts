'use server'

import { auth } from "@/auth"
import { Session, User } from "next-auth"
import { ModelData } from "@/app/utils/definitions"
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


export async function sendEmail(formData: FormData) {

    const user_name: string = formData.get("name") as string;
    const user_email: string = formData.get("email") as string;
    const category: string = formData.get("category") as string;
    const message: string = formData.get("message") as string;

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
            subject: category,
            html: `<p>From: ${user_name} (${user_email})</p><p>${message}</p>`
        })
        console.log("Message sent: %s", info.messageId);
    } catch (error) {
        console.error("Error sending email: %s", error);
    }
}

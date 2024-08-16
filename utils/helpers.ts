'use server'

import { auth } from "@/auth"
import { Session, User } from "next-auth"


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

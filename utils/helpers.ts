'use server'

import { auth } from "@/auth"
import { Session } from "next-auth"


export async function getUser() {
    const session: Session | null = await auth()

    if (!session?.user) return null

    console.log(session.user)

    return session.user
}

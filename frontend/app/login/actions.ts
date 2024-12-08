'use server'

import { signIn } from "@/auth"

export default async function signInAction(form_data: FormData) {

    const provider: string = form_data.get('provider') as string
    await signIn(provider, form_data)

}

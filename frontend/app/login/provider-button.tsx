'use client'

import {
    RemixiconComponentType,
    RiErrorWarningFill,
    RiGithubFill,
    RiGoogleFill,
    RiMailLine,

 } from "@remixicon/react"
import { Button } from "@tremor/react"

export function ProviderButton({provider}: {provider: string}) {

    let icon: RemixiconComponentType

    if (provider === 'github') {
        icon = RiGithubFill
    }
    else if (provider === 'google') {
        icon = RiGoogleFill
    }
    else {
        icon = RiErrorWarningFill
    }

    return (
        <div className="p-2 mx-2">
            <Button type="submit" icon={icon} size="xl" className="min-w-32 max-w-64 w-full mx-auto">
                {provider.charAt(0).toUpperCase() + provider.slice(1)}
            </Button>
        </div>
    )
}

export function EmailSignInButton() {

    return (
        <div className="p-2">
            <Button type="submit" icon={RiMailLine} size="xl" className="min-w-32 max-w-64 w-full mx-auto">
                Sign in with email
            </Button>
        </div>
    )
}

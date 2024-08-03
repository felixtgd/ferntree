'use client'

import {
    RemixiconComponentType,
    RiAppleFill,
    RiErrorWarningFill,
    RiFacebookCircleFill,
    RiGithubFill,
    RiGoogleFill,

 } from "@remixicon/react"
import { Button } from "@tremor/react"

export default function ProviderButton({provider}: {provider: string}) {

    let icon: RemixiconComponentType

    if (provider === 'github') {
        icon = RiGithubFill
    }
    else if (provider === 'google') {
        icon = RiGoogleFill
    }
    else if (provider === 'facebook') {
        icon = RiFacebookCircleFill
    }
    else if (provider === 'apple') {
        icon = RiAppleFill
    }
    else {
        icon = RiErrorWarningFill
    }

    return (
        <div className="p-2">
            <Button type="submit" icon={icon}/>
        </div>
    )
}

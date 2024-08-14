'use client'

import { RemixiconComponentType, RiDeleteBin6Line, RiEyeLine, RiPencilLine, RiPlayCircleLine } from "@remixicon/react";
import { Button, ButtonProps } from "@tremor/react";


function BaseButton(
    {
        icon,
        color,
        tooltip,
    }:
    {
        tooltip: string,
        color: ButtonProps["color"],
        icon: RemixiconComponentType,
    }
) {
    return (
        <div className="flex justify-center p-2">
            <Button
                icon={icon}
                size="sm"
                color={color}
                variant="secondary"
                disabled={false}
                loading={false}
                loadingText="Loading"
                tooltip={tooltip}
                className="w-10 h-10"
            />
        </div>
    );
}

export function DeleteButton({type}: {type: string}) {

    const tooltip=`Delete ${type}`

    return (
        <BaseButton
            icon={RiDeleteBin6Line}
            color="red"
            tooltip={tooltip}
        />
    );
}

export function EditButton({type}: {type: string}) {

    const tooltip=`Edit ${type}`

    return (
        <BaseButton
            icon={RiPencilLine}
            color="orange"
            tooltip={tooltip}
        />
    );
}

export function RunButton({type}: {type: string}) {

    let tooltip;
    if (type === "model") {
        tooltip = "Run simulation";
    } else if (type === "scenario") {
        tooltip = "Run scenario";
    }
    else {
        tooltip = "Type unknown";
    }

    return (
        <BaseButton
            icon={RiPlayCircleLine}
            color="blue"
            tooltip={tooltip}
        />
    );
}

export function ViewButton({type}: {type: string}) {

    let tooltip;
    if (type === "model") {
        tooltip = "View simulation results";
    } else if (type === "scenario") {
        tooltip = "View scenario results";
    }
    else {
        tooltip = "Type unknown";
    }

    return (
        <BaseButton
            icon={RiEyeLine}
            color="green"
            tooltip={tooltip}
        />
    );
}

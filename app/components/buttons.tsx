'use client'

import { RemixiconComponentType, RiDeleteBin6Line, RiEyeLine, RiPencilLine, RiPlayCircleLine } from "@remixicon/react";
import { Button, ButtonProps } from "@tremor/react";
import { deleteModel, editModel, runSimulation, viewResults } from "../workspace/models/actions";


function BaseButton(
    {
        icon,
        color,
        tooltip,
        model_id,
        buttonAction,
    }:
    {
        tooltip: string,
        color: ButtonProps["color"],
        icon: RemixiconComponentType,
        model_id: string,
        buttonAction: (model_id: string) => Promise<void>,
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
                onClick={() => buttonAction(model_id)}
            />
        </div>
    );
}

export function DeleteButton({type, model_id}: {type: string, model_id: string}) {

    const tooltip=`Delete ${type}`

    return (
        <BaseButton
            icon={RiDeleteBin6Line}
            color="red"
            tooltip={tooltip}
            model_id={model_id}
            buttonAction={deleteModel}
        />
    );
}

export function RunButton({type, model_id}: {type: string, model_id: string}) {

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
            model_id={model_id}
            buttonAction={runSimulation}
        />
    );
}

export function ViewButton({type, model_id}: {type: string, model_id: string}) {

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
            model_id={model_id}
            buttonAction={viewResults}
        />
    );
}

// not used right now, maybe in the future
export function EditButton({type, model_id}: {type: string, model_id: string}) {

    const tooltip=`Edit ${type}`

    return (
        <BaseButton
            icon={RiPencilLine}
            color="orange"
            tooltip={tooltip}
            model_id={model_id}
            buttonAction={editModel}
        />
    );
}

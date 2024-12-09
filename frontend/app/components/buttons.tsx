'use client'

import { RemixiconComponentType, RiDeleteBin6Line, RiExchangeDollarLine, RiEyeLine, RiPencilLine, RiPlayCircleLine } from "@remixicon/react";
import { Button, ButtonProps } from "@tremor/react";
import { deleteModel, editModel, goToFin, runSimulation, viewResults } from "@/app/components/button-actions";
import { useState } from "react";
import { useRouter } from "next/navigation";
import LoadingScreen from "./loading-screen";


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

export function DeleteModelButton({ model_id}: {model_id: string}) {

    const tooltip = "Delete model"

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

export function RunSimButton({model_id}: {model_id: string}) {

    const [isLoading, setIsLoading] = useState(false);
    const router = useRouter();

    async function handleRunSimulation(model_id: string) {
        setIsLoading(true);
        const result = await runSimulation(model_id);
        setIsLoading(false);

        if (result.success) {
          router.push(`/workspace/simulations/${result.model_id}`);
        } else {
          router.refresh();
        }
      };

    const tooltip = "Run simulation";

    return (
        <>
            <BaseButton
                icon={RiPlayCircleLine}
                color="blue"
                tooltip={tooltip}
                model_id={model_id}
                buttonAction={handleRunSimulation}
            />
            {isLoading && <LoadingScreen message={"Simulating your energy system ..."} />}
        </>
    );
}

export function ViewSimButton({model_id}: {model_id: string}) {

    const tooltip = "View simulation results"

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


export function GoToFinButton({model_id}: {model_id: string}) {

    const tooltip = "Go to finances"

    return (
        <BaseButton
            icon={RiExchangeDollarLine}
            color="orange"
            tooltip={tooltip}
            model_id={model_id}
            buttonAction={goToFin}
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

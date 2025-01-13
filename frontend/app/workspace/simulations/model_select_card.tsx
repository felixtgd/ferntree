import { Card, } from "@tremor/react";
import { fetchModels } from "@/app/utils/helpers";
import { ModelData } from "@/app/utils/definitions";
import { ModelSelectForm } from "./model_select_form";

export async function ModelSelection() {

    const models: ModelData[] = await fetchModels();

    return (
        <Card
            className="flex transition-all duration-300 flex-grow flex-col items-center justify-center w-full"
        >
            <ModelSelectForm models={models} />

        </Card>
    );
}

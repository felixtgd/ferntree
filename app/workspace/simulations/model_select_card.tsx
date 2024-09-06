import { Card, } from "@tremor/react";
import { fetchModels } from "@/app/utils/helpers";
import { ModelData } from "@/app/utils/definitions";
import { ModelSelectForm } from "./model_select_form";

export async function ModelSelection() {

    const models: ModelData[] = await fetchModels();

    return (
        <div className="p-2">
            <Card
                className="flex w-[30%] lg:w-[20%] 2xl:w-[15%] transition-all duration-300"
            >
                <ModelSelectForm models={models} />

            </Card>
        </div>
    );
}

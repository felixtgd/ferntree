import { Card, } from "@tremor/react";
import { fetchModels } from "./actions";
import { ModelData } from "@/utils/definitions";
import { ModelSelectForm } from "./model_select_form";

export async function ModelSelection() {

    const models: ModelData[] = await fetchModels();

    return (
        <div className="p-2">
            <Card
                className="flex w-[30%] lg:w-[15%] transition-all duration-300"
            >
                <ModelSelectForm models={models} />

            </Card>
        </div>
    );
}

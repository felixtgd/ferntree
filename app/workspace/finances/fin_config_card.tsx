import { Card, } from "@tremor/react";
import { fetchModels } from "@/app/utils/helpers";
import { ModelData } from "@/app/utils/definitions";
import { FinanceConfigForm } from "./fin_config_form";

export async function FinanceConfig() {

    const models: ModelData[] = await fetchModels();

    return (
        <Card
            className="flex transition-all duration-300 flex-grow flex-col items-center justify-center w-full"
        >
            <FinanceConfigForm models={models} />

        </Card>
    );
}

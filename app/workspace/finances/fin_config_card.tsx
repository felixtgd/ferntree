import { Card, } from "@tremor/react";
import { fetchModels } from "@/app/utils/helpers";
import { FinData, ModelData } from "@/app/utils/definitions";
import { FinanceConfigForm } from "./fin_config_form";
import { fetchFinFormData } from "./actions";

export async function FinanceConfig() {

    const models: ModelData[] = await fetchModels();
    const fin_form_data_all: FinData[] = await fetchFinFormData();

    return (
        <Card
            className="flex transition-all duration-300 flex-grow flex-col items-center justify-center w-full"
        >
            <FinanceConfigForm models={models} fin_form_data_all={fin_form_data_all} />

        </Card>
    );
}

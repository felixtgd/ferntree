import { Card, } from "@tremor/react";
import { fetchModels } from "@/app/utils/helpers";
import { FinData, ModelData } from "@/app/utils/definitions";
import { FinanceConfigForm } from "./fin_config_form";
import { fetchFinFormData } from "./actions";
import Link from "next/link";

export async function FinanceConfig() {

    const models: ModelData[] = await fetchModels();
    const fin_form_data_all: FinData[] = await fetchFinFormData();

    return (
        <Card
            className="flex transition-all duration-300 flex-grow flex-col items-center justify-center w-full"
        >
        {models.length > 0 ? (
            <FinanceConfigForm models={models} fin_form_data_all={fin_form_data_all} />
        ) : (
            <div className="flex flex-col w-full items-center">
                <h2 className="w-full text-center mb-4">
                    Please <Link href="/workspace/models" className="text-blue-500">create a model</Link> first.
                </h2>
            </div>
        )}
        </Card>
    );
}

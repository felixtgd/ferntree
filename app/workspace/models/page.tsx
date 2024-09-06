import { ModelFormDialog } from "./model-form-dialog";
import { ModelCard } from "./model-card";
import { fetchModels } from "@/app/utils/helpers";
import { ModelData } from "@/app/utils/definitions";


export default async function Page() {

    const models: ModelData[] = await fetchModels();
    const num_models = models.length;

    return (
        <main>
            <div className="flex justify-between items-center p-4">
                <h3 className="mx-auto text-2xl font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong">
                    Models
                </h3>

                <div className="flex items-center">
                    <ModelFormDialog num_models={num_models} />
                </div>
            </div>

            <div>
                {models.map((modelData, index) => (
                    <ModelCard key={index} modelData={modelData} />
                ))}
            </div>
        </main>
    );
}

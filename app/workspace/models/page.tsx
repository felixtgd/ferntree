import { ModelFormDialog } from "./model-form-dialog";
import { ModelCard } from "./model-card";
import { fetchModels } from "./actions";
import { ModelData } from "@/utils/definitions";


export default async function Page() {

    const models: ModelData[] | null = await fetchModels();

    return (
        <main>
            <div className="flex justify-between items-center p-4">
                <h3 className="mx-auto text-2xl font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong">
                    Models
                </h3>

                <div className="flex items-center">
                    <ModelFormDialog />
                </div>
            </div>

            <div>
                {models?.map((modelData, index) => (
                    <ModelCard key={index} modelData={modelData} />
                ))}
            </div>
        </main>
    );
}

import { ModelFormDialog } from "./model-form-dialog";
import { ModelCard } from "./model-card";
import { fetchModels } from "@/app/utils/helpers";
import { ModelData } from "@/app/utils/definitions";


function EmptyStateMessage() {
    return (
      <div className="flex relative">
        <svg
            className="absolute top-12 right-32 w-128 h-64 text-blue-500"
            fill="none"
            viewBox="0 0 100 50" // "min-x min-y width height"
            stroke="currentColor"
        >
            <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={1}
            d="M0 35 C45 35, 85 25, 95 5 L89 10 M95 5 L93 13"
            />
            <text
                x="1"
                y="45"
                fill="currentColor"
                fontSize="4"
                // fontFamily="Arial, sans-serif"
                fontWeight="300"
                strokeWidth="0.2"
            >
                Start by creating a model
            </text>
        </svg>
      </div>
    );
  }

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

            {models.length === 0 ? (
                <EmptyStateMessage />
            ) : (
                <div>
                {models.map((modelData, index) => (
                    <ModelCard key={index} modelData={modelData} />
                ))}
                </div>
            )}
        </main>
    );
}

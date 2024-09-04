import { ModelSelection } from "./model_select_card";

export default async function Page() {

    return (
        <main>
            <div className="flex justify-between items-center p-4">
                <h3 className="mx-auto text-2xl font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong">
                    Simulations
                </h3>
            </div>
            <div>
                <ModelSelection />
            </div>
        </main>
    );
}

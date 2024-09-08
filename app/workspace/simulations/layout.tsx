import { ModelSelection } from "./model_select_card";

export default async function Layout({ children }: { children: React.ReactNode }) {

    return (
        <main>

            <div className="flex justify-between items-center p-4">
                <h3 className="mx-auto text-2xl font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong">
                    Simulations
                </h3>
            </div>

            <div className="grid gap-4 grid-cols-5">

                <div className="col-span-1">
                    <ModelSelection />
                </div>

                <div className="col-span-4">
                    {children}
                </div>

            </div>

        </main>
    );
}

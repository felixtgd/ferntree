
import { FinanceConfig } from "./finance_config_card";

export default async function Layout({ children }: { children: React.ReactNode }) {

    return (
        <div>

            <div className="flex justify-between items-center p-4">
                <h3 className="mx-auto text-2xl font-semibold text-tremor-content-strong dark:text-dark-tremor-content-strong">
                    Finances
                </h3>
            </div>

            <div className="grid gap-4 grid-cols-5">

                <div className="col-span-1">
                    <FinanceConfig />
                </div>

                <div className="col-span-4">
                    {children}
                </div>

            </div>

        </div>
    );
}

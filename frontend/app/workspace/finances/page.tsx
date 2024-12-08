import { Card } from "@tremor/react";

export default async function Page() {

    return (
        <main>
            <div className="grid gap-4 grid-cols-3">
                <div className="col-span-1">
                    <Card
                        className="flex flex-grow flex-col items-center justify-center w-full h-full max-h-80"
                        // decoration="top"
                        // decorationColor="blue-300"
                    >
                        <span className="text-center text-tremor-content-strong dark:text-dark-tremor-content-strong font-medium">
                            Set up finances to view results
                        </span>
                    </Card>
                </div>
            </div>
        </main>
    );
}

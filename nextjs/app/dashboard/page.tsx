'use client'

import PvForm from '@/app/ui/dashboard/pv-form';
import SimDataContext from '@/app/ui/dashboard/pv-context';
import PvResults from '@/app/ui/dashboard/pv-results';
import { SimEvaluation } from '@/app/lib/definitions';
import { useState } from 'react';

export default function Page() {
    const [data, setData] = useState<SimEvaluation | null>(null);

    return (
        <main>
            <div className="grid gap-6 grid-cols-5">
            <SimDataContext.Provider value={data}>
                <div className="col-span-1">
                    <PvForm setData={setData} />
                </div>
                <div className="col-span-4">
                    <PvResults />
                </div>
            </SimDataContext.Provider>
            </div>
        </main>
    );
}

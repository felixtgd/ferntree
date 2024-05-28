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
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <SimDataContext.Provider value={data}>
                <PvForm setData={setData} />
                <PvResults />
            </SimDataContext.Provider>
            </div>
        </main>
    );
}

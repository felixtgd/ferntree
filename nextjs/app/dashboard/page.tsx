'use client'

import PvForm from '@/app/ui/dashboard/pv-form';
import PvDataContext from '@/app/ui/dashboard/pv-context';
import PvResults from '@/app/ui/dashboard/pv-results';
import { PvData } from '@/app/lib/definitions';
import { useState } from 'react';

export default function Page() {
    const [data, setData] = useState<PvData | null>(null);

    return (
        <main>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <PvDataContext.Provider value={data}>
                <PvForm setData={setData} />
                <PvResults />
            </PvDataContext.Provider>
            </div>
        </main>
    );
}

import { PvForm } from './pv-form';

export default function Page() {
    return (
        <main>
            <div className="grid gap-4 grid-cols-5">
                <div className="col-span-1">
                    <PvForm />
                </div>
            </div>
        </main>
    );
}

import Form from '@/app/ui/dashboard/pv-form';

export default async function Page() {

    return (
        <main>
            <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
                <Form />
            </div>
        </main>
    );
}

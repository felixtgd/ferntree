import Link from "next/link";

export default function Page() {
    return (
        <main>
            <div className="mt-24 w-3/4 items-center justify-between mx-auto">
                <div className="flex flex-col md:flex-row justify-between items-center">
                    <Link href="/workspace/models">
                        <div className="bg-blue-100 rounded-lg shadow-md p-4 text-center w-64 mb-4 md:mb-0 hover:bg-blue-300">
                            <div className="bg-blue-500 text-white w-8 h-8 rounded-full flex items-center justify-center mx-auto mb-2">1</div>
                            <h3 className="font-bold mb-2">Models</h3>
                            <p className="text-sm">Design your energy system. You can create up to 5 models.</p>
                        </div>
                    </Link>
                    <div className="text-blue-500 text-4xl mx-4 hidden md:block">→</div>
                    <Link href="/workspace/simulations">
                        <div className="bg-blue-100 rounded-lg shadow-md p-4 text-center w-64 mb-4 md:mb-0 hover:bg-blue-300">
                            <div className="bg-blue-500 text-white w-8 h-8 rounded-full flex items-center justify-center mx-auto mb-2">2</div>
                            <h3 className="font-bold mb-2">Simulations</h3>
                            <p className="text-sm">Simulate the energy system and examine its operation.</p>
                        </div>
                    </Link>
                    <div className="text-blue-500 text-4xl mx-4 hidden md:block">→</div>
                    <Link href="/workspace/finances">
                        <div className="bg-blue-100 rounded-lg shadow-md p-4 text-center w-64 mb-4 md:mb-0 hover:bg-blue-300">
                            <div className="bg-blue-500 text-white w-8 h-8 rounded-full flex items-center justify-center mx-auto mb-2">3</div>
                            <h3 className="font-bold mb-2">Finances</h3>
                            <p className="text-sm">Analyze the financial performance of your system.</p>
                        </div>
                    </Link>
                </div>
            </div>
        </main>
    );
}

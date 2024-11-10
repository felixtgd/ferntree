import { getUser } from "@/app/utils/helpers";
import { User } from "next-auth";
import Image from "next/image";
import Link from "next/link";

export default async function Page() {
    const user: User | null = await getUser();

    return (
        <main>
            <div className="bg-blue-100 rounded-lg shadow-md p-6 mb-8 mt-8 max-w-2xl mx-auto">
                {user && (
                    <div className="flex items-center space-x-4">
                        <Image
                            src={user.image as string}
                            width={80}
                            height={80}
                            alt={user.name as string}
                            className="rounded-full border-4 border-white shadow-sm"
                        />
                        <div>
                            <h2 className="text-2xl font-bold text-blue-800">Welcome {user.name}!</h2>
                            <p className="text-blue-600 mt-1">We&apos;re happy to see you on Ferntree.</p>
                            <p className="text-sm text-blue-500 mt-2">Ready to design your sustainable energy system?</p>
                        </div>
                    </div>
                )}
            </div>
            <div className="bg-blue-50 rounded-lg shadow-md p-6 mb-8 mt-8 max-w-2xl mx-auto">
                    <div className="flex items-center space-x-4">
                        <div>
                            <h2 className="text-xl font-bold text-blue-600">Note:</h2>
                            <p className="text-blue-400 mt-1">
                                At the moment, this application is hosted on a free server that shuts down when idle.
                                It therefore takes a minute to start. If you receive the error message
                                &apos;Application error: a client-side exception has occurred&apos; after clicking a button,
                                please wait one minute and refresh the page.
                            </p>
                        </div>
                    </div>
            </div>
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

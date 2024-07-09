import Image from "next/image";
import Link from "next/link";

export default async function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm">

        <div className="flex flex-col items-center justify-between">
          <Image
            src="/ferntree.png"
            alt="Ferntree"
            width={300}
            height={300}
          />
        </div>

        <div className="flex flex-col items-center justify-between mt-16">
          <h1 className="text-6xl font-bold text-center">
            <span className="text-blue-500">Ferntree</span>
          </h1>
          <h2 className="text-2xl text-center">
            Sustainable Energy Solutions
          </h2>
        </div>

        <div className="flex flex-col items-center justify-between text-sm mt-16">
          <Link href="/dashboard">
            <button className="mt-4 bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
              Try it out
            </button>
          </Link>
        </div>

      </div>

    </main>
  );
}

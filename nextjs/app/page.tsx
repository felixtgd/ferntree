import Image from "next/image";

export default function Home() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-between p-24">
      <div className="z-10 w-full max-w-5xl items-center justify-between font-mono text-sm lg:flex">
        <div className="flex flex-col items-center justify-between">
          <h1 className="text-6xl font-bold text-center">
            <span className="text-blue-500">Ferntree</span>
          </h1>
          <h2 className="text-2xl text-center">
            Sustainable Energy Solutions
          </h2>
        </div>
        <div className="flex flex-col items-center justify-between">
          <Image
            src="/ferntree.png"
            alt="Ferntree"
            width={500}
            height={500}
          />
        </div>
      </div>
    </main>
  );
}

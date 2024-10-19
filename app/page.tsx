import Image from "next/image";
import Link from "next/link";
import { Button } from "@tremor/react";
import ContactForm from "./components/contact-form";

export default function Home() {
  return (
    <>
      <div className="w-full flex min-h-screen items-center flex-col">
        <header className="flex items-center justify-between flex-row w-full max-w-7xl p-4 mt-4">
          <div className="flex items-center flex-row justify-start">
            <Image
              alt="image"
              width={60}
              height={60}
              src="/ferntree.png"
              className="object-cover mr-4"
            />
            <span className="text-2xl font-urbanist font-extrabold leading-tight tracking-widest uppercase">
              <span className="text-blue-500">FERN</span>
              <span className="text-green-600">TREE</span>
            </span>
          </div>
          <div className="flex items-center justify-end">
            <Link href="/workspace">
              <Button variant="primary" size="lg" className="mx-2">
                  Get started
              </Button>
            </Link>
            <Link href="/workspace">
              <Button variant="secondary" size="lg" className="mx-2">
                Log in
              </Button>
            </Link>
          </div>
        </header>
        <div className="bg-blue-500 w-full py-16">
          <div className="max-w-7xl mx-auto flex items-center">
            <div className="flex-none w-2/3 flex flex-col items-start mr-8 mb-12">
              <span className="text-white p-2 text-sm font-urbanist font-extrabold leading-tight tracking-widest uppercase mb-4">
                Sustainable Energy Solutions
              </span>
              <h1 className="text-white p-2 text-6xl font-urbanist font-semibold leading-tight mb-4">
                Design Your Home&apos;s Sustainable Energy System
              </h1>
              <span className="text-white p-2 text-xl leading-relaxed mb-8">
                Make informed decisions with Ferntree&apos;s easy-to-use tools
                for designing and assessing your ideal energy system.
              </span>
              <div className="flex w-full p-2">
                <Link href="/workspace">
                  <Button variant="primary" size="xl" className="bg-white text-blue-500 hover:bg-blue-100">
                      Get started
                  </Button>
                </Link>
                <Link href="/workspace">
                  <Button variant="secondary" size="xl" className="mx-4 bg-transparent border border-white text-white">
                    Log in
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
        <div className="w-full py-16">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-start">
            <div className="w-full md:w-1/2 flex flex-col justify-center mr-8">
              <span className="text-green-600 py-2">
                OPEN SOURCE AND FREE-TO-USE
              </span>
              <h1 className="text-green-800 text-4xl font-urbanist font-bold leading-tight mb-4">
                Your Independent Solar Calculator
              </h1>
              <span className="text-base leading-relaxed py-2 mb-12">
                <span>
                  Considering a solar system for your home?
                  You likely have questions about size, battery options, costs, and economic viability.
                  While many online calculators exist, they often come with commercial interests.
                </span>
                <br></br>
                <br></br>
                <span>
                  Ferntree offers an unbiased, free tool to help you make informed decisions.
                  Our open-source calculator allows you to:
                </span>
                <br></br>
                <br></br>
                <span>
                  <ul className="list-disc list-inside">
                    <li>Design and simulate various energy systems</li>
                    <li>Compare different setups</li>
                    <li>Customize financial parameters</li>
                    <li>Assess investment potential</li>
                  </ul>
                </span>
                <br></br>
                <span>
                  No sales pressure, no spam - just the data you need to decide what&apos;s best for your home.
                </span>
              </span>
            </div>
            <div className="w-full md:w-1/2 flex flex-col justify-center ml-8">
              <span className="text-green-600 py-2">
                HELPING YOU MAKE BETTER DECISIONS
              </span>
              <h1 className="text-green-800 text-4xl font-urbanist font-bold leading-tight mb-4">
                Unbiased decision support
              </h1>
              <span className="text-base leading-relaxed py-2 mb-12">
                <span>
                  Ferntree aims to help you in your decision-making process.
                  Whether you&apos;re tech-savvy or not, our tool provides objective data to support your choice.
                </span>
                <br></br>
                <br></br>
                <span>
                  Experiment freely with system designs, financial scenarios, and energy options.
                  You&apos;re in control - we simply provide the tools for your analysis.
                </span>
                <br></br>
                <br></br>
                <span>
                  Start exploring your solar possibilities today - it&apos;s free, unbiased, and tailored to your needs.
                </span>
              </span>
              <div className="flex">
                <Link href="/workspace">
                  <Button variant="primary" size="xl" className="bg-green-600 border-green-600 hover:bg-green-800 hover:border-green-800">
                      Get started
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>

        <div className="w-full py-16">
          <div className="max-w-7xl mx-auto flex flex-col md:flex-row justify-center items-center">
            <div className="w-full md:w-1/2 flex flex-col justify-center items-center">
              <h1 className="text-blue-500 text-4xl font-urbanist font-bold leading-tight mb-4">Contact us</h1>
              <ContactForm />
            </div>
          </div>
        </div>

        <footer className="w-full py-6">
          <div className="max-w-7xl mx-auto px-4 flex justify-center items-center">
            <span className="text-gray-600">
              © 2024 Ferntree. Check out our{' '}
              <Link
                href="https://github.com/felixtgd/ferntree"
                target="_blank"
                rel="noopener noreferrer"
                className="text-blue-500 hover:text-blue-700 underline"
              >
                GitHub repository
              </Link>
            </span>
          </div>
        </footer>
      </div>
    </>
  );
}

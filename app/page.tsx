import Image from "next/image";
import Link from "next/link";
import { Button } from "@tremor/react";

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
                Sustainable energy solutions
              </span>
              <h1 className="text-white p-2 text-6xl font-urbanist font-semibold leading-tight mb-4">
                Design and assess your own sustainable energy system for your home
              </h1>
              <span className="text-white p-2 text-xl leading-relaxed mb-8">
                Ferntree enables you to make informed decisions about your
                future energy system by providing easy-to-use tools that allow
                you to design and assess your system according to your needs.
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
            <div className="w-full md:w-1/2 flex flex-col justify-center md:ml-8">
              <span className="text-green-600 py-2">OPEN SOURCE AND FREE-TO-USE</span>
              <h1 className="text-green-800 text-4xl font-urbanist font-bold leading-tight mb-4">Your free solar calculator</h1>
              <span className="text-base leading-relaxed py-2 mb-12">
              <span>
                  When deciding whether or not to purchase a photovoltaic system
                  for your own home, you are confronted with many questions: How
                  big does the PV system need to be? Does a battery make sense?
                  How much will this investment cost and does it make economic
                  sense for me?
                </span>
                <br></br>
                <br></br>
                <span>
                  There are a large number of websites on the Internet,
                  especially solar calculators, which are supposed to help you
                  make this decision. At the same time, however, they have a
                  commercial interest in selling solar systems. These resources
                  therefore often offer distorted information to tempt potential
                  buyers into making a purchase. It is therefore almost
                  impossible to form an unbiased opinion based on objective and
                  undistorted data. In most cases, all you get is the statement
                  that an investment is worthwhile, and shortly afterwards you
                  are flooded with spam e-mails with sales offers.
                </span>
                <br></br>
                <br></br>
                <span>
                  Ferntree does not have this conflict. We simply want to
                  help people make informed decisions, so that everyone can
                  decide on their own, what type of energy system makes the most
                  sense for them.
                </span>
                <br></br>
                <br></br>
              </span>
            </div>
            <div className="w-full md:w-1/2 flex flex-col justify-center md:ml-8">
              <span className="text-green-600 py-2">HELPING YOU MAKE BETTER DECISIONS</span>
              <h1 className="text-green-800 text-4xl font-urbanist font-bold leading-tight mb-4">Unbiased decision support</h1>
              <span className="text-base leading-relaxed py-2 mb-12">
              <span>
                  The aim of Ferntree is to give people who are thinking
                  about buying a solar system the opportunity to generate the
                  data they need to make an informed decision on their own.
                  Every person, with or without technical knowledge, should be
                  able to make this decision independently, based on objective
                  data, without being influenced by the business interests of
                  others.
                </span>
                <br></br>
                <br></br>
                <span>
                  Our tool allows you to freely design and simulate different
                  energy systems, compare them with each other and set your
                  individual financial parameters. Try out for yourself when a
                  battery makes sense for you. Investigate the conditions under
                  which an investment is worthwhile for you. We don&apos;t give
                  you any guidelines. You have full control. We simply provide
                  you with the tools you need to make an informed decision on
                  your own. And best of all: it&apos;s free to use. Get started
                  now and try it out!
                </span>
                <br></br>
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

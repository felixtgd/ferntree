import Image from 'next/image';
import { SignInProvider, SignInEmail } from './sign-in';
import { Metadata } from 'next';
import Link from 'next/link';

export const metadata: Metadata = {
  title: "Login"
};

export default function LoginPage() {

  return (
    <main className="flex items-center justify-center md:h-screen">
      <div className="relative mx-auto flex w-full max-w-[500px] flex-col space-y-2.5 p-4 md:-mt-32">
        <div className="flex flex-col items-center justify-between">
          <Link href="/">
            <Image
              src="/ferntree.png"
              alt="Ferntree"
              width={200}
              height={200}
            />
          </Link>
        </div>

        <div className="flex flex-col items-center justify-between mt-16">
          <h1 className="text-2xl text-bold text-center p-2">
            <span className="text-blue-500">Hi there!</span>
          </h1>
          <h2 className="text-xl text-center p-2">
            Sign in with email or choose a provider.
          </h2>
        </div>

        <div className="flex flex-col items-center justify-between">
          <SignInEmail />
        </div>

        <div className="flex items-center justify-center w-[90%] mx-auto">
          <hr className="w-full border-t border-gray-300" />
          <span className="px-4 text-gray-500">or</span>
          <hr className="w-full border-t border-gray-300" />
        </div>

        <div className="flex flex-row items-center justify-between max-w-[400px] mx-auto">
          <SignInProvider provider="github" />
          <SignInProvider provider="google" />
        </div>
      </div>
    </main>
  );
}

import Image from 'next/image';
import SignIn from './sign-in';

export default function LoginPage() {
  return (
    <main className="flex items-center justify-center md:h-screen">
      <div className="relative mx-auto flex w-full max-w-[400px] flex-col space-y-2.5 p-4 md:-mt-32">
        <div className="flex flex-col items-center justify-between">
          <Image
            src="/ferntree.png"
            alt="Ferntree"
            width={200}
            height={200}
          />
        </div>

        <div className="flex flex-col items-center justify-between mt-16">
          <h1 className="text-2xl text-bold text-center p-2">
            <span className="text-blue-500">Hi there!</span>
          </h1>
          <h2 className="text-xl text-center p-2">
            Choose a provider to sign-in.
          </h2>
        </div>

        <div className="flex flex-row items-center justify-between">
          <SignIn provider="github" />
          <SignIn provider="google" />
          <SignIn provider="facebook" />
          <SignIn provider="apple" />
        </div>
      </div>
    </main>
  );
}

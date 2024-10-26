'use client'

import { ProviderButton, EmailSignInButton } from "./provider-button"
import signInAction from "./actions"
import { useOptimistic, useState } from "react"

export function SignInProvider({provider}: {provider: string}) {
  return (
    <form
        action={signInAction}
    >
        <input type="hidden" name="provider" value={provider} />
        <ProviderButton provider={provider}/>
    </form>
  )
}

export function SignInEmail() {

  const [isSubmitted, setIsSubmitted] = useState(false);

  type OptimisticFormState = {
    isSubmitted: boolean;
  };

  const [optimisticFormState, addOptimisticFormState] = useOptimistic<
          OptimisticFormState,
          Partial<OptimisticFormState>
      >(
      { isSubmitted: false },
      (state: OptimisticFormState, newState: Partial<OptimisticFormState>) => ({ ...state, ...newState })
  );

  const handleSubmit = async (form_data: FormData) => {
      addOptimisticFormState({ isSubmitted: true });
      await signInAction(form_data);
      setIsSubmitted(true);
  }

  if (optimisticFormState.isSubmitted || isSubmitted) {
    return (
      <div className="flex flex-col space-y-4 items-center justify-between w-full mx-auto">
        <p className="text-center">
          Please check your email for a sign-in link.
        </p>
      </div>
    )
  }

  return (
    <div className="flex flex-col space-y-4 items-center justify-between w-full mx-auto">
      <form
        action={handleSubmit}
        className="flex flex-col space-y-4 items-center justify-between w-full mx-auto">
        <input
          type="email"
          name="email"
          placeholder="Enter your email"
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />
        <input type="hidden" name="provider" value="nodemailer" />

        <EmailSignInButton />
      </form>
    </div>
  )
}

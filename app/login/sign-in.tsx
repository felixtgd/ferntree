import { signIn } from "@/auth"
import { ProviderButton, EmailSignInButton } from "./provider-button"

export function SignInProvider({provider}: {provider: string}) {
  return (
    <form
        action={async () => {
            "use server"
            await signIn(provider)
        }}
    >
        <ProviderButton provider={provider}/>
    </form>
  )
}

export function SignInEmail() {

  return (
    <div className="flex flex-col space-y-4 items-center justify-between w-full mx-auto">
      <form
        action={async (form_data: FormData) => {
          "use server"
          await signIn("nodemailer", form_data)
        }}
        className="flex flex-col space-y-4 items-center justify-between w-full mx-auto">
        <input
          type="email"
          name="email"
          placeholder="Enter your email"
          className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          required
        />

        <EmailSignInButton />
      </form>
    </div>
  )
}

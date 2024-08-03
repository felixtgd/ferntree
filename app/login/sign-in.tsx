import { signIn } from "@/auth"
import ProviderButton from "./provider-button"

export default function SignIn({provider}: {provider: string}) {
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

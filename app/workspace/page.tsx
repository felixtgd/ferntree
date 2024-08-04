import { auth } from "@/auth";
import { Session, User } from "next-auth";
import Image from "next/image";

async function getUser() {
    const session: Session | null = await auth()

    if (!session?.user) return null

    console.log(session.user)

    return session.user
}


export default async function Page() {
    const user: User | null = await getUser()

    return (
        <main>
            <div className="grid gap-4 grid-cols-5">
                <div className="col-span-1">
                    { user &&
                    <div>
                        <p> Hi {user.name} </p>
                        <p> Your user ID: {user.id}</p>
                        <p> Your email: {user.email} </p>
                        <Image src={user.image as string} width={100} height={100} alt={user.name as string}/>
                    </div>
                    }
                </div>
            </div>
        </main>
    );
}

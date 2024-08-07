import { getUser } from "@/utils/helpers";
import { User } from "next-auth";
import Image from "next/image";

export default async function Page() {
    const user: User | null = await getUser();

    return (
        <main>
            <div className="flex flew-grid flex-grow">
                    { user &&
                    <div>
                        <p> Hi {user.name} </p>
                        <p> Your user ID: {user.id}</p>
                        <p> Your email: {user.email} </p>
                        <Image src={user.image as string} width={100} height={100} alt={user.name as string}/>
                    </div>
                    }
            </div>
        </main>
    );
}

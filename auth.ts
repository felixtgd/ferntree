import NextAuth from 'next-auth';
import { MongoDBAdapter } from "@auth/mongodb-adapter"
import client from "./utils/db"
// import { z } from 'zod';
// import bcrypt from 'bcrypt';
// import Credentials from 'next-auth/providers/credentials';
import GitHub from 'next-auth/providers/github';
import Google from 'next-auth/providers/google';

// type User = {
//   id: string;
//   name: string;
//   email: string;
//   password: string;
// };

// async function getUser(email: string): Promise<User | undefined> {
//   try {
//     const password = await bcrypt.hash('123456789', 10);
//     const user = { id: '1', name: 'Test User', email: email, password: password};
//      //await sql<User>`SELECT * FROM users WHERE email=${email}`;
//     return user //.rows[0];
//   } catch (error) {
//     console.error('Failed to fetch user:', error);
//     throw new Error('Failed to fetch user.');
//   }
// }

export const { handlers, signIn, signOut, auth } = NextAuth({

  pages: {
    signIn: '/login',
  },

  callbacks: {
    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isInWorkspace = nextUrl.pathname.startsWith('/workspace');
      // const isInWorkspace = nextUrl.pathname.startsWith('/test');
      if (isInWorkspace) {
        if (isLoggedIn) return true;
        return false; // Redirect unauthenticated users to login page
      } else if (isLoggedIn) {
        return Response.redirect(new URL('/workspace', nextUrl));
      }
      return true;
    },
  },

  adapter: MongoDBAdapter(client),

  providers: [
    GitHub,
    Google,
    // Credentials({
    //   async authorize(credentials) {
    //     const parsedCredentials = z
    //       .object({ email: z.string().email(), password: z.string().min(6) })
    //       .safeParse(credentials);

    //     if (parsedCredentials.success) {
    //       const { email, password } = parsedCredentials.data;
    //       const user = await getUser(email);
    //       if (!user) return null;
    //       const passwordsMatch = await bcrypt.compare(password, user.password);

    //       if (passwordsMatch) return user;
    //     }

    //     console.log('Invalid credentials');
    //     return null;
    //   },
    // }),
  ],
});

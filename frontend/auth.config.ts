import type { NextAuthConfig, Session, User } from "next-auth";
import { JWT } from "next-auth/jwt";
import GitHub from 'next-auth/providers/github';
import Google from 'next-auth/providers/google';


export default {

  pages: {
    signIn: '/login',
  },

  providers: [
    GitHub,
    Google,
  ],

  callbacks: {

    authorized({ auth, request: { nextUrl } }) {
      const isLoggedIn = !!auth?.user;
      const isInWorkspace = nextUrl.pathname.startsWith('/workspace');
      if (isInWorkspace) {
        if (isLoggedIn) return true;
        return false; // Redirect unauthenticated users to login page
      } else if (isLoggedIn) {
        return Response.redirect(new URL('/workspace', nextUrl));
      }
      return true;
    },

    jwt({ token, user } : { token: JWT, user: User }) {
      if (user) { // User is available during sign-in
        token.id = user.id
      }
      return token
    },

    session({ session, token } : { session: Session, token: JWT }) {
      if (token && session.user) {
        const id: string = token.id as string
        session.user.id = id
      }

      return session
    },
  },

} satisfies NextAuthConfig

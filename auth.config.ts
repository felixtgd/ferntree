import type { NextAuthConfig } from "next-auth";
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

} satisfies NextAuthConfig

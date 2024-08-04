import NextAuth from 'next-auth';
import authConfig from "@/auth.config";

import { MongoDBAdapter } from "@auth/mongodb-adapter";
import client from "@/utils/db";


export const { handlers, signIn, signOut, auth } = NextAuth({
  ...authConfig,

  adapter: MongoDBAdapter(client),

  session: { strategy: "jwt" },

});

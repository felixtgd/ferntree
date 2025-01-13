import NextAuth from 'next-auth';
import authConfig from "@/auth.config";

import { MongoDBAdapter } from "@auth/mongodb-adapter";
import client from "@/app/utils/db";
import Nodemailer from 'next-auth/providers/nodemailer';


export const { handlers, signIn, signOut, auth } = NextAuth({
  ...authConfig,

  adapter: MongoDBAdapter(client),

  providers: [
    ...authConfig.providers,
    Nodemailer({
      server: {
        host: process.env.EMAIL_HOST,
        port: process.env.EMAIL_PORT ? parseInt(process.env.EMAIL_PORT, 10) : undefined,
        auth: {
          user: process.env.EMAIL_SENDER,
          pass: process.env.EMAIL_PASS,
        },
      },
      from: process.env.EMAIL_SENDER,
    }),
  ],

  // session: { strategy: "database" },
  session: { strategy: "jwt" },

});

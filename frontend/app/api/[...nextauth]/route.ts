import { handlers } from "@/auth";

export const { GET, POST } = handlers

export const runtime = "nodejs" // crucial! don't use edge runtime, because some modules are not supported

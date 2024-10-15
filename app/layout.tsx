import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: {
    template: "Ferntree | %s",
    default: "Ferntree",
  },
  description: "Design and assess your own sustainable energy system for your home",
  keywords: ["solar energy", "sustainable energy", "home energy system", "solar calculator"],

  authors: [{ name: 'Felix', url: 'https://github.com/felixtgd' }],
  creator: 'Felix Tangerding',
  publisher: 'Felix Tangerding',
  formatDetection: {
    email: false,
    address: false,
    telephone: false,
  },

  openGraph: {
    title: 'Ferntree',
    description: 'Design and assess your own sustainable energy system for your home',
    type: 'website',
    url: 'https://www.ferntree.dev/',
    siteName: 'Ferntree',
    images: [
      {
        url: 'https://www.ferntree.dev/ferntree.png',
        width: 600,
        height: 600,
        alt: 'Ferntree - Sustainable Energy Solutions',
      },
    ],
  },

  icons: {
    icon: '/favicon.ico',
  },

  metadataBase: new URL('https://ferntree.dev'),
  alternates: {
    canonical: '/',
  },

  robots: {
    index: false,
    follow: true,
    nocache: true,
    googleBot: {
      index: true,
      follow: false,
      noimageindex: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default async function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>{children}</body>
    </html>
  );
}

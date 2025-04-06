import type { Metadata } from "next";
import localFont from "next/font/local";
import "./globals.css";
import Logo from "@/components/logo";
import { ThemeProvider } from "@/components/theme-provider";
import Link from "next/link";

const geistSans = localFont({
  src: "./fonts/GeistVF.woff",
  variable: "--font-geist-sans",
  weight: "100 900",
});
const geistMono = localFont({
  src: "./fonts/GeistMonoVF.woff",
  variable: "--font-geist-mono",
  weight: "100 900",
});

export const metadata: Metadata = {
  title: "NCSU SG",
  description:
    "A tool to understand the inner workings of NCSU's student government.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} bg-black antialiased`}
      >
        <ThemeProvider
          attribute="class"
          defaultTheme="dark"
          enableSystem
          disableTransitionOnChange
        >
          <Link href="/">
            <Logo />
          </Link>
          {children}
        </ThemeProvider>
      </body>
    </html>
  );
}

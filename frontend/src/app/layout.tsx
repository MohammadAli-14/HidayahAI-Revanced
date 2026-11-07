import type { Metadata } from "next";
import { Inter, Cormorant_Garamond, Amiri } from "next/font/google";
import "./globals.css";

const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
  display: "swap",
});

const cormorant = Cormorant_Garamond({
  variable: "--font-cormorant",
  subsets: ["latin"],
  weight: ["500", "600", "700"],
  display: "swap",
});

const amiri = Amiri({
  variable: "--font-amiri",
  subsets: ["arabic", "latin"],
  weight: ["400", "700"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "Hidayah AI — Quranic Research & Theological Companion",
  description: "Elite 30-Day Ramadan Research Companion, Hadith Takhrīj, and Multilingual Audio Recitation.",
  icons: {
    icon: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      className={`dark ${inter.variable} ${cormorant.variable} ${amiri.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col bg-[#0B0F17] text-slate-100 font-sans selection:bg-[#D4AF37]/30 selection:text-white">
        {children}
      </body>
    </html>
  );
}

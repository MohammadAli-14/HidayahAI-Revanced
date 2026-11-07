"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { BookOpen, Sparkles, ArrowLeft, Headphones } from "lucide-react";
import { HidayahEmblem } from "@/components/navigation/HidayahEmblem";
import { NamesGrid } from "@/components/names/NamesGrid";
import { fetchNamesOfAllah, fetchNameCategories, NameOfAllah, NameCategory } from "@/lib/api";

export default function NamesOfAllahPage() {
  const [names, setNames] = useState<NameOfAllah[]>([]);
  const [categories, setCategories] = useState<NameCategory[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      setIsLoading(true);
      try {
        const [namesData, catsData] = await Promise.all([
          fetchNamesOfAllah(),
          fetchNameCategories(),
        ]);
        setNames(namesData);
        setCategories(catsData);
      } finally {
        setIsLoading(false);
      }
    }
    loadData();
  }, []);

  return (
    <div className="min-h-screen bg-[#0B0F17] text-slate-100 flex flex-col font-sans selection:bg-[#D4AF37]/30 selection:text-white">
      {/* Sacred Top Navigation Header */}
      <header className="sticky top-0 z-30 h-16 glass-header px-4 lg:px-8 flex items-center justify-between border-b border-white/[0.08] bg-[#0B0F17]/90 backdrop-blur-xl">
        <div className="flex items-center space-x-3">
          <Link
            href="/"
            className="flex items-center space-x-2 px-3 py-1.5 rounded-xl bg-black/40 hover:bg-[#D4AF37]/15 border border-white/10 hover:border-[#D4AF37]/50 text-slate-300 hover:text-[#D4AF37] text-xs transition-all cursor-pointer group"
            title="Return to Quran Reader"
          >
            <ArrowLeft className="w-3.5 h-3.5 text-[#D4AF37] group-hover:-translate-x-0.5 transition-transform" />
            <span className="font-medium">Quran Reader</span>
          </Link>

          <div className="h-4 w-px bg-white/10 hidden sm:block" />

          <div className="flex items-center space-x-2.5">
            <HidayahEmblem className="w-8 h-8 rounded-xl shadow-md shadow-black/50" />
            <div>
              <h1 className="text-sm sm:text-base font-serif font-bold text-white tracking-wide flex items-center gap-2">
                <span>أسماء الله الحسنى</span>
                <span className="text-[11px] font-mono font-normal text-[#D4AF37] px-2 py-0.5 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/30 hidden md:inline">
                  99 Divine Names
                </span>
              </h1>
            </div>
          </div>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            href="/?juz=1"
            className="hidden sm:flex items-center space-x-2 px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-[#D4AF37]/20 to-[#D4AF37]/10 border border-[#D4AF37]/40 text-[#D4AF37] text-xs font-semibold hover:border-[#D4AF37] transition-all shadow-sm"
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Open Mushaf Reader</span>
          </Link>
        </div>
      </header>

      {/* Hero Presentation & Canonical Hadith Banner */}
      <section className="relative overflow-hidden pt-10 pb-6 px-4 sm:px-6 lg:px-8 border-b border-white/[0.06] bg-gradient-to-b from-[#0F172A]/70 via-[#0B0F17] to-[#0B0F17]">
        <div className="max-w-4xl mx-auto text-center space-y-4">
          <div className="inline-flex items-center space-x-2 px-3.5 py-1 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/30 text-xs font-medium text-[#D4AF37]">
            <Sparkles className="w-3.5 h-3.5 text-[#D4AF37]" />
            <span>Theological Contemplation & Devotion</span>
          </div>

          <h2 className="text-3xl sm:text-4xl lg:text-5xl font-serif font-bold text-white tracking-tight drop-shadow-md">
            The 99 Beautiful Names of Allah
          </h2>

          <p className="text-xs sm:text-sm text-slate-300 max-w-2xl mx-auto leading-relaxed">
            Contemplate the transcendent attributes{" "}
            <span className="font-serif italic text-[#D4AF37] font-semibold">
              (Ṣifāt / الصِّفَات)
            </span>{" "}
            of Allah through vocalized Arabic calligraphy, classical root derivations, trilingual commentary, and direct Quranic cross-referencing.
          </p>

          {/* Canonical Hadith Card */}
          <div className="rounded-2xl bg-black/40 border border-[#D4AF37]/35 p-5 max-w-2xl mx-auto text-center shadow-xl relative overflow-hidden">
            <div className="absolute top-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent" />
            <p className="font-serif text-lg sm:text-2xl text-white font-bold leading-loose tracking-wide py-1" dir="rtl">
              &quot;إِنَّ لِلَّهِ تِسْعَةً وَتِسْعِينَ اسْمًا مِائَةً إِلَّا وَاحِدًا مَنْ أَحْصَاهَا دَخَلَ الْجَنَّةَ&quot;
            </p>
            <p className="text-xs text-[#D4AF37] mt-2 font-medium font-sans">
              &quot;To Allah belong ninety-nine names, one hundred less one; whoever enumerates/learns them will enter Paradise.&quot;
            </p>
            <span className="text-[10px] text-slate-400 font-mono mt-1 block">
              — Sahih al-Bukhari 2736 • Sahih Muslim 2677
            </span>
          </div>
        </div>
      </section>

      {/* Main Content Area */}
      <main className="flex-1">
        {isLoading ? (
          <div className="max-w-7xl mx-auto px-4 py-20 text-center space-y-3">
            <div className="w-10 h-10 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin mx-auto" />
            <p className="text-xs text-slate-400 font-mono tracking-wide">
              Loading canonical 99 Divine Names...
            </p>
          </div>
        ) : (
          <NamesGrid initialNames={names} categories={categories} />
        )}
      </main>

      {/* Sacred Footer */}
      <footer className="border-t border-white/[0.06] py-6 px-4 text-center text-xs text-slate-400 bg-black/40">
        <p>Hidayah AI — Theological Research & Quranic Companion</p>
        <p className="text-[10px] text-slate-400 mt-1">
          Rooted in Ahl al-Sunnah wal-Jama&apos;ah scholarly consensus • Authentic Quran & Hadith citations
        </p>
      </footer>
    </div>
  );
}

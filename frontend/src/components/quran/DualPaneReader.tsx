"use client";

import React, { useEffect, useRef, useState } from "react";
import { Play, Pause, BookOpen, Copy, Check, Sparkles, ServerOff, RefreshCw } from "lucide-react";
import { Ayah } from "@/lib/api";

interface DualPaneReaderProps {
  ayahs: Ayah[];
  currentAyahIndex: number;
  isPlaying: boolean;
  onPlayAyah: (index: number) => void;
  onOpenContext: (ayah: Ayah) => void;
  audioMode?: string;
  isLoading?: boolean;
  isGatewayOffline?: boolean;
  onRetryConnection?: () => void;
}

export function DualPaneReader({
  ayahs,
  currentAyahIndex,
  isPlaying,
  onPlayAyah,
  onOpenContext,
  audioMode = "Arabic (Mishary Rashid)",
  isLoading = false,
  isGatewayOffline = false,
  onRetryConnection,
}: DualPaneReaderProps) {
  const activeRowRef = useRef<HTMLDivElement | null>(null);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  // Smoothly scroll active verse into viewport center when audio advances
  useEffect(() => {
    if (activeRowRef.current && isPlaying) {
      activeRowRef.current.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }
  }, [currentAyahIndex, isPlaying]);

  const handleCopyAyah = (ayah: Ayah, idx: number) => {
    const textToCopy = `${ayah.arabic}\n\n[${ayah.surah_name} ${ayah.surah_number}:${ayah.number_in_surah}]\nEnglish: ${ayah.english}\nUrdu: ${ayah.urdu}`;
    navigator.clipboard.writeText(textToCopy);
    setCopiedIndex(idx);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  // Sacred Quran Skeleton Loader when transitioning between Juz or Surah
  if (isLoading) {
    return (
      <div className="max-w-5xl mx-auto px-3 sm:px-6 py-6 space-y-6 animate-pulse">
        {/* Shimmering Chapter Header Skeleton */}
        <div className="relative text-center py-8 px-4 rounded-3xl glass-panel border border-[#D4AF37]/30 my-6 bg-gradient-to-b from-[#101725] to-[#070A10] shadow-xl space-y-3">
          <div className="w-28 h-5 rounded-full bg-[#D4AF37]/20 border border-[#D4AF37]/30 mx-auto" />
          <div className="w-56 h-8 rounded-xl bg-white/10 mx-auto" />
          <div className="w-36 h-4 rounded-lg bg-white/5 mx-auto" />
          <div className="w-72 h-8 rounded-xl bg-white/[0.08] mx-auto mt-3" />
          <p className="text-[11px] text-[#D4AF37]/80 font-mono tracking-widest uppercase pt-2 flex items-center justify-center gap-2">
            <span className="w-2 h-2 rounded-full bg-[#D4AF37] animate-ping" />
            <span>Retrieving Sacred Verses & Translations...</span>
          </p>
        </div>

        {/* 3 Ayah Row Skeletons */}
        {[1, 2, 3].map((placeholder) => (
          <div
            key={placeholder}
            className="rounded-2xl border border-white/[0.06] glass-panel overflow-hidden"
          >
            <div className="grid grid-cols-1 xl:grid-cols-2 divide-y xl:divide-y-0 xl:divide-x xl:divide-x-reverse divide-white/[0.06]">
              {/* Arabic Pane Skeleton */}
              <div className="p-6 bg-black/15 space-y-4">
                <div className="flex justify-between items-center">
                  <div className="w-8 h-8 rounded-xl bg-[#D4AF37]/15 border border-[#D4AF37]/30" />
                  <div className="w-24 h-4 rounded bg-white/5" />
                </div>
                <div className="space-y-3 py-2">
                  <div className="w-full h-7 rounded-lg bg-white/[0.07]" />
                  <div className="w-4/5 h-7 rounded-lg bg-white/[0.07] ml-auto" />
                  <div className="w-3/5 h-7 rounded-lg bg-white/[0.07] ml-auto" />
                </div>
                <div className="pt-3 border-t border-white/[0.05] flex justify-between">
                  <div className="w-20 h-6 rounded-lg bg-white/5" />
                  <div className="w-6 h-6 rounded-lg bg-white/5" />
                </div>
              </div>

              {/* Translation Pane Skeleton */}
              <div className="p-6 bg-black/5 space-y-4">
                <div className="p-3.5 rounded-xl bg-black/30 border border-white/[0.04] space-y-2">
                  <div className="w-32 h-3.5 rounded bg-[#D4AF37]/20" />
                  <div className="w-full h-4 rounded bg-white/5" />
                  <div className="w-5/6 h-4 rounded bg-white/5" />
                </div>
                <div className="p-3.5 rounded-xl bg-emerald-950/20 border border-emerald-900/20 space-y-2">
                  <div className="w-36 h-3.5 rounded bg-emerald-500/20 ml-auto" />
                  <div className="w-full h-4 rounded bg-white/5" />
                  <div className="w-4/6 h-4 rounded bg-white/5 ml-auto" />
                </div>
                <div className="pt-3 border-t border-white/[0.05] flex justify-between">
                  <div className="w-28 h-6 rounded-lg bg-white/5" />
                  <div className="w-16 h-4 rounded bg-white/5" />
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    );
  }

  if (!ayahs || ayahs.length === 0) {
    if (isGatewayOffline) {
      return (
        <div className="relative max-w-xl mx-auto my-12 p-8 rounded-3xl bg-gradient-to-b from-[#101725] to-[#070A10] border border-[#D4AF37]/30 shadow-2xl text-center space-y-5 overflow-hidden">
          <div className="absolute -top-24 left-1/2 -translate-x-1/2 w-72 h-32 bg-[#D4AF37]/10 blur-3xl pointer-events-none rounded-full" />
          
          <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/30 flex items-center justify-center mx-auto text-amber-400">
            <ServerOff className="w-8 h-8" />
          </div>

          <div className="space-y-1">
            <span className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-mono font-medium tracking-wide uppercase bg-amber-500/10 border border-amber-500/30 text-amber-300">
              <span className="w-2 h-2 rounded-full bg-amber-400 animate-pulse" />
              FastAPI Gateway Offline
            </span>
            <h3 className="text-xl font-serif text-slate-100 tracking-wide pt-2">
              Theological Gateway Connection Required
            </h3>
            <p className="text-slate-400 text-xs sm:text-sm leading-relaxed max-w-md mx-auto">
              Next.js is running on Port 3000, but cannot reach the Python API on Port 8001. Start the unified platform runner:
            </p>
          </div>

          <div className="bg-black/60 border border-white/[0.08] rounded-xl p-3 text-left font-mono text-xs text-amber-200/90 space-y-1">
            <div className="text-slate-500 text-[10px] uppercase tracking-wider font-sans">Run in terminal:</div>
            <div>python run_platform.py</div>
            <div className="text-slate-500 text-[11px]"># or: .\run.ps1</div>
          </div>

          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            {onRetryConnection && (
              <button
                onClick={onRetryConnection}
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 px-5 py-2.5 rounded-xl bg-gradient-to-r from-[#D4AF37] to-[#B38F26] text-black font-semibold text-sm hover:brightness-110 active:scale-95 transition-all shadow-lg shadow-[#D4AF37]/10 cursor-pointer"
              >
                <RefreshCw className="w-4 h-4" />
                <span>Retry Connection</span>
              </button>
            )}
          </div>

          <div className="flex items-center justify-center gap-2 text-xs text-slate-500 pt-1">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
            <span>Auto-detecting gateway on port 8001 every 4s...</span>
          </div>
        </div>
      );
    }

    return (
      <div className="flex flex-col items-center justify-center min-h-[50vh] text-center p-8">
        <div className="w-16 h-16 rounded-2xl bg-white/5 border border-[#D4AF37]/30 flex items-center justify-center mb-4 text-3xl shadow-xl">
          📖
        </div>
        <p className="text-slate-300 font-serif text-lg">Loading Quranic Scripture...</p>
        <p className="text-slate-500 text-xs mt-1">Retrieving canonical Arabic, Urdu, and English texts.</p>
      </div>
    );
  }

  // Determine which translations to display based on mode
  const showEnglish =
    audioMode !== "Urdu Translation Only";
  const showUrdu =
    audioMode !== "English Translation Only";

  return (
    <div className="max-w-5xl mx-auto px-3 sm:px-6 py-6 space-y-6">
      {ayahs.map((ayah, idx) => {
        const isActive = idx === currentAyahIndex;
        const isFirstAyahOfSurah = ayah.number_in_surah === 1;

        return (
          <div key={ayah.number} className="space-y-4">
            {/* Surah Bismillah Banner with Noble Hover Interaction */}
            {isFirstAyahOfSurah && (
              <div
                className="relative text-center py-7 px-4 rounded-3xl glass-panel border border-[#D4AF37]/35 my-8 bg-gradient-to-b from-[#101725] to-[#070A10] shadow-xl hover:border-[#D4AF37]/75 hover:shadow-[0_0_35px_rgba(212,175,55,0.2)] hover:-translate-y-0.5 transition-all duration-300 group cursor-default"
                title={`Surah ${ayah.surah_name} (Chapter ${ayah.surah_number})`}
              >
                {/* Subtle Islamic corner ornaments */}
                <div className="absolute top-3 left-4 text-xs text-[#D4AF37]/40 group-hover:text-[#D4AF37]/90 transition-colors">
                  ✦
                </div>
                <div className="absolute top-3 right-4 text-xs text-[#D4AF37]/40 group-hover:text-[#D4AF37]/90 transition-colors">
                  ✦
                </div>

                <div className="inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/25 mb-2.5 group-hover:bg-[#D4AF37]/20 group-hover:border-[#D4AF37]/50 transition-colors">
                  <Sparkles className="w-3 h-3 text-[#D4AF37]" />
                  <span className="text-[10px] font-bold tracking-widest text-[#D4AF37] uppercase">
                    Chapter {ayah.surah_number}
                  </span>
                </div>

                <h3 className="text-2xl sm:text-3xl font-serif font-bold text-white tracking-wider mb-1.5 group-hover:text-[#F3E5AB] transition-colors">
                  Surah {ayah.surah_name}
                </h3>

                <p className="text-xs sm:text-sm text-slate-400 font-sans tracking-wide mb-3 group-hover:text-slate-300 transition-colors">
                  {ayah.surah_english_name}
                </p>

                {ayah.surah_number !== 9 && (
                  <p className="quran-arabic text-2xl sm:text-3xl text-slate-200 mt-2 select-text group-hover:text-white transition-colors">
                    بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ
                  </p>
                )}
              </div>
            )}

            {/* Ayah Row: Dual Pane Card with Respectful Hover Feedback */}
            <div
              id={`ayah-${idx}`}
              ref={isActive ? activeRowRef : null}
              className={`rounded-2xl border transition-all duration-300 overflow-hidden ${
                isActive
                  ? "active-verse-card border-[#D4AF37]/85 shadow-2xl shadow-black/60 ring-1 ring-[#D4AF37]/30"
                  : "glass-panel border-white/[0.08] hover:border-[#D4AF37]/45 hover:shadow-lg hover:shadow-black/50 hover:bg-white/[0.015]"
              }`}
            >
              <div className="grid grid-cols-1 xl:grid-cols-2 divide-y xl:divide-y-0 xl:divide-x xl:divide-x-reverse divide-white/[0.08]">
                {/* Arabic Pane (RTL) */}
                <div className="p-5 sm:p-7 flex flex-col justify-between bg-black/15">
                  <div className="flex items-center justify-between mb-4">
                    <span className="w-8 h-8 rounded-xl border border-[#D4AF37]/40 bg-[#D4AF37]/15 flex items-center justify-center text-xs font-serif font-bold text-[#D4AF37] shadow-sm">
                      {ayah.number_in_surah}
                    </span>
                    <span className="text-[11px] font-mono text-slate-400 tracking-wide">
                      {ayah.surah_name} {ayah.surah_number}:{ayah.number_in_surah}
                    </span>
                  </div>

                  <p className="quran-arabic text-2xl sm:text-3xl text-right text-slate-100 leading-[2.5] select-text my-2">
                    {ayah.arabic}
                    <span className="inline-block mx-2 text-[#D4AF37] text-2xl font-serif">
                      ۝
                    </span>
                  </p>

                  <div className="mt-4 pt-3 border-t border-white/[0.06] flex items-center justify-between">
                    <button
                      onClick={() => onPlayAyah(idx)}
                      className={`flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold transition-all cursor-pointer ${
                        isActive && isPlaying
                          ? "bg-[#D4AF37] text-black shadow-md shadow-[#D4AF37]/30"
                          : "bg-white/[0.04] hover:bg-[#D4AF37]/20 text-slate-300 hover:text-[#D4AF37] border border-white/5"
                      }`}
                    >
                      {isActive && isPlaying ? (
                        <>
                          <Pause className="w-3.5 h-3.5 fill-current" />
                          <span>Pause</span>
                        </>
                      ) : (
                        <>
                          <Play className="w-3.5 h-3.5 fill-current" />
                          <span>Recite</span>
                        </>
                      )}
                    </button>

                    <button
                      onClick={() => handleCopyAyah(ayah, idx)}
                      className="p-1.5 text-slate-400 hover:text-[#D4AF37] transition-colors rounded-lg hover:bg-white/5 cursor-pointer"
                      title="Copy Arabic & Translations"
                    >
                      {copiedIndex === idx ? (
                        <Check className="w-3.5 h-3.5 text-emerald-400" />
                      ) : (
                        <Copy className="w-3.5 h-3.5" />
                      )}
                    </button>
                  </div>
                </div>

                {/* Translation & Exegesis Pane (Synchronized with Mode) */}
                <div className="p-5 sm:p-7 flex flex-col justify-between space-y-4 bg-black/5">
                  <div className="space-y-4">
                    {/* English Translation (Hidden if Urdu Only selected) */}
                    {showEnglish && (
                      <div className="p-3.5 rounded-xl bg-black/30 border border-white/[0.06]">
                        <span className="text-[10px] font-bold tracking-widest uppercase text-[#D4AF37]/90 mb-1.5 block">
                          English (Muhammad Asad)
                        </span>
                        <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans select-text">
                          {ayah.english}
                        </p>
                      </div>
                    )}

                    {/* Urdu Translation (Hidden if English Only selected) */}
                    {showUrdu && ayah.urdu && (
                      <div className="p-3.5 rounded-xl bg-emerald-950/25 border border-emerald-800/35 shadow-inner">
                        <span className="text-[10px] font-bold tracking-widest uppercase text-emerald-400 mb-1.5 flex items-center justify-end gap-1.5">
                          <span>اردو (مولانا فتح محمد جالندھری)</span>
                          <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                        </span>
                        <p className="urdu-text text-base sm:text-lg text-right text-emerald-100 select-text font-medium leading-[2.3]">
                          {ayah.urdu}
                        </p>
                      </div>
                    )}
                  </div>

                  {/* Actions Bar */}
                  <div className="pt-3 border-t border-white/[0.06] flex items-center justify-between">
                    <button
                      onClick={() => onOpenContext(ayah)}
                      className="flex items-center space-x-1.5 text-xs text-[#D4AF37] hover:text-[#F3E5AB] transition-colors py-1.5 px-3 rounded-xl bg-[#D4AF37]/10 hover:bg-[#D4AF37]/20 border border-[#D4AF37]/30 cursor-pointer"
                    >
                      <BookOpen className="w-3.5 h-3.5" />
                      <span>Exegesis & Hadiths</span>
                    </button>

                    <span className="text-[10px] text-slate-400 font-mono">
                      Ayah {ayah.number} overall
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

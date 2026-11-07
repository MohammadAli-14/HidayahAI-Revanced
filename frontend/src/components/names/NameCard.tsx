"use client";

import React from "react";
import { Play, Pause, Volume2, Sparkles, BookOpen } from "lucide-react";
import { NameOfAllah } from "@/lib/api";

interface NameCardProps {
  name: NameOfAllah;
  onSelect: (name: NameOfAllah) => void;
  onOpenDetail?: (name: NameOfAllah) => void;
  onShowToast?: (msg: string) => void;
  isActivelyPlayingContinuous?: boolean;
}

export function NameCard({
  name,
  onSelect,
  onOpenDetail,
  onShowToast,
  isActivelyPlayingContinuous = false,
}: NameCardProps) {
  const handlePlayAudio = (e: React.MouseEvent) => {
    e.stopPropagation();
    onSelect(name);
  };

  const handleOpenDetail = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (onOpenDetail) {
      onOpenDetail(name);
    } else {
      onSelect(name);
    }
  };

  return (
    <div
      id={`name-card-${name.id}`}
      onClick={() => onSelect(name)}
      className={`group relative rounded-2xl p-5 transition-all duration-300 cursor-pointer flex flex-col justify-between overflow-hidden border ${
        isActivelyPlayingContinuous
          ? "bg-gradient-to-b from-[#0F172A] via-[#064E3B]/20 to-[#0B0F17] border-[#D4AF37] ring-2 ring-[#D4AF37] shadow-2xl shadow-[#D4AF37]/25 scale-[1.02]"
          : "bg-gradient-to-b from-[#0F172A] to-[#0B0F17] border-white/10 hover:border-[#D4AF37]/60 hover:shadow-2xl hover:shadow-[#D4AF37]/10"
      }`}
    >
      {/* Decorative Golden Top Shimmer */}
      <div
        className={`absolute top-0 left-0 right-0 h-[2.5px] bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent transition-opacity duration-300 ${
          isActivelyPlayingContinuous ? "opacity-100" : "opacity-0 group-hover:opacity-100"
        }`}
      />

      {/* Header: Number Badge & Category Pill */}
      <div className="flex items-center justify-between mb-3">
        <div
          className={`w-7 h-7 rounded-lg border flex items-center justify-center font-mono text-xs font-bold transition-colors ${
            isActivelyPlayingContinuous
              ? "bg-[#D4AF37] text-black border-[#D4AF37]"
              : "bg-black/60 border-[#D4AF37]/40 text-[#D4AF37] shadow-inner"
          }`}
        >
          {name.number}
        </div>

        <div className="flex items-center space-x-1.5">
          {isActivelyPlayingContinuous && (
            <span className="flex items-center space-x-0.5 px-2 py-0.5 rounded-full bg-[#D4AF37]/20 border border-[#D4AF37]/60 text-[10px] text-[#D4AF37] font-semibold animate-pulse">
              <span className="w-1 h-2.5 bg-[#D4AF37] rounded-full animate-bounce" />
              <span className="w-1 h-3.5 bg-[#D4AF37] rounded-full animate-bounce [animation-delay:0.15s]" />
              <span className="w-1 h-2 bg-[#D4AF37] rounded-full animate-bounce [animation-delay:0.3s]" />
              <span className="ml-1">Reciting</span>
            </span>
          )}

          <span className="text-[10px] px-2.5 py-0.5 rounded-full bg-[#064E3B]/40 border border-[#064E3B] text-emerald-300 font-medium tracking-wide truncate max-w-[130px]">
            {name.category}
          </span>
        </div>
      </div>

      {/* Center: Arabic Calligraphy */}
      <div className="text-center my-3">
        <h3 className="font-serif text-3xl font-bold text-white group-hover:text-[#D4AF37] transition-colors tracking-wide leading-relaxed drop-shadow-sm">
          {name.name_ar}
        </h3>
        <p className="text-xs font-semibold text-[#D4AF37] tracking-wider uppercase mt-1">
          {name.transliteration}
        </p>
      </div>

      {/* Translations: English & Urdu */}
      <div className="border-t border-white/[0.06] pt-3 mt-1 space-y-1 text-center">
        <p className="text-xs text-slate-300 font-medium line-clamp-1">
          {name.meaning_en}
        </p>
        <p className="text-xs text-slate-400 font-serif line-clamp-1 text-right" dir="rtl">
          {name.meaning_ur}
        </p>
      </div>

      {/* Footer Actions: Audio Pronunciation & Details */}
      <div className="flex items-center justify-between mt-4 pt-2 border-t border-white/[0.04]">
        <button
          onClick={handlePlayAudio}
          className={`p-2 rounded-xl border transition-all cursor-pointer flex items-center space-x-1.5 text-xs ${
            isActivelyPlayingContinuous
              ? "bg-[#D4AF37] border-[#D4AF37] text-black shadow-md shadow-[#D4AF37]/20 font-bold"
              : "bg-black/40 border-white/10 hover:border-[#D4AF37]/50 text-slate-300 hover:text-[#D4AF37]"
          }`}
          title={`Listen to ${name.transliteration}`}
          aria-label={`Listen to ${name.transliteration}`}
        >
          {isActivelyPlayingContinuous ? (
            <>
              <Pause className="w-3.5 h-3.5 fill-current" />
              <span className="text-[10px]">Playing</span>
            </>
          ) : (
            <>
              <Volume2 className="w-3.5 h-3.5 text-[#D4AF37]" />
              <span className="text-[10px] font-medium hidden sm:inline">Recite</span>
            </>
          )}
        </button>

        <button
          onClick={handleOpenDetail}
          className="text-[11px] text-slate-400 hover:text-[#D4AF37] flex items-center space-x-1 transition-colors cursor-pointer bg-white/[0.04] hover:bg-white/[0.08] px-2.5 py-1.5 rounded-lg border border-white/5 hover:border-[#D4AF37]/30"
          title="Open Tafseer, Hadith & Tasbih"
        >
          <span>Explore</span>
          <BookOpen className="w-3 h-3 text-[#D4AF37]" />
        </button>
      </div>
    </div>
  );
}

"use client";

import React, { useState, useEffect, useRef } from "react";
import { Search, X, BookOpen, ChevronRight, CornerDownLeft, Sparkles, Layers } from "lucide-react";
import { fetchSurahs, SurahMeta, JuzMeta } from "@/lib/api";

interface SearchModalProps {
  isOpen: boolean;
  onClose: () => void;
  juzs: JuzMeta[];
  onSelectJuz: (id: number) => void;
  onSelectSurah?: (surahNumber: number) => void;
}

export function SearchModal({
  isOpen,
  onClose,
  juzs,
  onSelectJuz,
  onSelectSurah,
}: SearchModalProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [surahs, setSurahs] = useState<SurahMeta[]>([]);
  const [activeTab, setActiveTab] = useState<"all" | "surahs" | "juzs">("all");
  const inputRef = useRef<HTMLInputElement | null>(null);

  useEffect(() => {
    if (isOpen) {
      setTimeout(() => inputRef.current?.focus(), 50);
      if (surahs.length === 0) {
        fetchSurahs().then(setSurahs).catch(console.error);
      }
    }
  }, [isOpen, surahs.length]);

  // Handle Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  if (!isOpen) return null;

  const term = searchTerm.toLowerCase().trim();

  // Filter Surahs
  const filteredSurahs = surahs.filter((s) => {
    if (!term) return true;
    return (
      s.englishName.toLowerCase().includes(term) ||
      s.englishNameTranslation.toLowerCase().includes(term) ||
      s.name.includes(term) ||
      s.number.toString() === term ||
      `surah ${s.number}`.includes(term)
    );
  });

  // Filter Juzs
  const filteredJuzs = juzs.filter((j) => {
    if (!term) return true;
    return (
      j.name.toLowerCase().includes(term) ||
      j.english.toLowerCase().includes(term) ||
      j.arabic.includes(term) ||
      j.surahs.toLowerCase().includes(term) ||
      j.id.toString() === term ||
      `juz ${j.id}`.includes(term)
    );
  });

  const displayedSurahs = activeTab === "all" ? filteredSurahs.slice(0, 20) : filteredSurahs;
  const displayedJuzs = activeTab === "all" ? filteredJuzs.slice(0, 10) : filteredJuzs;

  return (
    <div className="fixed inset-0 z-50 flex items-start justify-center pt-14 sm:pt-20 p-3 bg-black/80 backdrop-blur-md">
      <div
        className="w-full max-w-2xl glass-panel border border-[#D4AF37]/35 rounded-2xl flex flex-col shadow-2xl bg-[#090D17]/95 overflow-hidden animate-in fade-in zoom-in-95 duration-200"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Search Input Box */}
        <div className="p-4 border-b border-white/[0.08] flex items-center space-x-3 bg-black/40">
          <Search className="w-5 h-5 text-[#D4AF37]" />
          <input
            ref={inputRef}
            type="text"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            placeholder="Search by Surah name (e.g. Al-Kahf, Yaseen, 67), or Juz number..."
            className="flex-1 bg-transparent text-sm sm:text-base text-slate-100 placeholder-slate-500 focus:outline-none"
          />
          {searchTerm && (
            <button
              onClick={() => setSearchTerm("")}
              className="p-1 rounded-md text-slate-400 hover:text-white transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          )}
          <kbd className="hidden sm:inline-block px-2 py-0.5 rounded bg-white/[0.06] border border-white/10 text-[10px] font-mono text-slate-400">
            ESC
          </kbd>
        </div>

        {/* Tab Filters */}
        <div className="px-4 py-2 border-b border-white/[0.06] bg-black/20 flex items-center justify-between text-xs">
          <div className="flex space-x-2">
            {(["all", "surahs", "juzs"] as const).map((tab) => (
              <button
                key={tab}
                onClick={() => setActiveTab(tab)}
                className={`px-3 py-1 rounded-lg text-xs font-medium capitalize transition-all cursor-pointer flex items-center gap-1.5 ${
                  activeTab === tab
                    ? "bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/40 shadow-sm"
                    : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04] border border-transparent"
                }`}
              >
                {tab === "surahs" && <Sparkles className="w-3 h-3" />}
                {tab === "juzs" && <Layers className="w-3 h-3" />}
                <span>{tab === "all" ? "All Scripture" : tab}</span>
              </button>
            ))}
          </div>

          <span className="text-[11px] text-slate-500 font-mono">
            {activeTab === "juzs"
              ? `${filteredJuzs.length} Juzs`
              : activeTab === "surahs"
              ? `${filteredSurahs.length} Surahs`
              : `${filteredSurahs.length} Surahs, ${filteredJuzs.length} Juzs`}
          </span>
        </div>

        {/* Results List */}
        <div className="max-h-[60vh] overflow-y-auto p-3 space-y-1 divide-y divide-white/[0.03]">
          {/* Juz Results */}
          {(activeTab === "all" || activeTab === "juzs") && displayedJuzs.length > 0 && (
            <div className="space-y-1 pb-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-[#D4AF37]/80 px-2.5 py-1 block">
                Juz Divisions (30 Para)
              </span>
              {displayedJuzs.map((j) => (
                <button
                  key={`juz-${j.id}`}
                  onClick={() => {
                    onSelectJuz(j.id);
                    onClose();
                  }}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-gradient-to-r hover:from-[#D4AF37]/20 hover:to-[#D4AF37]/5 border border-transparent hover:border-[#D4AF37]/40 text-left transition-all duration-200 group cursor-pointer"
                >
                  <div className="flex items-center space-x-3">
                    <span className="w-7 h-7 rounded-lg bg-white/[0.06] border border-white/10 group-hover:bg-[#D4AF37] group-hover:text-black flex items-center justify-center text-xs font-bold font-serif transition-colors text-slate-300">
                      {j.id}
                    </span>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-semibold text-slate-200 group-hover:text-[#D4AF37] transition-colors">
                          {j.name}
                        </span>
                        <span className="font-arabic text-xs text-[#D4AF37]/80">
                          {j.arabic}
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-400">{j.surahs}</p>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-slate-500 group-hover:text-[#D4AF37] group-hover:translate-x-1 transition-all" />
                </button>
              ))}
            </div>
          )}

          {/* Surah Results */}
          {(activeTab === "all" || activeTab === "surahs") && displayedSurahs.length > 0 && (
            <div className="space-y-1 pt-2">
              <span className="text-[10px] font-bold uppercase tracking-wider text-emerald-400/80 px-2.5 py-1 block">
                114 Surahs (Noble Chapters)
              </span>
              {displayedSurahs.map((s) => (
                <button
                  key={`surah-${s.number}`}
                  onClick={() => {
                    if (onSelectSurah) {
                      onSelectSurah(s.number);
                    }
                    onClose();
                  }}
                  className="w-full flex items-center justify-between p-2.5 rounded-xl hover:bg-gradient-to-r hover:from-[#D4AF37]/20 hover:to-[#D4AF37]/5 border border-transparent hover:border-[#D4AF37]/45 text-left transition-all duration-200 group cursor-pointer"
                >
                  <div className="flex items-center space-x-3">
                    <span className="w-7 h-7 rounded-lg bg-emerald-950/60 border border-emerald-800/40 text-emerald-300 group-hover:bg-[#D4AF37] group-hover:text-black group-hover:border-[#D4AF37] flex items-center justify-center text-xs font-bold font-mono transition-colors">
                      {s.number}
                    </span>
                    <div>
                      <div className="flex items-center space-x-2">
                        <span className="text-xs font-semibold text-slate-200 group-hover:text-[#D4AF37] transition-colors">
                          Surah {s.englishName}
                        </span>
                        <span className="font-arabic text-xs text-[#D4AF37]/80">
                          {s.name}
                        </span>
                      </div>
                      <p className="text-[10px] text-slate-400">
                        {s.englishNameTranslation} • {s.numberOfAyahs} Ayahs
                      </p>
                    </div>
                  </div>
                  <CornerDownLeft className="w-3.5 h-3.5 text-slate-500 opacity-0 group-hover:opacity-100 group-hover:text-[#D4AF37] group-hover:translate-x-0.5 transition-all" />
                </button>
              ))}
            </div>
          )}

          {filteredSurahs.length === 0 && filteredJuzs.length === 0 && (
            <div className="py-12 text-center text-slate-500 text-xs">
              No matching Surah or Juz found for &quot;{searchTerm}&quot;.
            </div>
          )}
        </div>

        {/* Footer info */}
        <div className="p-3 border-t border-white/[0.06] bg-black/40 flex items-center justify-between text-[10px] text-slate-500">
          <span>Navigate Scripture • 114 Surahs and 30 Juz instantaneously</span>
          <span>Press ESC to exit</span>
        </div>
      </div>
    </div>
  );
}

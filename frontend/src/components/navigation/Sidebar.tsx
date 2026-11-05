"use client";

import React, { useState } from "react";
import Link from "next/link";
import { BookOpen, ChevronRight, Search, X, Sparkles, Layers } from "lucide-react";
import { JuzMeta, SurahMeta } from "@/lib/api";
import { HidayahEmblem } from "./HidayahEmblem";

interface SidebarProps {
  juzs: JuzMeta[];
  surahs?: SurahMeta[];
  currentJuz: number;
  currentSurahNumber?: number;
  onSelectJuz: (id: number) => void;
  onSelectSurah?: (surahNumber: number) => void;
  isOpen: boolean;
  onClose: () => void;
}

export function Sidebar({
  juzs,
  surahs = [],
  currentJuz,
  currentSurahNumber,
  onSelectJuz,
  onSelectSurah,
  isOpen,
  onClose,
}: SidebarProps) {
  const [searchTerm, setSearchTerm] = useState("");
  const [activeTab, setActiveTab] = useState<"juz" | "surahs">("juz");

  const term = searchTerm.toLowerCase().trim();

  const filteredJuzs = juzs.filter(
    (j) =>
      !term ||
      j.name.toLowerCase().includes(term) ||
      j.arabic.includes(term) ||
      j.english.toLowerCase().includes(term) ||
      j.surahs.toLowerCase().includes(term) ||
      `juz ${j.id}`.includes(term)
  );

  const filteredSurahs = surahs.filter(
    (s) =>
      !term ||
      s.englishName.toLowerCase().includes(term) ||
      s.englishNameTranslation.toLowerCase().includes(term) ||
      s.name.includes(term) ||
      s.number.toString() === term ||
      `surah ${s.number}`.includes(term)
  );

  return (
    <>
      {/* Mobile Backdrop */}
      {isOpen && (
        <div
          onClick={onClose}
          className="fixed inset-0 z-40 bg-black/70 backdrop-blur-md lg:hidden transition-opacity"
        />
      )}

      {/* Sidebar Container: In-flow flex child on desktop, slide-over drawer on mobile */}
      <aside
        className={`fixed lg:relative inset-y-0 left-0 z-40 lg:z-10 h-full flex flex-col flex-shrink-0 glass-sidebar transition-all duration-300 ease-in-out ${
          isOpen
            ? "translate-x-0 w-72 xl:w-80 opacity-100"
            : "-translate-x-full lg:translate-x-0 lg:w-0 lg:opacity-0 lg:overflow-hidden lg:pointer-events-none lg:border-r-0"
        }`}
      >
        {/* App Logo & Header */}
        <div className="p-4 xl:p-5 flex items-center justify-between border-b border-white/[0.08] bg-black/20">
          <div className="flex items-center space-x-3">
            <div className="relative">
              <HidayahEmblem className="w-10 h-10 shadow-lg shadow-black/60 rounded-2xl" />
              <div className="absolute -top-0.5 -right-0.5 w-2.5 h-2.5 bg-[#D4AF37] rounded-full animate-pulse border border-black" />
            </div>
            <div>
              <h1 className="text-base xl:text-lg font-serif font-bold tracking-wider text-white">
                Hidayah<span className="text-[#D4AF37]">AI</span>
              </h1>
              <p className="text-[10px] xl:text-[11px] text-slate-400 font-sans tracking-wide">
                Quranic Research Workstation
              </p>
            </div>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-[#D4AF37] rounded-lg hover:bg-white/5 cursor-pointer transition-colors"
            aria-label="Collapse Sidebar"
            title="Collapse Sidebar"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Search Bar */}
        <div className="p-3 border-b border-white/[0.06] bg-black/10">
          <div className="relative">
            <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-slate-400" />
            <input
              type="text"
              placeholder={activeTab === "juz" ? "Search 30 Juz..." : "Search 114 Surahs..."}
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-8 pr-3 py-1.5 bg-black/40 border border-white/10 rounded-lg text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#D4AF37]/60 transition-colors"
            />
          </div>
        </div>

        {/* 99 Names of Allah Dedicated Module Shortcut */}
        <div className="px-3 pt-2.5 pb-1">
          <Link
            href="/names-of-allah"
            className="w-full flex items-center justify-between px-3 py-2 rounded-xl bg-gradient-to-r from-[#D4AF37]/15 to-[#064E3B]/20 hover:from-[#D4AF37]/25 hover:to-[#064E3B]/35 border border-[#D4AF37]/40 text-xs font-semibold text-white hover:text-[#D4AF37] transition-all shadow-sm group"
          >
            <div className="flex items-center space-x-2">
              <Sparkles className="w-3.5 h-3.5 text-[#D4AF37] group-hover:scale-110 transition-transform" />
              <span>99 Names of Allah</span>
            </div>
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#D4AF37]/20 border border-[#D4AF37]/40 text-[#D4AF37] font-serif font-normal">
              أسماء الله
            </span>
          </Link>
        </div>

        {/* Navigation Tabs: 30 Juz vs 114 Surahs */}
        <div className="flex border-b border-white/[0.08] px-2.5 py-1.5 bg-black/20 gap-1.5">
          <button
            onClick={() => setActiveTab("juz")}
            className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold tracking-wide transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
              activeTab === "juz"
                ? "bg-gradient-to-r from-[#D4AF37]/25 to-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/40 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04] border border-transparent"
            }`}
          >
            <Layers className="w-3 h-3" />
            <span>30 Juz</span>
          </button>
          <button
            onClick={() => setActiveTab("surahs")}
            className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold tracking-wide transition-all cursor-pointer flex items-center justify-center gap-1.5 ${
              activeTab === "surahs"
                ? "bg-gradient-to-r from-[#D4AF37]/25 to-[#D4AF37]/10 text-[#D4AF37] border border-[#D4AF37]/40 shadow-sm"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.04] border border-transparent"
            }`}
          >
            <Sparkles className="w-3 h-3" />
            <span>114 Surahs</span>
          </button>
        </div>

        {/* List Content */}
        <div className="flex-1 overflow-y-auto overscroll-contain p-2.5 space-y-1.5">
          {activeTab === "juz" ? (
            <>
              <div className="px-2 py-1 text-[10px] font-bold tracking-widest text-[#D4AF37]/90 uppercase flex items-center justify-between">
                <span>30 Juz Index</span>
                <span className="text-slate-500 font-normal">Canonical</span>
              </div>

              {filteredJuzs.map((j) => {
                const isActive = j.id === currentJuz;
                return (
                  <button
                    key={j.id}
                    onClick={() => {
                      onSelectJuz(j.id);
                      if (window.innerWidth < 1024) onClose();
                    }}
                    className={`w-full group flex items-center justify-between p-2.5 rounded-xl text-left transition-all duration-200 cursor-pointer ${
                      isActive
                        ? "bg-gradient-to-r from-[#D4AF37]/20 to-[#D4AF37]/5 border border-[#D4AF37]/50 shadow-sm"
                        : "hover:bg-gradient-to-r hover:from-[#D4AF37]/15 hover:to-transparent border border-transparent hover:border-[#D4AF37]/40 text-slate-300 hover:text-white"
                    }`}
                  >
                    <div className="flex items-center space-x-3 truncate">
                      <div
                        className={`w-7 h-7 rounded-lg flex-shrink-0 flex items-center justify-center text-xs font-bold font-serif transition-colors ${
                          isActive
                            ? "bg-[#D4AF37] text-black shadow-md shadow-[#D4AF37]/20"
                            : "bg-white/5 text-slate-400 group-hover:bg-[#D4AF37] group-hover:text-black border border-white/5"
                        }`}
                      >
                        {j.id}
                      </div>
                      <div className="truncate">
                        <div className="flex items-center space-x-2">
                          <span
                            className={`text-xs font-medium truncate ${
                              isActive ? "text-[#D4AF37] font-semibold" : "text-slate-200 group-hover:text-[#D4AF37]"
                            }`}
                          >
                            {j.name}
                          </span>
                          <span className="font-arabic text-xs text-[#D4AF37]/80">
                            {j.arabic}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-400 truncate max-w-[170px]">
                          {j.surahs}
                        </p>
                      </div>
                    </div>

                    <ChevronRight
                      className={`w-4 h-4 flex-shrink-0 transition-all duration-200 ${
                        isActive
                          ? "text-[#D4AF37] translate-x-0.5"
                          : "text-slate-500 opacity-0 group-hover:opacity-100 group-hover:text-[#D4AF37] group-hover:translate-x-1"
                      }`}
                    />
                  </button>
                );
              })}
            </>
          ) : (
            <>
              <div className="px-2 py-1 text-[10px] font-bold tracking-widest text-emerald-400/90 uppercase flex items-center justify-between">
                <span>114 Surahs</span>
                <span className="text-slate-500 font-normal">{filteredSurahs.length} Chapters</span>
              </div>

              {filteredSurahs.map((s) => {
                const isActive = s.number === currentSurahNumber;
                return (
                  <button
                    key={s.number}
                    onClick={() => {
                      if (onSelectSurah) onSelectSurah(s.number);
                      if (window.innerWidth < 1024) onClose();
                    }}
                    className={`w-full group flex items-center justify-between p-2.5 rounded-xl text-left transition-all duration-200 cursor-pointer ${
                      isActive
                        ? "bg-gradient-to-r from-emerald-900/40 to-emerald-950/20 border border-emerald-500/50 shadow-sm"
                        : "hover:bg-gradient-to-r hover:from-[#D4AF37]/15 hover:to-transparent border border-transparent hover:border-[#D4AF37]/45 text-slate-300 hover:text-white"
                    }`}
                  >
                    <div className="flex items-center space-x-3 truncate">
                      <div
                        className={`w-7 h-7 rounded-lg flex-shrink-0 flex items-center justify-center text-xs font-bold font-mono transition-colors ${
                          isActive
                            ? "bg-emerald-500 text-black shadow-md shadow-emerald-500/20"
                            : "bg-white/5 text-slate-400 group-hover:bg-[#D4AF37] group-hover:text-black border border-white/5"
                        }`}
                      >
                        {s.number}
                      </div>
                      <div className="truncate">
                        <div className="flex items-center space-x-2">
                          <span
                            className={`text-xs font-medium truncate ${
                              isActive ? "text-emerald-400 font-semibold" : "text-slate-200 group-hover:text-[#D4AF37]"
                            }`}
                          >
                            Surah {s.englishName}
                          </span>
                          <span className="font-arabic text-xs text-[#D4AF37]/80">
                            {s.name}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-400 truncate max-w-[170px]">
                          {s.englishNameTranslation} • {s.numberOfAyahs} Ayahs
                        </p>
                      </div>
                    </div>

                    <ChevronRight
                      className={`w-4 h-4 flex-shrink-0 transition-all duration-200 ${
                        isActive
                          ? "text-emerald-400 translate-x-0.5"
                          : "text-slate-500 opacity-0 group-hover:opacity-100 group-hover:text-[#D4AF37] group-hover:translate-x-1"
                      }`}
                    />
                  </button>
                );
              })}
            </>
          )}
        </div>

        {/* Footer / Status */}
        <div className="p-3 border-t border-white/[0.08] bg-black/30 flex items-center justify-between">
          <p className="text-[11px] text-slate-400 flex items-center gap-1.5 truncate">
            <BookOpen className="w-3.5 h-3.5 text-[#D4AF37] flex-shrink-0" />
            <span>Reading Juz {currentJuz} of 30</span>
          </p>
          <span className="text-[10px] font-mono text-[#D4AF37]/80 px-1.5 py-0.5 rounded bg-[#D4AF37]/10">
            Juz {currentJuz}
          </span>
        </div>
      </aside>
    </>
  );
}

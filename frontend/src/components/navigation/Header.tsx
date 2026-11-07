"use client";

import React, { useEffect, useState, useRef } from "react";
import Link from "next/link";
import {
  Menu,
  Sparkles,
  Search,
  Languages,
  ChevronDown,
  Check,
  Headphones,
} from "lucide-react";
import { HidayahEmblem } from "./HidayahEmblem";

interface HeaderProps {
  onToggleSidebar: () => void;
  onToggleScholar: () => void;
  onOpenSearch?: () => void;
  isScholarOpen: boolean;
  isSidebarOpen?: boolean;
  juzName: string;
  juzId: number;
  surahSummary: string;
  audioMode: string;
  onChangeAudioMode: (mode: string) => void;
  isLoadingJuz?: boolean;
}

export const RECITATION_AND_VIEW_MODES = [
  {
    id: "Arabic (Mishary Rashid)",
    label: "Arabic (Alafasy)",
    reciter: "Mishary Rashid Alafasy",
    details: "Fluid Melodic Audio • Trilingual Display",
  },
  {
    id: "Arabic (Mahmoud Al-Husary)",
    label: "Arabic (Al-Husary)",
    reciter: "Mahmoud Khalil Al-Husary",
    details: "Tajweed Learning Standard • Trilingual Display",
  },
  {
    id: "Arabic (Abdul Basit)",
    label: "Arabic (Abdul Basit)",
    reciter: "Abdul Basit Abdul Samad",
    details: "Classical Resonant Murattal • Trilingual Display",
  },
  {
    id: "Arabic (Al-Minshawi)",
    label: "Arabic (Al-Minshawi)",
    reciter: "Muhammad Siddiq Al-Minshawi",
    details: "Deeply Emotive Murattal • Trilingual Display",
  },
  {
    id: "Arabic + Urdu Translation",
    label: "Arabic + Urdu Recitation",
    reciter: "Mishary Alafasy & Shamshad Khan",
    details: "Arabic Audio then Urdu • Arabic & Urdu Translation Display",
  },
  {
    id: "Arabic + English Translation",
    label: "Arabic + English Recitation",
    reciter: "Mishary Alafasy & Ibrahim Walk",
    details: "Arabic Audio then English • Arabic & English Translation Display",
  },
  {
    id: "Urdu Translation Only",
    label: "Urdu Translation Only",
    reciter: "Shamshad Ali Khan",
    details: "Urdu Audio • Exclusive Urdu Translation Display",
  },
  {
    id: "English Translation Only",
    label: "English Translation Only",
    reciter: "Ibrahim Walk",
    details: "English Audio • Exclusive English Translation Display",
  },
];

export function Header({
  onToggleSidebar,
  onToggleScholar,
  onOpenSearch,
  isScholarOpen,
  isSidebarOpen = false,
  juzName,
  juzId,
  surahSummary,
  audioMode,
  onChangeAudioMode,
  isLoadingJuz = false,
}: HeaderProps) {
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement | null>(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  // Listen for Ctrl+K / Cmd+K to open search modal
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === "k") {
        e.preventDefault();
        onOpenSearch?.();
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onOpenSearch]);

  const activeModeObj =
    RECITATION_AND_VIEW_MODES.find((m) => m.id === audioMode) ||
    RECITATION_AND_VIEW_MODES[0];

  return (
    <header className="sticky top-0 z-30 h-16 glass-header px-4 lg:px-6 flex items-center justify-between relative">
      {/* Top Gold Shimmer Progress Bar when Loading Scripture */}
      {isLoadingJuz && (
        <div className="absolute top-0 left-0 right-0 h-[2.5px] bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent animate-pulse" />
      )}

      {/* Left: Mobile Toggle & Juz Info */}
      <div className="flex items-center space-x-3">
        <button
          onClick={onToggleSidebar}
          className={`p-2 text-slate-300 hover:text-white rounded-lg hover:bg-white/5 transition-colors cursor-pointer ${
            isSidebarOpen ? "lg:hidden" : "flex items-center"
          }`}
          aria-label={isSidebarOpen ? "Close Sidebar" : "Open 30 Juz & Surahs Sidebar"}
          title={isSidebarOpen ? "Close Sidebar" : "Open 30 Juz & Surahs Sidebar"}
        >
          <Menu className="w-5 h-5 text-[#D4AF37]" />
        </button>

        <div className={`${isSidebarOpen ? "lg:hidden" : "flex"} flex-shrink-0`}>
          <HidayahEmblem className="w-7 h-7" />
        </div>

        <div className="flex flex-col">
          <div className="flex items-center space-x-2">
            <span className="px-2 py-0.5 rounded bg-gradient-to-r from-[#D4AF37]/25 to-[#D4AF37]/10 border border-[#D4AF37]/40 text-[10px] font-bold text-[#D4AF37] tracking-wider uppercase flex items-center gap-1.5">
              {isLoadingJuz ? (
                <>
                  <span className="w-1.5 h-1.5 rounded-full bg-[#D4AF37] animate-ping" />
                  <span>Loading...</span>
                </>
              ) : (
                <span>Juz {juzId}</span>
              )}
            </span>
            <h2 className="text-sm sm:text-base font-serif font-bold text-white tracking-wide truncate max-w-[170px] sm:max-w-xs md:max-w-md">
              {juzName}
            </h2>
          </div>
          <span className="text-[11px] text-slate-400 font-sans truncate max-w-[190px] sm:max-w-sm">
            {surahSummary || "Quranic Exegesis & Audio Sync"}
          </span>
        </div>
      </div>

      {/* Right: Navigate Scripture + 99 Names + Custom Sacred Mode Dropdown + Scholar AI */}
      <div className="flex items-center space-x-2 sm:space-x-3">
        {/* Dedicated 99 Names of Allah Entry */}
        <Link
          href="/names-of-allah"
          className="flex items-center space-x-1.5 px-2.5 sm:px-3 py-1.5 rounded-xl bg-black/40 hover:bg-[#D4AF37]/15 border border-white/10 hover:border-[#D4AF37]/50 text-slate-300 hover:text-[#D4AF37] text-xs transition-all duration-200 cursor-pointer shadow-sm group flex-shrink-0"
          title="Explore the 99 Names of Allah (Asma-ul-Husna)"
        >
          <Sparkles className="w-3.5 h-3.5 text-[#D4AF37] group-hover:scale-110 transition-transform" />
          <span className="hidden xl:inline font-medium">99 Names</span>
        </Link>

        {/* Scripture Navigator Button */}
        {onOpenSearch && (
          <button
            onClick={onOpenSearch}
            className="flex items-center space-x-1.5 sm:space-x-2 px-2.5 sm:px-3.5 py-1.5 rounded-xl bg-black/40 hover:bg-[#D4AF37]/15 border border-white/10 hover:border-[#D4AF37]/50 text-slate-300 hover:text-[#D4AF37] text-xs transition-all duration-200 cursor-pointer shadow-sm group flex-shrink-0"
            title="Navigate Scripture (Ctrl+K / ⌘K) — Explore Surahs & Juz"
          >
            <Search className="w-3.5 h-3.5 text-[#D4AF37] group-hover:scale-110 transition-transform" />
            <span className="hidden 2xl:inline font-medium">Navigate Scripture</span>
            <kbd className="hidden md:inline-block px-1.5 py-0.2 rounded bg-white/[0.06] border border-white/10 text-[9px] font-mono text-slate-400">
              ⌘K
            </kbd>
          </button>
        )}

        {/* Custom Frosted Glass Reciter & Translation View Dropdown */}
        <div ref={dropdownRef} className="relative flex-shrink-0">
          <button
            onClick={() => setIsDropdownOpen(!isDropdownOpen)}
            className={`flex items-center space-x-1.5 sm:space-x-2 px-2.5 sm:px-3 py-1.5 rounded-xl text-xs transition-all duration-200 cursor-pointer border ${
              isDropdownOpen
                ? "bg-[#D4AF37]/15 border-[#D4AF37]/60 text-white shadow-md shadow-[#D4AF37]/10"
                : "bg-black/50 border-white/10 hover:border-[#D4AF37]/40 text-slate-200 hover:text-white"
            }`}
            title="Select Recitation Voice & Translation Display Mode"
          >
            <Languages className="w-3.5 h-3.5 text-[#D4AF37]" />
            <span className="font-medium max-w-[100px] sm:max-w-[140px] truncate">
              {activeModeObj.label}
            </span>
            <ChevronDown
              className={`w-3.5 h-3.5 text-slate-400 transition-transform duration-200 ${
                isDropdownOpen ? "rotate-180 text-[#D4AF37]" : ""
              }`}
            />
          </button>

          {/* Frosted Dropdown Menu */}
          {isDropdownOpen && (
            <div className="absolute right-0 top-full mt-2 w-72 sm:w-80 rounded-2xl glass-panel border border-[#D4AF37]/40 bg-[#0B0F17]/95 backdrop-blur-2xl shadow-2xl p-2 z-50 animate-in fade-in zoom-in-95 duration-150">
              <div className="px-3 py-1.5 border-b border-white/[0.08] mb-1 flex items-center justify-between">
                <span className="text-[10px] font-bold tracking-widest text-[#D4AF37] uppercase flex items-center gap-1.5">
                  <Headphones className="w-3 h-3" />
                  Recitation & View Mode
                </span>
                <span className="text-[9px] text-slate-400 font-mono">Sync Mode</span>
              </div>

              <div className="space-y-1">
                {RECITATION_AND_VIEW_MODES.map((mode) => {
                  const isSelected = mode.id === audioMode;
                  return (
                    <button
                      key={mode.id}
                      onClick={() => {
                        onChangeAudioMode(mode.id);
                        setIsDropdownOpen(false);
                      }}
                      className={`w-full text-left p-2.5 rounded-xl transition-all duration-200 flex items-start justify-between group cursor-pointer ${
                        isSelected
                          ? "bg-gradient-to-r from-[#D4AF37]/25 to-[#D4AF37]/10 border border-[#D4AF37]/50 text-white"
                          : "hover:bg-white/[0.06] text-slate-300 hover:text-white border border-transparent"
                      }`}
                    >
                      <div className="pr-2">
                        <div className="flex items-center space-x-1.5">
                          <span
                            className={`text-xs font-semibold ${
                              isSelected ? "text-[#D4AF37]" : "group-hover:text-[#D4AF37]"
                            }`}
                          >
                            {mode.label}
                          </span>
                        </div>
                        <p className="text-[10px] text-slate-400 font-sans mt-0.5 leading-tight">
                          {mode.details}
                        </p>
                      </div>

                      {isSelected && (
                        <Check className="w-4 h-4 text-[#D4AF37] flex-shrink-0 mt-0.5" />
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          )}
        </div>

        {/* Scholar AI Toggle Button */}
        <button
          onClick={onToggleScholar}
          className={`relative flex items-center space-x-1.5 px-3 py-1.5 rounded-xl text-xs font-semibold tracking-wide transition-all duration-200 shadow-sm cursor-pointer flex-shrink-0 ${
            isScholarOpen
              ? "bg-[#D4AF37]/20 border border-[#D4AF37] text-[#D4AF37] shadow-sm shadow-[#D4AF37]/10"
              : "bg-white/[0.04] hover:bg-white/[0.08] border border-[#D4AF37]/40 text-slate-200 hover:text-white hover:scale-105 active:scale-95"
          }`}
          title={isScholarOpen ? "Close Scholar AI Copilot" : "Open Scholar AI Copilot"}
        >
          <Sparkles
            className={`w-3.5 h-3.5 ${
              isScholarOpen ? "text-[#D4AF37]" : "text-[#D4AF37]"
            }`}
          />
          <span className="hidden sm:inline">Scholar AI</span>
          <span className="flex h-2 w-2 relative">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-[#10B981] opacity-75" />
            <span className="relative inline-flex rounded-full h-2 w-2 bg-[#10B981]" />
          </span>
        </button>
      </div>
    </header>
  );
}

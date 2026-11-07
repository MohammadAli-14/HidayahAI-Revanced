"use client";

import React from "react";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Repeat,
  X,
  Volume2,
  Sparkles,
} from "lucide-react";
import { NameOfAllah } from "@/lib/api";

interface NamesContinuousPlayerBarProps {
  currentName: NameOfAllah | null;
  currentIndex: number;
  totalNames: number;
  isPlaying: boolean;
  playbackSpeed: number;
  isLooping: boolean;
  onPlayPause: () => void;
  onNext: () => void;
  onPrev: () => void;
  onToggleSpeed: () => void;
  onToggleLoop: () => void;
  onClose: () => void;
  onSelectName: (name: NameOfAllah) => void;
}

export function NamesContinuousPlayerBar({
  currentName,
  currentIndex,
  totalNames,
  isPlaying,
  playbackSpeed,
  isLooping,
  onPlayPause,
  onNext,
  onPrev,
  onToggleSpeed,
  onToggleLoop,
  onClose,
  onSelectName,
}: NamesContinuousPlayerBarProps) {
  if (!currentName) return null;

  const progressPercent = Math.min(100, Math.round(((currentIndex + 1) / totalNames) * 100));

  return (
    <div className="fixed bottom-4 left-4 right-4 sm:left-6 sm:right-6 max-w-4xl mx-auto z-40 animate-in slide-in-from-bottom-4 duration-300">
      <div className="relative rounded-2xl bg-[#0B0F17]/95 border border-[#D4AF37]/50 shadow-2xl shadow-black/80 backdrop-blur-2xl p-3 sm:p-4 overflow-hidden">
        {/* Top Progress Line Indicator */}
        <div className="absolute top-0 left-0 right-0 h-[2.5px] bg-white/[0.08]">
          <div
            className="h-full bg-gradient-to-r from-[#AA8220] via-[#D4AF37] to-[#F3E5AB] transition-all duration-300"
            style={{ width: `${progressPercent}%` }}
          />
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-1">
          {/* Left: Current Divine Name Info */}
          <div
            onClick={() => onSelectName(currentName)}
            className="flex items-center space-x-3 w-full sm:w-auto cursor-pointer group"
            title="Click to view full theological meaning and scripture"
          >
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-[#064E3B] to-[#0A261E] border border-[#D4AF37]/50 flex items-center justify-center font-mono text-xs font-bold text-[#D4AF37] shadow-inner flex-shrink-0 group-hover:scale-105 transition-transform">
              {currentName.number}
            </div>

            <div className="truncate text-left">
              <div className="flex items-center space-x-2">
                <span className="font-serif text-lg font-bold text-white group-hover:text-[#D4AF37] transition-colors leading-none">
                  {currentName.name_ar}
                </span>
                <span className="text-xs font-semibold text-[#D4AF37] uppercase tracking-wider">
                  {currentName.transliteration}
                </span>
              </div>
              <p className="text-[11px] text-slate-300 truncate max-w-[200px] sm:max-w-xs font-sans">
                {currentName.meaning_en}
              </p>
            </div>
          </div>

          {/* Center: Recitation Controls */}
          <div className="flex items-center space-x-3">
            <button
              onClick={onPrev}
              disabled={currentIndex === 0 && !isLooping}
              className="p-1.5 text-slate-400 hover:text-[#D4AF37] disabled:opacity-25 transition-all cursor-pointer disabled:cursor-not-allowed hover:scale-110 active:scale-95"
              title="Previous Divine Name"
              aria-label="Previous Divine Name"
            >
              <SkipBack className="w-4 h-4" />
            </button>

            <button
              onClick={onPlayPause}
              className="w-10 h-10 rounded-full bg-[#D4AF37] hover:bg-[#F3E5AB] text-black flex items-center justify-center shadow-lg shadow-[#D4AF37]/25 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
              title={isPlaying ? "Pause Continuous Recitation" : "Resume Continuous Recitation"}
              aria-label={isPlaying ? "Pause" : "Play"}
            >
              {isPlaying ? (
                <Pause className="w-4 h-4 fill-black" />
              ) : (
                <Play className="w-4 h-4 fill-black translate-x-0.5" />
              )}
            </button>

            <button
              onClick={onNext}
              disabled={currentIndex >= totalNames - 1 && !isLooping}
              className="p-1.5 text-slate-400 hover:text-[#D4AF37] disabled:opacity-25 transition-all cursor-pointer disabled:cursor-not-allowed hover:scale-110 active:scale-95"
              title="Next Divine Name"
              aria-label="Next Divine Name"
            >
              <SkipForward className="w-4 h-4" />
            </button>
          </div>

          {/* Right: Loop Mode, Speed, Progress & Close */}
          <div className="flex items-center space-x-2.5 w-full sm:w-auto justify-end">
            {/* Loop Toggle */}
            <button
              onClick={onToggleLoop}
              className={`p-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition-all cursor-pointer border ${
                isLooping
                  ? "bg-[#D4AF37]/25 text-[#D4AF37] border-[#D4AF37]/50 shadow-sm"
                  : "text-slate-400 hover:text-white border-transparent hover:bg-white/5"
              }`}
              title={isLooping ? "Continuous Loop: ON (Loops 99 to 1)" : "Continuous Loop: OFF"}
            >
              <Repeat className="w-3.5 h-3.5" />
            </button>

            {/* Speed Stepper */}
            <button
              onClick={onToggleSpeed}
              className="px-2 py-1 rounded-lg bg-white/5 hover:bg-[#D4AF37]/15 border border-white/10 hover:border-[#D4AF37]/40 text-[11px] font-mono font-bold text-[#D4AF37] transition-all cursor-pointer hover:scale-105 active:scale-95"
              title="Cycle Recitation Speed (1.0x, 1.25x, 1.5x)"
            >
              {playbackSpeed}x
            </button>

            {/* Progress Counter Pill */}
            <span className="text-[11px] font-mono font-medium text-slate-300 bg-black/50 px-2 py-1 rounded-lg border border-white/10">
              <strong className="text-[#D4AF37]">{currentIndex + 1}</strong> / {totalNames}
            </span>

            {/* Close / Dismiss Bar */}
            <button
              onClick={onClose}
              className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-colors cursor-pointer"
              title="Stop Recitation and Close Player"
            >
              <X className="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

"use client";

import React, { useRef } from "react";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Repeat,
  X,
  Volume2,
  Headphones,
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
  currentTime: number;
  duration: number;
  reciterTitle?: string;
  onPlayPause: () => void;
  onNext: () => void;
  onPrev: () => void;
  onToggleSpeed: () => void;
  onToggleLoop: () => void;
  onSeek?: (targetSeconds: number) => void;
  onClose: () => void;
  onSelectName: (name: NameOfAllah) => void;
}

function formatTime(seconds: number): string {
  if (isNaN(seconds) || seconds < 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

export function NamesContinuousPlayerBar({
  currentName,
  currentIndex,
  totalNames,
  isPlaying,
  playbackSpeed,
  isLooping,
  currentTime,
  duration,
  reciterTitle = "Sheikh Mishary Rashid Alafasy",
  onPlayPause,
  onNext,
  onPrev,
  onToggleSpeed,
  onToggleLoop,
  onSeek,
  onClose,
  onSelectName,
}: NamesContinuousPlayerBarProps) {
  const progressBarRef = useRef<HTMLDivElement | null>(null);

  if (!currentName) return null;

  const progressPercent = duration > 0 ? Math.min(100, (currentTime / duration) * 100) : 0;

  const handleProgressBarClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressBarRef.current || duration <= 0 || !onSeek) return;
    const rect = progressBarRef.current.getBoundingClientRect();
    const clickPos = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const seekPercentage = clickPos / rect.width;
    onSeek(seekPercentage * duration);
  };

  return (
    <div className="fixed bottom-4 left-3 right-3 sm:left-6 sm:right-6 max-w-4xl mx-auto z-40 animate-in slide-in-from-bottom-4 duration-300">
      <div className="relative rounded-2xl bg-[#0B0F17]/95 border border-[#D4AF37]/50 shadow-2xl shadow-black/90 backdrop-blur-2xl p-3 sm:p-4 overflow-hidden">
        {/* Interactive Seekable Progress Bar */}
        <div
          ref={progressBarRef}
          onClick={handleProgressBarClick}
          className="absolute top-0 left-0 right-0 h-2 bg-white/[0.08] hover:h-2.5 cursor-pointer transition-all duration-150 group"
          title="Click to seek recitation timeline"
        >
          <div
            className="h-full bg-gradient-to-r from-[#AA8220] via-[#D4AF37] to-[#F3E5AB] relative transition-all duration-100"
            style={{ width: `${progressPercent}%` }}
          >
            <span className="absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-[#F3E5AB] shadow-md shadow-[#D4AF37] border border-white opacity-0 group-hover:opacity-100 transition-opacity" />
          </div>
        </div>

        <div className="flex flex-col sm:flex-row items-center justify-between gap-3 pt-1">
          {/* Left: Active Divine Name Info & Reciter Badge */}
          <div
            onClick={() => onSelectName(currentName)}
            className="flex items-center space-x-3 w-full sm:w-auto cursor-pointer group"
            title="Click to inspect theological exegesis and scripture references"
          >
            <div className="relative">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[#064E3B] to-[#0A261E] border border-[#D4AF37]/50 flex items-center justify-center font-mono text-xs font-bold text-[#D4AF37] shadow-inner flex-shrink-0 group-hover:scale-105 transition-transform">
                {currentName.number}
              </div>
              {isPlaying && (
                <div className="absolute -bottom-1 -right-1 w-3 h-3 rounded-full bg-[#D4AF37] border-2 border-black animate-ping" />
              )}
            </div>

            <div className="truncate text-left">
              <div className="flex items-center space-x-2">
                <span className="font-serif text-xl font-bold text-white group-hover:text-[#D4AF37] transition-colors leading-none">
                  {currentName.name_ar}
                </span>
                <span className="text-xs font-semibold text-[#D4AF37] uppercase tracking-wider">
                  {currentName.transliteration}
                </span>
              </div>
              <div className="flex items-center space-x-1.5 mt-0.5">
                <p className="text-[11px] text-slate-300 truncate max-w-[170px] sm:max-w-xs font-sans">
                  {currentName.meaning_en}
                </p>
                <span className="text-[9px] px-2 py-0.2 rounded-full bg-[#D4AF37]/15 border border-[#D4AF37]/40 text-[#D4AF37] font-medium hidden md:inline-flex items-center gap-1">
                  <Headphones className="w-2.5 h-2.5" />
                  <span>{reciterTitle}</span>
                </span>
              </div>
            </div>
          </div>

          {/* Center: Recitation Controls */}
          <div className="flex items-center space-x-3.5">
            <button
              onClick={onPrev}
              disabled={currentIndex === 0 && !isLooping}
              className="p-1.5 text-slate-400 hover:text-[#D4AF37] disabled:opacity-20 transition-all cursor-pointer disabled:cursor-not-allowed hover:scale-110 active:scale-95"
              title="Previous Divine Name"
              aria-label="Previous Divine Name"
            >
              <SkipBack className="w-4 h-4" />
            </button>

            <button
              onClick={onPlayPause}
              className="w-11 h-11 rounded-full bg-gradient-to-r from-[#D4AF37] to-[#F3E5AB] hover:from-[#E5C158] hover:to-[#FFF0B8] text-black flex items-center justify-center shadow-lg shadow-[#D4AF37]/30 transition-all duration-200 hover:scale-105 active:scale-95 cursor-pointer"
              title={isPlaying ? "Pause Recitation" : "Play Recitation"}
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
              className="p-1.5 text-slate-400 hover:text-[#D4AF37] disabled:opacity-20 transition-all cursor-pointer disabled:cursor-not-allowed hover:scale-110 active:scale-95"
              title="Next Divine Name"
              aria-label="Next Divine Name"
            >
              <SkipForward className="w-4 h-4" />
            </button>
          </div>

          {/* Right: Loop Mode, Speed, Timestamp & Dismiss */}
          <div className="flex items-center space-x-2.5 w-full sm:w-auto justify-end">
            {/* Timestamp Display */}
            <span className="text-[10px] font-mono text-slate-400 hidden sm:inline-block">
              {formatTime(currentTime)} / {formatTime(duration)}
            </span>

            {/* Loop Toggle */}
            <button
              onClick={onToggleLoop}
              className={`p-1.5 rounded-lg text-xs font-semibold flex items-center space-x-1 transition-all cursor-pointer border ${
                isLooping
                  ? "bg-[#D4AF37]/25 text-[#D4AF37] border-[#D4AF37]/50 shadow-sm"
                  : "text-slate-400 hover:text-white border-transparent hover:bg-white/5"
              }`}
              title={isLooping ? "Continuous Loop: ON" : "Continuous Loop: OFF"}
            >
              <Repeat className="w-3.5 h-3.5" />
            </button>

            {/* Speed Stepper */}
            <button
              onClick={onToggleSpeed}
              className="px-2 py-1 rounded-lg bg-white/5 hover:bg-[#D4AF37]/15 border border-white/10 hover:border-[#D4AF37]/40 text-[11px] font-mono font-bold text-[#D4AF37] transition-all cursor-pointer hover:scale-105 active:scale-95"
              title="Recitation Speed (1.0x, 1.25x, 1.5x)"
            >
              {playbackSpeed}x
            </button>

            {/* Progress Counter Pill */}
            <span className="text-[11px] font-mono font-medium text-slate-300 bg-black/60 px-2 py-1 rounded-lg border border-white/10">
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

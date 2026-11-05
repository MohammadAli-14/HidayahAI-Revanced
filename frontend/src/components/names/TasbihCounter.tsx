"use client";

import React, { useState, useEffect, useCallback } from "react";
import { RotateCcw, Volume2, VolumeX, Sparkles, Award } from "lucide-react";

interface TasbihCounterProps {
  nameId: number;
  nameArabic: string;
  transliteration: string;
  defaultTarget?: number;
}

export function TasbihCounter({
  nameId,
  nameArabic,
  transliteration,
  defaultTarget = 33,
}: TasbihCounterProps) {
  const storageKey = `hidayah_tasbih_${nameId}`;
  const lifetimeStorageKey = `hidayah_tasbih_lifetime_${nameId}`;

  const [count, setCount] = useState<number>(0);
  const [target, setTarget] = useState<number>(defaultTarget);
  const [lifetimeCount, setLifetimeCount] = useState<number>(0);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);
  const [isCompleted, setIsCompleted] = useState<boolean>(false);

  // Load persisted count from LocalStorage on mount
  useEffect(() => {
    try {
      const savedCount = localStorage.getItem(storageKey);
      const savedLifetime = localStorage.getItem(lifetimeStorageKey);
      if (savedCount !== null) setCount(parseInt(savedCount, 10) || 0);
      if (savedLifetime !== null) setLifetimeCount(parseInt(savedLifetime, 10) || 0);
    } catch (e) {
      console.warn("LocalStorage access error:", e);
    }
  }, [storageKey, lifetimeStorageKey]);

  // Audio click feedback via Web Audio API synth (zero external asset dependency)
  const playClickSound = useCallback(() => {
    if (!soundEnabled) return;
    try {
      const ctx = new (window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext)();
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = "sine";
      osc.frequency.setValueAtTime(587.33, ctx.currentTime); // D5 note (gentle resonant chime)
      gain.gain.setValueAtTime(0.08, ctx.currentTime);
      gain.gain.exponentialRampToValueAtTime(0.001, ctx.currentTime + 0.08);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start();
      osc.stop(ctx.currentTime + 0.08);
    } catch {
      // AudioContext unavailable
    }
  }, [soundEnabled]);

  const handleIncrement = () => {
    const nextCount = count + 1;
    const nextLifetime = lifetimeCount + 1;
    setCount(nextCount);
    setLifetimeCount(nextLifetime);

    // Persist to LocalStorage
    try {
      localStorage.setItem(storageKey, nextCount.toString());
      localStorage.setItem(lifetimeStorageKey, nextLifetime.toString());
    } catch {
      // Storage quota or disabled
    }

    // Haptic vibration feedback on mobile
    if (typeof window !== "undefined" && "vibrate" in navigator) {
      navigator.vibrate(15);
    }

    playClickSound();

    if (nextCount === target) {
      setIsCompleted(true);
      if (typeof window !== "undefined" && "vibrate" in navigator) {
        navigator.vibrate([40, 60, 40]);
      }
    }
  };

  const handleReset = (e: React.MouseEvent) => {
    e.stopPropagation();
    setCount(0);
    setIsCompleted(false);
    try {
      localStorage.setItem(storageKey, "0");
    } catch {
      // Ignore
    }
  };

  const progressPercent = Math.min(100, Math.round((count / target) * 100));

  return (
    <div className="rounded-2xl bg-black/40 border border-[#D4AF37]/30 p-5 flex flex-col items-center select-none shadow-xl relative overflow-hidden">
      {/* Decorative background radial halo */}
      <div className="absolute inset-0 bg-[radial-gradient(circle_at_center,rgba(212,175,55,0.06)_0%,transparent_70%)] pointer-events-none" />

      {/* Target Selector & Audio Toggle */}
      <div className="w-full flex items-center justify-between mb-4 z-10">
        <div className="flex items-center space-x-1.5 bg-black/50 p-1 rounded-xl border border-white/10">
          {[33, 99, 100].map((t) => (
            <button
              key={t}
              onClick={(e) => {
                e.stopPropagation();
                setTarget(t);
                if (count >= t) setIsCompleted(true);
                else setIsCompleted(false);
              }}
              className={`px-2.5 py-1 rounded-lg text-xs font-mono font-medium transition-all ${
                target === t
                  ? "bg-[#D4AF37] text-black font-bold shadow-sm"
                  : "text-slate-400 hover:text-white"
              }`}
            >
              {t}
            </button>
          ))}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              setSoundEnabled(!soundEnabled);
            }}
            className="p-1.5 text-slate-400 hover:text-[#D4AF37] rounded-lg hover:bg-white/5 transition-colors"
            title={soundEnabled ? "Mute Click Sound" : "Enable Click Sound"}
          >
            {soundEnabled ? <Volume2 className="w-4 h-4" /> : <VolumeX className="w-4 h-4" />}
          </button>

          <button
            onClick={handleReset}
            className="p-1.5 text-slate-400 hover:text-rose-400 rounded-lg hover:bg-white/5 transition-colors"
            title="Reset Counter"
          >
            <RotateCcw className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Main Circular Tap Area */}
      <button
        onClick={handleIncrement}
        className="group relative w-48 h-48 rounded-full border-4 border-[#D4AF37]/30 hover:border-[#D4AF37] bg-gradient-to-b from-[#0F172A] to-[#064E3B]/20 flex flex-col items-center justify-center p-4 cursor-pointer active:scale-95 transition-all duration-150 shadow-2xl focus:outline-none"
      >
        {/* Dynamic Circular Progress Indicator */}
        <svg className="absolute inset-0 w-full h-full -rotate-90 pointer-events-none" viewBox="0 0 100 100">
          <circle
            cx="50"
            cy="50"
            r="46"
            className="stroke-[#D4AF37]/10"
            strokeWidth="3"
            fill="none"
          />
          <circle
            cx="50"
            cy="50"
            r="46"
            className="stroke-[#D4AF37] transition-all duration-200"
            strokeWidth="3.5"
            strokeDasharray="289.026"
            strokeDashoffset={289.026 - (289.026 * progressPercent) / 100}
            strokeLinecap="round"
            fill="none"
          />
        </svg>

        <span className="font-serif text-2xl font-bold text-white group-hover:text-[#D4AF37] transition-colors leading-none mb-1">
          {nameArabic}
        </span>
        <span className="text-[11px] text-[#D4AF37] tracking-wider uppercase font-medium mb-2">
          {transliteration}
        </span>

        {/* Counter Number Display */}
        <div className="text-4xl font-mono font-extrabold text-white tracking-tight drop-shadow-md">
          {count}
          <span className="text-xs text-slate-400 font-normal ml-1">/ {target}</span>
        </div>

        <span className="text-[10px] text-slate-400 mt-1 uppercase tracking-widest group-hover:text-slate-300">
          Tap to Recite
        </span>
      </button>

      {/* Completion Banner */}
      {isCompleted && (
        <div className="mt-3 px-3 py-1 rounded-full bg-[#064E3B]/80 border border-[#D4AF37]/50 text-xs text-[#D4AF37] font-medium flex items-center space-x-1.5 animate-in fade-in zoom-in-95">
          <Award className="w-3.5 h-3.5 text-[#D4AF37]" />
          <span>Goal Reached! Masha&apos;Allah</span>
        </div>
      )}

      {/* Lifetime Stats Footer */}
      <div className="mt-4 flex items-center space-x-2 text-[11px] text-slate-400 font-sans z-10">
        <Sparkles className="w-3.5 h-3.5 text-[#D4AF37]" />
        <span>Lifetime Devotion: <strong className="text-slate-200 font-mono">{lifetimeCount}</strong> recitations</span>
      </div>
    </div>
  );
}

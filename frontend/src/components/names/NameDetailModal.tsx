"use client";

import React, { useState, useEffect, useRef } from "react";
import {
  X,
  Volume2,
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Sparkles,
  ScrollText,
  ExternalLink,
  Layers,
} from "lucide-react";
import { NameOfAllah, fetchNameById, fetchNameScripture } from "@/lib/api";
import { TasbihCounter } from "./TasbihCounter";

interface NameDetailModalProps {
  initialName: NameOfAllah | null;
  onClose: () => void;
  onShowToast?: (msg: string) => void;
}

export function NameDetailModal({
  initialName,
  onClose,
  onShowToast,
}: NameDetailModalProps) {
  const [currentName, setCurrentName] = useState<NameOfAllah | null>(initialName);
  const [activeTab, setActiveTab] = useState<"contemplation" | "scripture" | "tasbih">("contemplation");
  const [scriptureData, setScriptureData] = useState<{ quran_verses: any[]; hadith_citations: any[] } | null>(null);
  const [isLoadingScripture, setIsLoadingScripture] = useState<boolean>(false);
  const [isPlayingAudio, setIsPlayingAudio] = useState<boolean>(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Sync state if initialName changes
  useEffect(() => {
    setCurrentName(initialName);
    setActiveTab("contemplation");
  }, [initialName]);

  // Load scripture cross-references when name changes
  useEffect(() => {
    if (!currentName) return;
    async function loadScripture() {
      setIsLoadingScripture(true);
      try {
        const data = await fetchNameScripture(currentName!.id);
        if (data) {
          setScriptureData({
            quran_verses: data.quran_verses || currentName!.quran_references || [],
            hadith_citations: data.hadith_citations || [],
          });
        }
      } finally {
        setIsLoadingScripture(false);
      }
    }
    loadScripture();
  }, [currentName]);

  // Handle Audio Pronunciation
  const playAudio = () => {
    if (!currentName) return;
    if (isPlayingAudio && audioRef.current) {
      audioRef.current.pause();
      setIsPlayingAudio(false);
      return;
    }

    if (!audioRef.current) {
      const audio = new Audio(currentName.audio_url);
      audio.onended = () => setIsPlayingAudio(false);
      audio.onerror = () => {
        if (currentName.audio_fallback_url && audio.src !== currentName.audio_fallback_url) {
          audio.src = currentName.audio_fallback_url;
          audio.play().catch(() => {
            setIsPlayingAudio(false);
            onShowToast?.(`Audio unavailable for ${currentName.transliteration}`);
          });
        } else {
          setIsPlayingAudio(false);
          onShowToast?.(`Audio unavailable for ${currentName.transliteration}`);
        }
      };
      audioRef.current = audio;
    } else {
      audioRef.current.src = currentName.audio_url;
    }

    setIsPlayingAudio(true);
    if (audioRef.current) {
      audioRef.current.currentTime = 0;
      audioRef.current.play().catch(() => {
        setIsPlayingAudio(false);
        onShowToast?.("Audio playback failed.");
      });
    }
  };

  // Navigate to Adjacent Name
  const navigateName = async (targetId: number) => {
    if (audioRef.current) {
      audioRef.current.pause();
      setIsPlayingAudio(false);
    }
    const res = await fetchNameById(targetId);
    if (res?.name) {
      setCurrentName(res.name);
    }
  };

  if (!currentName) return null;

  const prevId = currentName.number === 1 ? 99 : currentName.number - 1;
  const nextId = currentName.number === 99 ? 1 : currentName.number + 1;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4 bg-black/80 backdrop-blur-md animate-in fade-in duration-200">
      <div className="relative w-full max-w-2xl max-h-[90vh] flex flex-col rounded-3xl bg-[#0B0F17] border border-[#D4AF37]/40 shadow-2xl overflow-hidden">
        {/* Top Gold Accent Bar */}
        <div className="h-[3px] bg-gradient-to-r from-transparent via-[#D4AF37] to-transparent w-full" />

        {/* Header Bar */}
        <div className="p-4 sm:p-5 flex items-center justify-between border-b border-white/[0.08] bg-black/40">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 rounded-xl bg-[#D4AF37]/15 border border-[#D4AF37]/50 flex items-center justify-center font-mono text-xs font-bold text-[#D4AF37]">
              {currentName.number}
            </div>
            <div>
              <span className="text-[10px] uppercase tracking-wider text-slate-400">
                Divine Name {currentName.number} of 99
              </span>
              <h2 className="text-sm font-semibold text-white tracking-wide">
                {currentName.transliteration}
              </h2>
            </div>
          </div>

          <div className="flex items-center space-x-2">
            {/* Prev / Next Controls */}
            <div className="flex items-center space-x-1 bg-black/50 p-1 rounded-xl border border-white/10">
              <button
                onClick={() => navigateName(prevId)}
                className="p-1.5 text-slate-400 hover:text-[#D4AF37] rounded-lg hover:bg-white/5 transition-colors"
                title="Previous Name"
              >
                <ChevronLeft className="w-4 h-4" />
              </button>
              <button
                onClick={() => navigateName(nextId)}
                className="p-1.5 text-slate-400 hover:text-[#D4AF37] rounded-lg hover:bg-white/5 transition-colors"
                title="Next Name"
              >
                <ChevronRight className="w-4 h-4" />
              </button>
            </div>

            <button
              onClick={onClose}
              className="p-2 text-slate-400 hover:text-white rounded-xl hover:bg-white/5 transition-colors cursor-pointer"
              aria-label="Close modal"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Calligraphy Hero Section */}
        <div className="p-6 bg-gradient-to-b from-[#0F172A] to-transparent border-b border-white/[0.06] flex flex-col items-center text-center relative">
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-[11px] px-3 py-0.5 rounded-full bg-[#064E3B]/50 border border-[#064E3B] text-emerald-300 font-medium">
              {currentName.category}
            </span>
            <span className="text-[11px] px-2.5 py-0.5 rounded-full bg-white/[0.05] border border-white/10 text-slate-300 font-mono">
              Root: {currentName.root_ar}
            </span>
          </div>

          <h1 className="font-serif text-5xl sm:text-6xl font-bold text-white tracking-wide my-2 leading-tight drop-shadow-md">
            {currentName.name_ar}
          </h1>

          <p className="text-sm font-serif font-bold text-[#D4AF37] tracking-widest uppercase">
            {currentName.transliteration}
          </p>

          <p className="text-xs text-slate-300 max-w-md mt-1">
            {currentName.meaning_en} • <span dir="rtl" className="font-serif">{currentName.meaning_ur}</span>
          </p>

          {/* Pronunciation Play Button */}
          <button
            onClick={playAudio}
            className={`mt-4 px-4 py-2 rounded-xl border flex items-center space-x-2 text-xs font-semibold transition-all cursor-pointer shadow-lg ${
              isPlayingAudio
                ? "bg-[#D4AF37] text-black border-[#D4AF37] shadow-[#D4AF37]/20"
                : "bg-black/50 text-slate-200 border-white/15 hover:border-[#D4AF37]/60 hover:text-white"
            }`}
          >
            <Volume2 className="w-4 h-4 text-[#D4AF37]" />
            <span>{isPlayingAudio ? "Playing Vocal Pronunciation..." : "Listen to Pronunciation"}</span>
          </button>
        </div>

        {/* Navigation Tabs */}
        <div className="flex border-b border-white/[0.08] px-4 bg-black/20 gap-2">
          <button
            onClick={() => setActiveTab("contemplation")}
            className={`py-2.5 px-3 text-xs font-semibold flex items-center space-x-1.5 border-b-2 transition-all cursor-pointer ${
              activeTab === "contemplation"
                ? "border-[#D4AF37] text-[#D4AF37]"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <ScrollText className="w-3.5 h-3.5" />
            <span>Theological Meaning</span>
          </button>

          <button
            onClick={() => setActiveTab("scripture")}
            className={`py-2.5 px-3 text-xs font-semibold flex items-center space-x-1.5 border-b-2 transition-all cursor-pointer ${
              activeTab === "scripture"
                ? "border-[#D4AF37] text-[#D4AF37]"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            <span>Scripture & Hadith</span>
          </button>

          <button
            onClick={() => setActiveTab("tasbih")}
            className={`py-2.5 px-3 text-xs font-semibold flex items-center space-x-1.5 border-b-2 transition-all cursor-pointer ${
              activeTab === "tasbih"
                ? "border-[#D4AF37] text-[#D4AF37]"
                : "border-transparent text-slate-400 hover:text-slate-200"
            }`}
          >
            <Sparkles className="w-3.5 h-3.5" />
            <span>Contemplative Dhikr</span>
          </button>
        </div>

        {/* Tab Body Content */}
        <div className="flex-1 overflow-y-auto p-5 space-y-4">
          {activeTab === "contemplation" && (
            <div className="space-y-4 animate-in fade-in duration-150">
              {/* English Explanation Card */}
              <div className="rounded-2xl bg-black/30 border border-white/[0.08] p-4">
                <h4 className="text-xs font-bold text-[#D4AF37] uppercase tracking-wider mb-1.5">
                  Theological Commentary (English)
                </h4>
                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans">
                  {currentName.explanation_en}
                </p>
              </div>

              {/* Urdu Explanation Card */}
              <div className="rounded-2xl bg-black/30 border border-white/[0.08] p-4 text-right" dir="rtl">
                <h4 className="text-xs font-bold text-[#D4AF37] uppercase tracking-wider mb-1.5">
                  ایمانی و روحانی مفہوم (اردو)
                </h4>
                <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-serif">
                  {currentName.explanation_ur}
                </p>
              </div>

              {/* Root Analysis Card */}
              <div className="rounded-2xl bg-[#064E3B]/20 border border-[#064E3B]/40 p-4">
                <h4 className="text-xs font-bold text-emerald-300 uppercase tracking-wider mb-1">
                  Linguistic Derivation (Classical Arabic Root)
                </h4>
                <p className="text-xs text-slate-300 leading-relaxed">
                  Derived from the trilateral Arabic root <strong className="text-white font-mono">{currentName.root_ar}</strong>, encapsulating fundamental divine attributes that manifest throughout creation.
                </p>
              </div>
            </div>
          )}

          {activeTab === "scripture" && (
            <div className="space-y-4 animate-in fade-in duration-150">
              {/* Quranic References */}
              <div>
                <h4 className="text-xs font-bold text-[#D4AF37] uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <BookOpen className="w-3.5 h-3.5 text-[#D4AF37]" />
                  <span>Primary Quranic Occurrences</span>
                </h4>

                <div className="space-y-2.5">
                  {(scriptureData?.quran_verses || currentName.quran_references || []).map((qref, idx) => (
                    <div
                      key={idx}
                      className="rounded-2xl bg-black/40 border border-white/10 p-3.5 space-y-1.5 hover:border-[#D4AF37]/40 transition-colors"
                    >
                      <div className="flex items-center justify-between text-[11px] text-[#D4AF37] font-semibold">
                        <span>Surah {qref.surah}, Ayah {qref.ayah}</span>
                        <a
                          href={`/?juz=1&ayah=0`}
                          className="hover:underline flex items-center space-x-1 text-slate-400 hover:text-white"
                        >
                          <span>Open in Reader</span>
                          <ExternalLink className="w-3 h-3" />
                        </a>
                      </div>
                      <p className="font-serif text-lg text-white text-right leading-loose" dir="rtl">
                        {qref.text}
                      </p>
                      {qref.translation && (
                        <p className="text-xs text-slate-300 italic font-sans">
                          &quot;{qref.translation}&quot;
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Canonical Hadith References */}
              <div className="pt-2 border-t border-white/[0.08]">
                <h4 className="text-xs font-bold text-[#D4AF37] uppercase tracking-wider mb-2 flex items-center space-x-1.5">
                  <Layers className="w-3.5 h-3.5 text-[#D4AF37]" />
                  <span>Canonical Hadith Evidence</span>
                </h4>

                <div className="space-y-2.5">
                  {(scriptureData?.hadith_citations || []).map((h, idx) => (
                    <div
                      key={idx}
                      className="rounded-2xl bg-black/30 border border-white/10 p-3.5 space-y-1.5"
                    >
                      <div className="flex items-center justify-between text-[11px]">
                        <span className="text-[#D4AF37] font-bold">{h.collection} #{h.hadith_number}</span>
                        <span className="text-slate-400">{h.narrator}</span>
                      </div>
                      <p className="font-serif text-base text-slate-200 text-right leading-loose" dir="rtl">
                        {h.arabic}
                      </p>
                      <p className="text-xs text-slate-300 font-sans">
                        {h.english}
                      </p>
                      {h.urdu && (
                        <p className="text-xs text-slate-400 font-serif text-right" dir="rtl">
                          {h.urdu}
                        </p>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {activeTab === "tasbih" && (
            <div className="animate-in fade-in duration-150">
              <TasbihCounter
                nameId={currentName.id}
                nameArabic={currentName.name_ar}
                transliteration={currentName.transliteration}
                defaultTarget={33}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

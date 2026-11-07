"use client";

import React, { useState, useEffect } from "react";
import { X, BookOpen, Scroll, Globe, Copy, Check, ExternalLink, History, ShieldCheck, AlertCircle } from "lucide-react";
import {
  Ayah,
  TafsirSource,
  RelatedHadith,
  AsbabData,
  fetchTafsir,
  fetchRelatedHadith,
  fetchAsbabAlNuzul,
} from "@/lib/api";

interface VerseContextDrawerProps {
  ayah: Ayah | null;
  onClose: () => void;
}

export function VerseContextDrawer({ ayah, onClose }: VerseContextDrawerProps) {
  const [activeTab, setActiveTab] = useState<"tafsir" | "hadith" | "asbab">("tafsir");
  const [tafsirLang, setTafsirLang] = useState<string>("en");
  const [tafsirList, setTafsirList] = useState<TafsirSource[]>([]);
  const [hadithList, setHadithList] = useState<RelatedHadith[]>([]);
  const [asbabData, setAsbabData] = useState<AsbabData | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  useEffect(() => {
    if (!ayah) return;

    let isMounted = true;
    setLoading(true);

    async function loadContext() {
      if (!ayah) return;
      try {
        if (activeTab === "tafsir") {
          const tafsirs = await fetchTafsir(ayah.surah_number, ayah.number_in_surah, tafsirLang);
          if (isMounted) setTafsirList(tafsirs);
        } else if (activeTab === "hadith") {
          const hadiths = await fetchRelatedHadith(
            ayah.surah_name,
            ayah.number_in_surah,
            ayah.english
          );
          if (isMounted) setHadithList(hadiths);
        } else if (activeTab === "asbab") {
          const asbab = await fetchAsbabAlNuzul(ayah.surah_number, ayah.number_in_surah);
          if (isMounted) setAsbabData(asbab);
        }
      } catch (err) {
        console.error("Context load error:", err);
      } finally {
        if (isMounted) setLoading(false);
      }
    }

    loadContext();

    return () => {
      isMounted = false;
    };
  }, [ayah, activeTab, tafsirLang]);

  // Handle Escape key
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [onClose]);

  const handleCopyText = (text: string, key: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(key);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  if (!ayah) return null;

  return (
    <div
      onClick={onClose}
      className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 bg-black/75 backdrop-blur-md transition-opacity animate-in fade-in duration-200 cursor-pointer"
    >
      <div
        onClick={(e) => e.stopPropagation()}
        className="relative w-full max-w-3xl max-h-[85vh] glass-panel border border-[#D4AF37]/35 rounded-2xl flex flex-col shadow-2xl bg-[#080C14]/95 overflow-hidden cursor-default animate-in zoom-in-95 duration-200"
      >
        {/* Header */}
        <div className="p-4 sm:p-5 border-b border-white/[0.08] flex items-center justify-between bg-black/40">
          <div>
            <div className="flex items-center space-x-2">
              <span className="px-2 py-0.5 rounded-md bg-[#D4AF37]/15 border border-[#D4AF37]/40 text-[10px] font-bold text-[#D4AF37] uppercase">
                Verse Context
              </span>
              <h3 className="text-sm sm:text-base font-serif font-bold text-white tracking-wide">
                Surah {ayah.surah_name} ({ayah.surah_number}:{ayah.number_in_surah})
              </h3>
            </div>
            <p className="text-xs text-slate-400 mt-1 truncate max-w-lg font-sans">
              {ayah.english}
            </p>
          </div>

          <button
            onClick={onClose}
            className="p-1.5 text-slate-400 hover:text-white rounded-lg hover:bg-white/5 transition-all cursor-pointer hover:scale-110 active:scale-95"
            aria-label="Close"
            title="Close Exegesis Modal (ESC)"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Tabs Bar */}
        <div className="flex items-center justify-between px-5 pt-3 border-b border-white/[0.06] bg-black/20">
          <div className="flex space-x-5">
            <button
              onClick={() => setActiveTab("tafsir")}
              className={`pb-2.5 text-xs font-semibold flex items-center space-x-1.5 border-b-2 transition-all cursor-pointer ${
                activeTab === "tafsir"
                  ? "border-[#D4AF37] text-[#D4AF37]"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <BookOpen className="w-3.5 h-3.5" />
              <span>Classical Tafseer</span>
            </button>

            <button
              onClick={() => setActiveTab("hadith")}
              className={`pb-2.5 text-xs font-semibold flex items-center space-x-1.5 border-b-2 transition-all cursor-pointer ${
                activeTab === "hadith"
                  ? "border-[#D4AF37] text-[#D4AF37]"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <Scroll className="w-3.5 h-3.5" />
              <span>Related Hadith</span>
            </button>

            <button
              onClick={() => setActiveTab("asbab")}
              className={`pb-2.5 text-xs font-semibold flex items-center space-x-1.5 border-b-2 transition-all cursor-pointer ${
                activeTab === "asbab"
                  ? "border-[#D4AF37] text-[#D4AF37]"
                  : "border-transparent text-slate-400 hover:text-slate-200"
              }`}
            >
              <History className="w-3.5 h-3.5" />
              <span>Asbab al-Nuzul (أسباب النزول)</span>
            </button>
          </div>

          {activeTab === "tafsir" && (
            <div className="flex items-center space-x-1.5 pb-2">
              <Globe className="w-3.5 h-3.5 text-[#D4AF37]" />
              <select
                value={tafsirLang}
                onChange={(e) => setTafsirLang(e.target.value)}
                className="bg-black/40 border border-white/10 rounded-lg px-2.5 py-1 text-[11px] text-slate-200 focus:outline-none focus:border-[#D4AF37]/60 cursor-pointer transition-colors"
              >
                <option value="en">English (Ibn Kathir / Maarif)</option>
                <option value="ur">اردو (معارف القرآن / ابن کثیر)</option>
                <option value="ar">العربية (الميسر / الجلالين)</option>
              </select>
            </div>
          )}
        </div>

        {/* Content Body */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-5 space-y-4">
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="w-7 h-7 border-2 border-[#D4AF37] border-t-transparent rounded-full animate-spin mb-3 shadow-md" />
              <p className="text-xs text-slate-400 font-sans">Consulting authenticated Islamic repositories...</p>
            </div>
          ) : activeTab === "tafsir" ? (
            tafsirList.length === 0 ? (
              <p className="text-center text-xs text-slate-500 py-10 font-sans">
                No verified Tafseer excerpts available for this selection.
              </p>
            ) : (
              tafsirList.map((t, idx) => (
                <div
                  key={idx}
                  className="p-4 rounded-xl bg-white/[0.03] border border-white/[0.06] space-y-2 hover:border-[#D4AF37]/35 transition-all duration-200 shadow-sm group"
                >
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-serif font-bold text-[#D4AF37]">
                      {t.source_name}
                    </span>
                    <div className="flex items-center space-x-2">
                      <span className="text-[9px] uppercase font-mono px-1.5 py-0.5 rounded bg-emerald-950/80 text-emerald-300 border border-emerald-700/40">
                        Authentic Source
                      </span>
                      <button
                        onClick={() => handleCopyText(t.text, `tafsir-${idx}`)}
                        className="p-1 rounded text-slate-400 hover:text-[#D4AF37] transition-colors cursor-pointer"
                        title="Copy Excerpt"
                      >
                        {copiedKey === `tafsir-${idx}` ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>
                  <p
                    className={`text-xs sm:text-sm text-slate-200 leading-relaxed ${
                      t.language === "ar" || t.language === "ur"
                        ? "quran-arabic text-base"
                        : "font-sans"
                    }`}
                  >
                    {t.text}
                  </p>
                </div>
              ))
            )
          ) : activeTab === "hadith" ? (
            hadithList.length === 0 ? (
              <p className="text-center text-xs text-slate-500 py-10 font-sans">
                No direct contextual narrations found for this Ayah in immediate corpus.
              </p>
            ) : (
            hadithList.map((h, idx) => {
              // Extract text fields resiliently across schemas
              const excerpt = h.excerpt || h.text || "";
              let arabic = h.text_arabic || "";
              let english = h.text_english || h.text || "";
              let narrator = h.narrator || "";

              if (!arabic && !english && excerpt) {
                if (excerpt.includes("Arabic:") && excerpt.includes("English:")) {
                  const arSplit = excerpt.split("Arabic:")[1];
                  const enSplit = arSplit.split("English:");
                  arabic = enSplit[0].trim();
                  english = enSplit[1]?.trim() || "";
                } else if (excerpt.includes("English:")) {
                  english = excerpt.split("English:")[1].trim();
                } else {
                  english = excerpt.trim();
                }
              }

              if (!narrator && excerpt.includes("Narrator:")) {
                try {
                  narrator = excerpt.split("Narrator:")[1].split("\n")[0].trim();
                } catch {
                  // Ignore
                }
              }

              const sourceTitle =
                h.source ||
                h.title ||
                h.source_name ||
                (h.book ? `${h.book} #${h.hadith_no}` : "Canonical Narration");

              const sunnahDeepUrl =
                h.url && h.url !== "https://sunnah.com"
                  ? h.url
                  : `https://sunnah.com/search?q=${encodeURIComponent(
                      `${h.book || sourceTitle} ${arabic ? arabic.slice(0, 35) : english.slice(0, 40)}`
                    )}`;

              const fullCopyText = `[${sourceTitle}]\n${
                narrator ? `Narrator: ${narrator}\n` : ""
              }${arabic ? `Arabic: ${arabic}\n` : ""}${
                english ? `English: ${english}\n` : ""
              }Reference: sunnah.com (${h.url || sunnahDeepUrl})`;

              return (
                <div
                  key={idx}
                  className="p-4 sm:p-5 rounded-2xl bg-white/[0.03] border border-white/[0.08] hover:border-[#D4AF37]/50 transition-all duration-200 shadow-md space-y-3"
                >
                  {/* Card Header */}
                  <div className="flex items-center justify-between border-b border-white/[0.06] pb-2.5">
                    <div className="flex items-center space-x-2 truncate">
                      <span className="w-6 h-6 rounded-lg bg-[#D4AF37]/15 border border-[#D4AF37]/40 text-[#D4AF37] flex items-center justify-center text-xs">
                        📜
                      </span>
                      <h4 className="text-xs sm:text-sm font-serif font-bold text-[#D4AF37] truncate">
                        {sourceTitle}
                      </h4>
                    </div>

                    <div className="flex items-center space-x-2 flex-shrink-0">
                      {/* Authentic Theological Grading Badge */}
                      {h.grading_badge && (
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-mono font-bold tracking-wider uppercase border ${
                            h.grading_badge.tier === "sahih"
                              ? "bg-emerald-950/90 text-emerald-300 border-emerald-500/50"
                              : h.grading_badge.tier === "hasan"
                              ? "bg-cyan-950/90 text-cyan-300 border-cyan-500/50"
                              : h.grading_badge.tier === "daif"
                              ? "bg-amber-950/90 text-amber-300 border-amber-500/50"
                              : h.grading_badge.tier === "mawdu"
                              ? "bg-rose-950/90 text-rose-300 border-rose-500/50"
                              : "bg-white/[0.06] text-slate-300 border-white/10"
                          }`}
                          title={`Grading: ${h.grading_badge.label}`}
                        >
                          {h.grading_badge.label}
                        </span>
                      )}

                      {/* Interactive sunnah.com Citation Badge */}
                      <a
                        href={sunnahDeepUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center space-x-1.5 px-2.5 py-0.5 rounded-full bg-emerald-950/80 hover:bg-emerald-900 border border-emerald-500/50 hover:border-emerald-400 text-emerald-300 hover:text-white text-[11px] font-mono font-bold transition-all shadow-sm group cursor-pointer"
                        title="View verified narration on Sunnah.com"
                      >
                        <Globe className="w-3 h-3 text-emerald-400 group-hover:scale-110 transition-transform" />
                        <span>sunnah.com</span>
                        <ExternalLink className="w-3 h-3 text-emerald-400 group-hover:translate-x-0.5 group-hover:-translate-y-0.5 transition-transform" />
                      </a>

                      <button
                        onClick={() => handleCopyText(fullCopyText, `hadith-${idx}`)}
                        className="p-1 rounded text-slate-400 hover:text-[#D4AF37] transition-colors cursor-pointer"
                        title="Copy Complete Hadith"
                      >
                        {copiedKey === `hadith-${idx}` ? (
                          <Check className="w-3.5 h-3.5 text-emerald-400" />
                        ) : (
                          <Copy className="w-3.5 h-3.5" />
                        )}
                      </button>
                    </div>
                  </div>

                  {/* Narrator */}
                  {narrator && (
                    <p className="text-[11px] text-[#D4AF37]/90 font-medium italic font-sans">
                      Narrator: {narrator}
                    </p>
                  )}

                  {/* Arabic Matn */}
                  {arabic && (
                    <div className="p-3.5 rounded-xl bg-black/40 border border-white/[0.06] shadow-inner">
                      <p className="quran-arabic text-xl sm:text-2xl text-right text-slate-100 leading-[2.3] select-text">
                        {arabic}
                      </p>
                    </div>
                  )}

                  {/* English Translation */}
                  {english && (
                    <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/[0.06]">
                      <span className="text-[10px] font-bold tracking-widest uppercase text-[#D4AF37] block mb-1">
                        English Translation
                      </span>
                      <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans select-text">
                        {english}
                      </p>
                    </div>
                  )}

                  {/* Card Footer */}
                  <div className="pt-2 border-t border-white/[0.04] flex items-center justify-between text-[10px] text-slate-500 font-mono">
                    <span>Canonical Hadith Corpus (50,762 Verified)</span>
                    {h.hadith_no && <span>Hadith #{h.hadith_no}</span>}
                  </div>
                </div>
              );
            })
          )) : (
            /* Asbab al-Nuzul View */
            !asbabData ? (
              <p className="text-center text-xs text-slate-500 py-10 font-sans">
                No historical revelation data recorded for this Ayah.
              </p>
            ) : (
              <div className="p-5 rounded-2xl bg-white/[0.03] border border-[#D4AF37]/35 shadow-xl space-y-4">
                {/* Header with Title and Classification Badges */}
                <div className="flex flex-wrap items-center justify-between gap-2 border-b border-white/[0.08] pb-3">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="w-6 h-6 rounded-lg bg-[#D4AF37]/15 border border-[#D4AF37]/40 text-[#D4AF37] flex items-center justify-center text-xs">
                        📜
                      </span>
                      <h4 className="text-sm sm:text-base font-serif font-bold text-[#D4AF37]">
                        {asbabData.title}
                      </h4>
                    </div>
                    <span className="text-[11px] text-slate-400 font-mono mt-0.5 block">
                      {asbabData.category}
                    </span>
                  </div>

                  <div className="flex flex-wrap items-center gap-1.5">
                    <span className="px-2.5 py-0.5 rounded-full bg-[#064E3B]/80 border border-[#D4AF37]/40 text-[#D4AF37] text-[10px] font-mono font-bold">
                      📍 {asbabData.period}
                    </span>
                    <span className="px-2.5 py-0.5 rounded-full bg-black/50 border border-white/10 text-slate-300 text-[10px] font-mono">
                      {asbabData.authority}
                    </span>
                  </div>
                </div>

                {/* Narrator */}
                {asbabData.narrator && (
                  <p className="text-xs text-[#D4AF37]/90 font-medium font-sans">
                    <span className="text-slate-400">Narrator:</span> {asbabData.narrator}
                  </p>
                )}

                {/* Arabic Matn Summary */}
                {asbabData.arabic_summary && (
                  <div className="p-4 rounded-xl bg-black/40 border border-emerald-900/30 shadow-inner">
                    <p className="quran-arabic text-xl sm:text-2xl text-right text-emerald-100 leading-[2.2] select-text">
                      {asbabData.arabic_summary}
                    </p>
                  </div>
                )}

                {/* Circumstance Narrative */}
                <div className="p-4 rounded-xl bg-white/[0.02] border border-white/[0.06] space-y-1.5">
                  <span className="text-[10px] font-bold tracking-widest uppercase text-[#D4AF37] block">
                    Historical Context & Cause of Revelation
                  </span>
                  <p className="text-xs sm:text-sm text-slate-200 leading-relaxed font-sans select-text">
                    {asbabData.circumstance}
                  </p>
                </div>

                {/* Theological & Juridical Significance */}
                {asbabData.significance && (
                  <div className="p-3.5 rounded-xl bg-[#064E3B]/20 border border-[#064E3B]/50 space-y-1">
                    <span className="text-[10px] font-bold tracking-widest uppercase text-emerald-400 block">
                      Theological & Juridical Significance
                    </span>
                    <p className="text-xs text-emerald-200/90 leading-relaxed font-sans">
                      {asbabData.significance}
                    </p>
                  </div>
                )}

                {/* Reference */}
                <div className="pt-2 border-t border-white/[0.06] flex items-center justify-between text-[10px] text-slate-400 font-mono">
                  <span>Source: {asbabData.reference}</span>
                  <button
                    onClick={() =>
                      handleCopyText(
                        `[Asbab al-Nuzul: ${asbabData.title}]\n${asbabData.circumstance}\nSignificance: ${asbabData.significance}\nReference: ${asbabData.reference}`,
                        "asbab"
                      )
                    }
                    className="flex items-center space-x-1 text-[#D4AF37] hover:underline cursor-pointer"
                  >
                    {copiedKey === "asbab" ? (
                      <>
                        <Check className="w-3 h-3 text-emerald-400" />
                        <span>Copied</span>
                      </>
                    ) : (
                      <>
                        <Copy className="w-3 h-3" />
                        <span>Copy Context</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            )
          )}
        </div>
      </div>
    </div>
  );
}

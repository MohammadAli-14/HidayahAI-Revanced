"use client";

import React, { useState, useMemo, useRef, useEffect, useCallback } from "react";
import { Search, Sparkles, Play, Pause, X, RotateCcw, Volume2 } from "lucide-react";
import { NameOfAllah, NameCategory } from "@/lib/api";
import { NameCard } from "./NameCard";
import { NameDetailModal } from "./NameDetailModal";
import { NamesContinuousPlayerBar } from "./NamesContinuousPlayerBar";

interface NamesGridProps {
  initialNames: NameOfAllah[];
  categories: NameCategory[];
}

export function NamesGrid({ initialNames, categories }: NamesGridProps) {
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [selectedCategory, setSelectedCategory] = useState<string>("All");
  const [selectedName, setSelectedName] = useState<NameOfAllah | null>(null);
  const [toastMessage, setToastMessage] = useState<string | null>(null);

  // Central Continuous Audio State
  const [isContinuousActive, setIsContinuousActive] = useState<boolean>(false);
  const [continuousIndex, setContinuousIndex] = useState<number>(0);
  const [isContinuousPlaying, setIsContinuousPlaying] = useState<boolean>(false);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0);
  const [isLoopingAll, setIsLoopingAll] = useState<boolean>(true);

  const continuousAudioRef = useRef<HTMLAudioElement | null>(null);
  const lookaheadAudioRef = useRef<HTMLAudioElement | null>(null);

  const showToast = useCallback((msg: string) => {
    setToastMessage(msg);
    setTimeout(() => {
      setToastMessage(null);
    }, 4000);
  }, []);

  // Filter names based on search and selected category
  const filteredNames = useMemo(() => {
    let list = initialNames;

    if (selectedCategory !== "All") {
      const catLower = selectedCategory.toLowerCase();
      list = list.filter(
        (n) =>
          n.category.toLowerCase() === catLower ||
          n.category_ur.toLowerCase() === catLower
      );
    }

    if (searchTerm.trim()) {
      const term = searchTerm.toLowerCase().trim();
      list = list.filter(
        (n) =>
          n.name_ar.includes(term) ||
          n.transliteration.toLowerCase().includes(term) ||
          n.meaning_en.toLowerCase().includes(term) ||
          n.meaning_ur.includes(term) ||
          n.root_ar.includes(term) ||
          n.number.toString() === term
      );
    }

    return list;
  }, [initialNames, selectedCategory, searchTerm]);

  // Audio Playback lifecycle for Central Player
  const isTransitioningRef = useRef<boolean>(false);

  // Play a specific track index in continuous mode
  const playTrack = useCallback((index: number) => {
    if (filteredNames.length === 0) return;
    const targetIndex = Math.max(0, Math.min(index, filteredNames.length - 1));
    const targetItem = filteredNames[targetIndex];
    if (!targetItem) return;

    if (!continuousAudioRef.current) {
      continuousAudioRef.current = new Audio();
    }

    const audio = continuousAudioRef.current;
    audio.playbackRate = playbackSpeed;

    // Attach sync event listeners to keep UI 100% aligned with actual audio state
    audio.onplay = () => setIsContinuousPlaying(true);
    audio.onpause = () => setIsContinuousPlaying(false);

    audio.onended = () => {
      if (isTransitioningRef.current) return;
      isTransitioningRef.current = true;

      setTimeout(() => {
        setContinuousIndex((prev) => {
          if (prev < filteredNames.length - 1) {
            return prev + 1;
          } else if (isLoopingAll) {
            return 0;
          } else {
            setIsContinuousPlaying(false);
            return prev;
          }
        });
        isTransitioningRef.current = false;
      }, 300);
    };

    audio.onerror = () => {
      console.warn(`Primary audio failed for ${targetItem.transliteration}, trying fallback.`);
      if (targetItem.audio_fallback_url && audio.src !== targetItem.audio_fallback_url) {
        audio.src = targetItem.audio_fallback_url;
        audio.play().catch((err) => {
          console.warn("Fallback audio play failed:", err);
          setIsContinuousPlaying(false);
        });
      } else {
        setIsContinuousPlaying(false);
      }
    };

    // Load and play new track
    if (audio.src !== targetItem.audio_url) {
      audio.src = targetItem.audio_url;
    }
    audio.currentTime = 0;
    audio.play().then(() => {
      setIsContinuousPlaying(true);
    }).catch((err) => {
      console.warn("Audio play prevented or interrupted:", err);
    });

    setContinuousIndex(targetIndex);
    setIsContinuousActive(true);
  }, [filteredNames, playbackSpeed, isLoopingAll]);

  // When continuousIndex changes while active, ensure correct track is playing
  useEffect(() => {
    if (!isContinuousActive || filteredNames.length === 0) return;
    const currentItem = filteredNames[continuousIndex];
    if (!currentItem || !continuousAudioRef.current) return;

    const audio = continuousAudioRef.current;
    if (audio.src !== currentItem.audio_url && audio.src !== currentItem.audio_fallback_url) {
      audio.src = currentItem.audio_url;
      audio.playbackRate = playbackSpeed;
      if (isContinuousPlaying) {
        audio.play().catch(console.warn);
      }
    }
  }, [continuousIndex, isContinuousActive, filteredNames, playbackSpeed, isContinuousPlaying]);

  // Lookahead prefetching next audio file
  useEffect(() => {
    const nextItem = filteredNames[continuousIndex + 1];
    if (isContinuousActive && nextItem) {
      if (!lookaheadAudioRef.current) {
        lookaheadAudioRef.current = new Audio();
      }
      lookaheadAudioRef.current.src = nextItem.audio_url;
      lookaheadAudioRef.current.preload = "auto";
    }
  }, [continuousIndex, isContinuousActive, filteredNames]);

  // Synchronized Auto-Scroll into view when continuous name advances
  useEffect(() => {
    if (isContinuousActive && filteredNames[continuousIndex]) {
      const activeId = filteredNames[continuousIndex].id;
      const el = document.getElementById(`name-card-${activeId}`);
      if (el) {
        el.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }
  }, [continuousIndex, isContinuousActive, filteredNames]);

  // Central Recitation Handlers
  const handleStartContinuousPlay = (startIndex: number = 0) => {
    playTrack(startIndex);
  };

  const handleTogglePlayPause = () => {
    if (!continuousAudioRef.current) {
      playTrack(continuousIndex);
      return;
    }
    const audio = continuousAudioRef.current;
    if (audio.paused) {
      audio.play().then(() => {
        setIsContinuousPlaying(true);
      }).catch(console.warn);
    } else {
      audio.pause();
      setIsContinuousPlaying(false);
    }
  };

  const handleNextContinuous = () => {
    const nextIdx = continuousIndex < filteredNames.length - 1
      ? continuousIndex + 1
      : isLoopingAll
      ? 0
      : continuousIndex;
    playTrack(nextIdx);
  };

  const handlePrevContinuous = () => {
    const prevIdx = continuousIndex > 0
      ? continuousIndex - 1
      : isLoopingAll
      ? filteredNames.length - 1
      : 0;
    playTrack(prevIdx);
  };

  const handleToggleSpeed = () => {
    const speeds = [1.0, 1.25, 1.5];
    const nextIdx = (speeds.indexOf(playbackSpeed) + 1) % speeds.length;
    const newSpeed = speeds[nextIdx];
    setPlaybackSpeed(newSpeed);
    if (continuousAudioRef.current) {
      continuousAudioRef.current.playbackRate = newSpeed;
    }
  };

  const handleToggleLoop = () => {
    setIsLoopingAll((prev) => !prev);
  };

  const handleCloseContinuous = () => {
    if (continuousAudioRef.current) {
      continuousAudioRef.current.pause();
      continuousAudioRef.current.src = "";
    }
    setIsContinuousPlaying(false);
    setIsContinuousActive(false);
  };

  const activeContinuousId =
    isContinuousActive && filteredNames[continuousIndex]
      ? filteredNames[continuousIndex].id
      : null;

  return (
    <div className="w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8 pb-32">
      {/* Search & Central Action Toolbar */}
      <div className="space-y-4">
        {/* Search Input Bar & Central Play All Action */}
        <div className="flex flex-col sm:flex-row items-center gap-3 max-w-3xl mx-auto">
          <div className="relative flex-1 w-full">
            <Search className="absolute left-4 top-3.5 w-4 h-4 text-slate-400" />
            <input
              type="text"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              placeholder="Search by Arabic, Transliteration, English, Urdu, or Root (e.g. Ar-Rahman, ر-ح-م)..."
              className="w-full pl-11 pr-10 py-3 bg-[#0F172A]/90 border border-white/10 hover:border-[#D4AF37]/50 focus:border-[#D4AF37] rounded-2xl text-sm text-slate-100 placeholder-slate-500 focus:outline-none shadow-xl transition-all"
            />
            {searchTerm && (
              <button
                onClick={() => setSearchTerm("")}
                className="absolute right-3.5 top-3.5 p-1 text-slate-400 hover:text-white rounded-lg"
                title="Clear Search"
              >
                <X className="w-4 h-4" />
              </button>
            )}
          </div>

          {/* Central Play All Button */}
          <button
            onClick={() => {
              if (isContinuousActive) {
                handleTogglePlayPause();
              } else {
                handleStartContinuousPlay(0);
              }
            }}
            className="w-full sm:w-auto flex items-center justify-center space-x-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-[#D4AF37] to-[#F3E5AB] hover:from-[#E5C158] hover:to-[#FFF0B8] text-black font-semibold text-xs shadow-xl shadow-[#D4AF37]/25 hover:scale-105 active:scale-95 transition-all duration-200 cursor-pointer flex-shrink-0"
            title="Start continuous sequential recitation of all Divine Names"
          >
            {isContinuousActive && isContinuousPlaying ? (
              <>
                <Pause className="w-4 h-4 fill-black" />
                <span>Pause Recitation</span>
              </>
            ) : (
              <>
                <Play className="w-4 h-4 fill-black translate-x-0.5" />
                <span>Play All ({filteredNames.length})</span>
              </>
            )}
          </button>
        </div>

        {/* Category Filter Pills (No left clipping on any viewport) */}
        <div className="w-full flex items-center overflow-x-auto pb-2 scrollbar-none gap-2 px-2 scroll-smooth">
          <button
            onClick={() => setSelectedCategory("All")}
            className={`px-4 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer border flex-shrink-0 ${
              selectedCategory === "All"
                ? "bg-[#D4AF37] text-black border-[#D4AF37] shadow-md shadow-[#D4AF37]/20 font-bold"
                : "bg-black/50 text-slate-300 border-white/10 hover:border-[#D4AF37]/40 hover:text-white"
            }`}
          >
            All Names ({initialNames.length})
          </button>

          {categories.map((cat) => (
            <button
              key={cat.category_en}
              onClick={() => setSelectedCategory(cat.category_en)}
              className={`px-3.5 py-2 rounded-xl text-xs font-semibold whitespace-nowrap transition-all cursor-pointer border flex-shrink-0 ${
                selectedCategory === cat.category_en
                  ? "bg-[#D4AF37] text-black border-[#D4AF37] shadow-md shadow-[#D4AF37]/20 font-bold"
                  : "bg-black/50 text-slate-300 border-white/10 hover:border-[#D4AF37]/40 hover:text-white"
              }`}
            >
              <span>{cat.category_en}</span>
              <span className="ml-1.5 opacity-70 font-mono text-[10px]">({cat.count})</span>
            </button>
          ))}
        </div>
      </div>

      {/* Results Count & Meta */}
      <div className="flex items-center justify-between text-xs text-slate-400 border-b border-white/[0.06] pb-3">
        <span className="flex items-center space-x-2">
          <span>
            Showing <strong className="text-white font-mono">{filteredNames.length}</strong> of 99 Divine Names
          </span>
          {isContinuousActive && (
            <span className="inline-flex items-center space-x-1 text-[#D4AF37] font-semibold text-[11px] animate-pulse">
              <span>• Continuous Recitation Active</span>
            </span>
          )}
        </span>

        {selectedCategory !== "All" && (
          <button
            onClick={() => setSelectedCategory("All")}
            className="text-xs text-[#D4AF37] hover:underline flex items-center space-x-1 cursor-pointer"
          >
            <span>Reset filter ({selectedCategory})</span>
            <RotateCcw className="w-3 h-3" />
          </button>
        )}
      </div>

      {/* Grid of 99 Cards */}
      {filteredNames.length > 0 ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 sm:gap-6">
          {filteredNames.map((name, idx) => (
            <NameCard
              key={name.id}
              name={name}
              onSelect={(n) => setSelectedName(n)}
              onShowToast={showToast}
              isActivelyPlayingContinuous={activeContinuousId === name.id}
            />
          ))}
        </div>
      ) : (
        <div className="rounded-3xl bg-black/30 border border-white/10 p-12 text-center space-y-3">
          <Sparkles className="w-8 h-8 text-[#D4AF37] mx-auto animate-pulse" />
          <h3 className="text-base font-bold text-white">No Divine Names matched your search</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto">
            Try searching with broader terms, root letters, or reset the category filter.
          </p>
          <button
            onClick={() => {
              setSearchTerm("");
              setSelectedCategory("All");
            }}
            className="px-4 py-2 rounded-xl bg-[#D4AF37]/20 border border-[#D4AF37]/50 text-[#D4AF37] text-xs font-semibold hover:bg-[#D4AF37]/30 transition-all cursor-pointer"
          >
            Clear Filters
          </button>
        </div>
      )}

      {/* Name Detail Modal */}
      {selectedName && (
        <NameDetailModal
          initialName={selectedName}
          onClose={() => setSelectedName(null)}
          onShowToast={showToast}
        />
      )}

      {/* Sticky Bottom Continuous Recitation Player Bar */}
      {isContinuousActive && (
        <NamesContinuousPlayerBar
          currentName={filteredNames[continuousIndex] || null}
          currentIndex={continuousIndex}
          totalNames={filteredNames.length}
          isPlaying={isContinuousPlaying}
          playbackSpeed={playbackSpeed}
          isLooping={isLoopingAll}
          onPlayPause={handleTogglePlayPause}
          onNext={handleNextContinuous}
          onPrev={handlePrevContinuous}
          onToggleSpeed={handleToggleSpeed}
          onToggleLoop={handleToggleLoop}
          onClose={handleCloseContinuous}
          onSelectName={(name) => setSelectedName(name)}
        />
      )}

      {/* Non-intrusive Toast Banner */}
      {toastMessage && (
        <div className="fixed bottom-6 right-6 z-50 bg-[#0B0F17]/95 border border-[#D4AF37]/60 text-slate-100 text-xs px-4 py-3 rounded-2xl shadow-2xl backdrop-blur-xl animate-in slide-in-from-bottom-3 duration-200 flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-[#D4AF37] animate-ping" />
          <span>{toastMessage}</span>
        </div>
      )}
    </div>
  );
}

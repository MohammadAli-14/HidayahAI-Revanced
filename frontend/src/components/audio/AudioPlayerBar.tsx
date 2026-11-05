"use client";

import React, { useState, useEffect, useRef, useCallback } from "react";
import {
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Repeat,
  Volume2,
  VolumeX,
} from "lucide-react";
import { Ayah } from "@/lib/api";

interface AudioPlayerBarProps {
  ayahs: Ayah[];
  currentIndex: number;
  isPlaying: boolean;
  onPlayPause: () => void;
  onNextAyah: () => void;
  onPrevAyah: () => void;
  audioMode: string;
  isScholarOpen?: boolean;
  isSidebarOpen?: boolean;
}

function formatTime(seconds: number): string {
  if (isNaN(seconds) || seconds < 0) return "0:00";
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs < 10 ? "0" : ""}${secs}`;
}

export function AudioPlayerBar({
  ayahs,
  currentIndex,
  isPlaying,
  onPlayPause,
  onNextAyah,
  onPrevAyah,
  audioMode,
  isScholarOpen = false,
  isSidebarOpen = true,
}: AudioPlayerBarProps) {
  const audioRef = useRef<HTMLAudioElement | null>(null);
  const lookaheadAudioRef = useRef<HTMLAudioElement | null>(null);
  const progressBarRef = useRef<HTMLDivElement | null>(null);
  const [playbackSpeed, setPlaybackSpeed] = useState<number>(1.0);
  const [hifzRepeatTarget, setHifzRepeatTarget] = useState<number>(1); // 1, 3, 5, 999 (infinity)
  const [hifzRepeatCount, setHifzRepeatCount] = useState<number>(1);
  const [hifzPauseMultiplier, setHifzPauseMultiplier] = useState<number>(0); // 0 = no pause, 1 = 1x duration, 1.5 = 1.5x duration
  const [isPausingForStudent, setIsPausingForStudent] = useState<boolean>(false);
  const [isPlayingBismillah, setIsPlayingBismillah] = useState<boolean>(false);
  const [currentTime, setCurrentTime] = useState<number>(0);
  const [duration, setDuration] = useState<number>(0);
  const [isMuted, setIsMuted] = useState<boolean>(false);
  const [subQueueIndex, setSubQueueIndex] = useState<number>(0);
  const [isHoveringProgress, setIsHoveringProgress] = useState<boolean>(false);

  const BISMILLAH_AUDIO_URL = "https://cdn.islamic.network/quran/audio/128/ar.alafasy/1.mp3";

  const currentAyah = ayahs[currentIndex] || null;

  const reciterLabel =
    audioMode === "Urdu Translation Only"
      ? "Urdu (Shamshad Khan)"
      : audioMode === "English Translation Only"
      ? "English (Ibrahim Walk)"
      : audioMode === "Arabic (Mahmoud Al-Husary)"
      ? "Arabic (Al-Husary — Tajweed)"
      : audioMode === "Arabic (Abdul Basit)"
      ? "Arabic (Abdul Basit — Murattal)"
      : audioMode === "Arabic (Al-Minshawi)"
      ? "Arabic (Al-Minshawi — Murattal)"
      : audioMode === "Arabic + Urdu Translation"
      ? subQueueIndex === 0
        ? "Arabic (Mishary)"
        : "Urdu (Shamshad Khan)"
      : audioMode === "Arabic + English Translation"
      ? subQueueIndex === 0
        ? "Arabic (Mishary)"
        : "English (Ibrahim Walk)"
      : "Arabic (Mishary Rashid)";

  const getArabicAudioUrl = useCallback((ayah: Ayah): string => {
    if (audioMode === "Arabic (Mahmoud Al-Husary)") {
      return `https://cdn.islamic.network/quran/audio/128/ar.husary/${ayah.number}.mp3`;
    }
    if (audioMode === "Arabic (Abdul Basit)") {
      return `https://cdn.islamic.network/quran/audio/192/ar.abdulbasitmurattal/${ayah.number}.mp3`;
    }
    if (audioMode === "Arabic (Al-Minshawi)") {
      return `https://cdn.islamic.network/quran/audio/128/ar.minshawi/${ayah.number}.mp3`;
    }
    return ayah.audio_url || `https://cdn.islamic.network/quran/audio/128/ar.alafasy/${ayah.number}.mp3`;
  }, [audioMode]);

  // Determine the sequence of URLs to play for current ayah based on audio mode
  const getAudioUrls = useCallback(
    (ayah: Ayah | null): string[] => {
      if (!ayah) return [];
      const urls: string[] = [];

      if (audioMode === "Urdu Translation Only" && ayah.audio_ur) {
        return [ayah.audio_ur];
      }
      if (audioMode === "English Translation Only" && ayah.audio_en) {
        return [ayah.audio_en];
      }

      // Default has Arabic according to active reciter
      const arabicUrl = getArabicAudioUrl(ayah);
      if (arabicUrl) urls.push(arabicUrl);

      if (audioMode === "Arabic + English Translation" && ayah.audio_en) {
        urls.push(ayah.audio_en);
      } else if (audioMode === "Arabic + Urdu Translation" && ayah.audio_ur) {
        urls.push(ayah.audio_ur);
      }

      return urls;
    },
    [audioMode, getArabicAudioUrl]
  );

  const currentUrls = getAudioUrls(currentAyah);

  // Play audio when currentAyah or subQueueIndex changes
  useEffect(() => {
    if (!audioRef.current || currentUrls.length === 0) return;

    const targetUrl = currentUrls[subQueueIndex] || currentUrls[0];
    if (audioRef.current.src !== targetUrl) {
      audioRef.current.src = targetUrl;
      audioRef.current.playbackRate = playbackSpeed;
    }

    if (isPlaying) {
      audioRef.current.play().catch((err) => {
        console.warn("Audio autoplay policy or stream error:", err);
      });
    } else {
      audioRef.current.pause();
    }
  }, [currentIndex, subQueueIndex, currentUrls, isPlaying, playbackSpeed]);

  // Reset repeat count when navigating to a new Ayah
  useEffect(() => {
    setHifzRepeatCount(1);
    setIsPlayingBismillah(false);
  }, [currentIndex]);

  // Lookahead Pre-buffering when currentTime passes 70% of duration
  const handleTimeUpdate = () => {
    if (!audioRef.current) return;
    const cur = audioRef.current.currentTime;
    const dur = audioRef.current.duration || 0;
    setCurrentTime(cur);
    setDuration(dur);

    // Lookahead: when >= 70% finished, buffer next Ayah's audio
    if (dur > 0 && cur / dur > 0.7 && lookaheadAudioRef.current) {
      const nextAyah = ayahs[currentIndex + 1];
      if (nextAyah) {
        const nextUrls = getAudioUrls(nextAyah);
        if (nextUrls[0] && lookaheadAudioRef.current.src !== nextUrls[0]) {
          lookaheadAudioRef.current.src = nextUrls[0];
          lookaheadAudioRef.current.preload = "auto";
        }
      }
    }
  };

  // Handle Ayah Audio Ended event
  const handleAudioEnded = () => {
    // If we just finished playing Bismillah before Surah start, now commence Verse 1!
    if (isPlayingBismillah) {
      setIsPlayingBismillah(false);
      setSubQueueIndex(0);
      onNextAyah();
      return;
    }

    // Check Hifz Repeat Target
    if (hifzRepeatTarget > 1 && hifzRepeatCount < hifzRepeatTarget) {
      setHifzRepeatCount((prev) => prev + 1);
      
      // If student pause is enabled, pause to allow student self-recitation from memory
      if (hifzPauseMultiplier > 0) {
        setIsPausingForStudent(true);
        const pauseMs = Math.min(25000, Math.max(2000, duration * hifzPauseMultiplier * 1000));
        setTimeout(() => {
          setIsPausingForStudent(false);
          if (audioRef.current) {
            audioRef.current.currentTime = 0;
            audioRef.current.play().catch(console.warn);
          }
        }, pauseMs);
      } else {
        if (audioRef.current) {
          audioRef.current.currentTime = 0;
          audioRef.current.play().catch(console.warn);
        }
      }
      return;
    }

    // SubQueue index (e.g. Arabic recitation followed by Urdu or English audio)
    if (subQueueIndex < currentUrls.length - 1) {
      setSubQueueIndex((prev) => prev + 1);
    } else {
      setHifzRepeatCount(1);

      // Check if advancing to a new Surah boundary (needs Bismillah recitation)
      const nextAyah = ayahs[currentIndex + 1];
      if (
        nextAyah &&
        currentAyah &&
        nextAyah.surah_number !== currentAyah.surah_number &&
        nextAyah.surah_number !== 9 && // No Bismillah for Surah At-Tawbah
        nextAyah.number_in_surah === 1 &&
        nextAyah.surah_number !== 1 // Surah Al-Fatiha has Bismillah as Verse 1
      ) {
        // Trigger opening Bismillah recitation
        setIsPlayingBismillah(true);
        if (audioRef.current) {
          audioRef.current.src = BISMILLAH_AUDIO_URL;
          audioRef.current.play().catch(console.warn);
        }
        return;
      }

      setSubQueueIndex(0);
      onNextAyah();
    }
  };

  const cycleHifzTarget = () => {
    if (hifzRepeatTarget === 1) setHifzRepeatTarget(3);
    else if (hifzRepeatTarget === 3) setHifzRepeatTarget(5);
    else if (hifzRepeatTarget === 5) setHifzRepeatTarget(999);
    else setHifzRepeatTarget(1);
    setHifzRepeatCount(1);
  };

  const cycleHifzPause = () => {
    if (hifzPauseMultiplier === 0) setHifzPauseMultiplier(1.0);
    else if (hifzPauseMultiplier === 1.0) setHifzPauseMultiplier(1.5);
    else setHifzPauseMultiplier(0);
  };

  // Seek on timeline click
  const handleSeek = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!progressBarRef.current || !audioRef.current || duration <= 0) return;
    const rect = progressBarRef.current.getBoundingClientRect();
    const clickPos = Math.max(0, Math.min(e.clientX - rect.left, rect.width));
    const seekPercentage = clickPos / rect.width;
    const targetTime = seekPercentage * duration;
    audioRef.current.currentTime = targetTime;
    setCurrentTime(targetTime);
  };

  // Sync with MediaSession API for lockscreen controls
  useEffect(() => {
    if ("mediaSession" in navigator && currentAyah) {
      navigator.mediaSession.metadata = new MediaMetadata({
        title: `Surah ${currentAyah.surah_name} — Ayah ${currentAyah.number_in_surah}`,
        artist: "Hidayah AI Reciter",
        album: `Juz ${currentAyah.juz || 1}`,
      });

      navigator.mediaSession.setActionHandler("play", onPlayPause);
      navigator.mediaSession.setActionHandler("pause", onPlayPause);
      navigator.mediaSession.setActionHandler("previoustrack", onPrevAyah);
      navigator.mediaSession.setActionHandler("nexttrack", onNextAyah);
    }
  }, [currentAyah, onPlayPause, onNextAyah, onPrevAyah]);

  const toggleSpeed = () => {
    const speeds = [0.75, 1.0, 1.25, 1.5];
    const nextIdx = (speeds.indexOf(playbackSpeed) + 1) % speeds.length;
    const newSpeed = speeds[nextIdx];
    setPlaybackSpeed(newSpeed);
    if (audioRef.current) {
      audioRef.current.playbackRate = newSpeed;
    }
  };

  if (!currentAyah) return null;

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <div className="w-full flex-shrink-0 glass-audio-bar border-t border-[#D4AF37]/25 bg-[#080C14]/95 backdrop-blur-xl relative z-20 pb-2 pt-0">
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onEnded={handleAudioEnded}
      />
      {/* Hidden Lookahead Audio Buffer for Zero-Latency Gapless Pre-loading */}
      <audio
        ref={lookaheadAudioRef}
        style={{ display: "none" }}
        preload="auto"
        tabIndex={-1}
        aria-hidden="true"
      />

      {/* Scrubbable Gold Timeline Progress Bar */}
      <div
        ref={progressBarRef}
        onClick={handleSeek}
        onMouseEnter={() => setIsHoveringProgress(true)}
        onMouseLeave={() => setIsHoveringProgress(false)}
        className="w-full h-1.5 hover:h-2.5 bg-white/[0.08] cursor-pointer relative group transition-all duration-200"
        title="Seek Audio Timeline"
      >
        <div
          className="h-full bg-gradient-to-r from-[#AA8220] via-[#D4AF37] to-[#F3E5AB] relative transition-all duration-100"
          style={{ width: `${progressPercent}%` }}
        >
          {/* Glowing Seek Thumb on Hover */}
          <span
            className={`absolute right-0 top-1/2 -translate-y-1/2 w-3 h-3 rounded-full bg-[#F3E5AB] shadow-lg shadow-[#D4AF37]/50 border border-white transition-opacity ${
              isHoveringProgress ? "opacity-100 scale-110" : "opacity-0"
            }`}
          />
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-3 sm:px-6 pt-2 flex items-center justify-between gap-2 sm:gap-4 h-14 sm:h-16">
        {/* Left: Current Ayah Info */}
        <div className="flex items-center space-x-2 sm:space-x-3 min-w-0 flex-shrink">
          <div className="w-7 h-7 sm:w-8 sm:h-8 rounded-lg bg-gradient-to-br from-[#064E3B] to-[#0A261E] border border-[#D4AF37]/40 flex items-center justify-center text-xs font-bold text-[#D4AF37] shadow-sm flex-shrink-0">
            {isPlayingBismillah ? "﷽" : currentAyah.number_in_surah}
          </div>
          <div className="text-left min-w-0">
            <h4 className="text-xs sm:text-sm font-serif font-bold text-white tracking-wide truncate max-w-[130px] sm:max-w-xs flex items-center gap-1.5">
              {isPlayingBismillah ? (
                <span className="text-[#D4AF37] animate-pulse">Bismillah al-Rahman al-Rahim</span>
              ) : isPausingForStudent ? (
                <span className="text-emerald-400 animate-pulse flex items-center gap-1 text-xs">
                  <span>Student Recitation Pause...</span>
                </span>
              ) : (
                <span>Surah {currentAyah.surah_name}</span>
              )}
            </h4>
            <p className="text-[10px] text-slate-400 font-sans flex items-center gap-1.5 truncate max-w-[150px] sm:max-w-sm">
              {isPlayingBismillah ? (
                <span className="text-[#D4AF37]/90 font-medium">Surah Opening Recitation</span>
              ) : (
                <>
                  <span>Ayah {currentAyah.number_in_surah}</span>
                  <span className="hidden sm:inline">•</span>
                  <span className="text-[#D4AF37]/90 font-medium truncate hidden sm:inline">{reciterLabel}</span>
                  <span>•</span>
                  <span className="font-mono text-slate-500">
                    {formatTime(currentTime)} / {formatTime(duration)}
                  </span>
                </>
              )}
            </p>
          </div>
        </div>

        {/* Center: Recitation Controls */}
        <div className="flex items-center space-x-2 sm:space-x-3.5 flex-shrink-0">
          <button
            onClick={onPrevAyah}
            disabled={currentIndex === 0}
            className="p-1 sm:p-1.5 text-slate-400 hover:text-[#D4AF37] disabled:opacity-20 disabled:hover:text-slate-400 transition-colors duration-150 cursor-pointer disabled:cursor-not-allowed hover:scale-110 active:scale-95"
            aria-label="Previous Ayah"
            title="Previous Ayah"
          >
            <SkipBack className="w-4 h-4" />
          </button>

          <button
            onClick={onPlayPause}
            className="w-9 h-9 sm:w-10 sm:h-10 rounded-full bg-[#D4AF37] hover:bg-[#F3E5AB] text-black flex items-center justify-center shadow-lg shadow-[#D4AF37]/25 transition-all duration-150 hover:scale-105 active:scale-95 cursor-pointer flex-shrink-0"
            aria-label={isPlaying ? "Pause" : "Play"}
            title={isPlaying ? "Pause Recitation" : "Play Recitation"}
          >
            {isPlaying ? (
              <Pause className="w-4 h-4 fill-black" />
            ) : (
              <Play className="w-4 h-4 fill-black translate-x-0.5" />
            )}
          </button>

          <button
            onClick={onNextAyah}
            disabled={currentIndex >= ayahs.length - 1}
            className="p-1 sm:p-1.5 text-slate-400 hover:text-[#D4AF37] disabled:opacity-20 disabled:hover:text-slate-400 transition-colors duration-150 cursor-pointer disabled:cursor-not-allowed hover:scale-110 active:scale-95"
            aria-label="Next Ayah"
            title="Next Ayah"
          >
            <SkipForward className="w-4 h-4" />
          </button>
        </div>

        {/* Right: Hifz Memorization Repetition & Playback Speed */}
        <div className="flex items-center space-x-1.5 sm:space-x-2.5 flex-shrink-0 justify-end">
          {/* Hifz Repeat Stepper (1x / 3x / 5x / ∞) */}
          <button
            onClick={cycleHifzTarget}
            className={`px-2 py-0.5 sm:px-2.5 sm:py-1 rounded-lg text-xs font-semibold flex items-center space-x-1 sm:space-x-1.5 transition-all duration-150 cursor-pointer flex-shrink-0 ${
              hifzRepeatTarget > 1
                ? "bg-[#D4AF37]/25 text-[#D4AF37] border border-[#D4AF37]/50 shadow-sm shadow-[#D4AF37]/20 scale-105"
                : "text-slate-400 hover:text-slate-200 hover:bg-white/[0.05] border border-transparent"
            }`}
            title={`Click to cycle Hifz Memorization repeat: ${
              hifzRepeatTarget === 999
                ? "Continuous Loop"
                : `${hifzRepeatTarget}x per Ayah`
            }`}
          >
            <Repeat className="w-3.5 h-3.5" />
            <span className="text-[10px] font-mono">
              {hifzRepeatTarget === 1
                ? "Hifz 1x"
                : hifzRepeatTarget === 999
                ? "Hifz ∞"
                : `Hifz ${hifzRepeatCount}/${hifzRepeatTarget}`}
            </span>
          </button>

          {/* Student Pause Interval Toggle when Hifz is active */}
          {hifzRepeatTarget > 1 && (
            <button
              onClick={cycleHifzPause}
              className="px-1.5 py-0.5 sm:px-2 sm:py-1 rounded-lg text-[9px] sm:text-[10px] font-mono border border-emerald-500/40 bg-[#064E3B]/30 text-emerald-300 hover:border-emerald-400 cursor-pointer transition-colors flex-shrink-0"
              title="Silent interval after recitation for student to recite from memory"
            >
              {hifzPauseMultiplier === 0 ? "Pause: 0" : `Pause: ${hifzPauseMultiplier}x`}
            </button>
          )}

          {/* Speed Stepper */}
          <button
            onClick={toggleSpeed}
            className="px-1.5 py-0.5 sm:px-2 rounded-md bg-white/5 hover:bg-[#D4AF37]/15 border border-white/10 hover:border-[#D4AF37]/40 text-[10px] sm:text-[11px] font-mono font-bold text-[#D4AF37] transition-all duration-150 cursor-pointer hover:scale-105 active:scale-95 flex-shrink-0"
            title="Click to cycle playback speed (0.75x, 1x, 1.25x, 1.5x)"
          >
            {playbackSpeed}x
          </button>

          {/* Mute Toggle */}
          <button
            onClick={() => {
              if (audioRef.current) {
                audioRef.current.muted = !isMuted;
                setIsMuted(!isMuted);
              }
            }}
            className="p-1 sm:p-1.5 text-slate-400 hover:text-[#D4AF37] transition-colors cursor-pointer rounded-lg hover:bg-white/5 flex-shrink-0"
            title={isMuted ? "Unmute" : "Mute"}
          >
            {isMuted ? (
              <VolumeX className="w-4 h-4 text-rose-400" />
            ) : (
              <Volume2 className="w-4 h-4" />
            )}
          </button>
        </div>
      </div>
    </div>
  );
}

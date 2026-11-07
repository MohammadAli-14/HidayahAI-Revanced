"use client";

import React, { useState, useEffect, useCallback } from "react";
import { Sidebar } from "@/components/navigation/Sidebar";
import { Header } from "@/components/navigation/Header";
import { SearchModal } from "@/components/navigation/SearchModal";
import { DualPaneReader } from "@/components/quran/DualPaneReader";
import { AudioPlayerBar } from "@/components/audio/AudioPlayerBar";
import { VerseContextDrawer } from "@/components/context/VerseContextDrawer";
import { ScholarDrawer } from "@/components/scholar/ScholarDrawer";
import {
  fetchJuzList,
  fetchJuzAyahs,
  fetchSurahs,
  checkGatewayHealth,
  JuzMeta,
  SurahMeta,
  Ayah,
  SURAH_STARTING_JUZ,
} from "@/lib/api";

export default function HomePage() {
  const [juzList, setJuzList] = useState<JuzMeta[]>([]);
  const [surahList, setSurahList] = useState<SurahMeta[]>([]);
  const [currentJuz, setCurrentJuz] = useState<number>(1);
  const [currentAyahs, setCurrentAyahs] = useState<Ayah[]>([]);
  const [currentJuzName, setCurrentJuzName] = useState<string>("Alif Lam Mim");
  const [currentAyahIndex, setCurrentAyahIndex] = useState<number>(0);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const [audioMode, setAudioMode] = useState<string>("Arabic (Mishary Rashid)");
  const [isLoadingJuz, setIsLoadingJuz] = useState<boolean>(false);
  const [isGatewayOffline, setIsGatewayOffline] = useState<boolean>(false);

  const [isSidebarOpen, setIsSidebarOpen] = useState<boolean>(true);
  const [isScholarOpen, setIsScholarOpen] = useState<boolean>(false);
  const [wasSidebarOpenBeforeScholar, setWasSidebarOpenBeforeScholar] = useState<boolean>(true);
  const [isSearchOpen, setIsSearchOpen] = useState<boolean>(false);
  const [activeContextAyah, setActiveContextAyah] = useState<Ayah | null>(null);

  // Set initial responsive sidebar state based on screen width
  useEffect(() => {
    if (typeof window !== "undefined" && window.innerWidth < 1024) {
      setIsSidebarOpen(false);
      setWasSidebarOpenBeforeScholar(false);
    }
  }, []);

  // Clean Predictable Workspace Toggles
  const handleToggleScholar = useCallback(() => {
    setIsScholarOpen((prev) => !prev);
  }, []);

  const handleCloseScholar = useCallback(() => {
    setIsScholarOpen(false);
  }, []);

  const handleToggleSidebar = useCallback(() => {
    setIsSidebarOpen((prev) => !prev);
  }, []);

  // Load Initial Juz Index, Surahs catalog, and URL query parameters
  const init = useCallback(async () => {
    setIsLoadingJuz(true);
    try {
      const [juzs, surahs] = await Promise.all([fetchJuzList(), fetchSurahs()]);
      setJuzList(juzs);
      setSurahList(surahs);

      const params = new URLSearchParams(window.location.search);
      const urlJuz = parseInt(params.get("juz") || "1", 10);
      const urlAyah = parseInt(params.get("ayah") || "0", 10);

      const targetJuz = isNaN(urlJuz) || urlJuz < 1 || urlJuz > 30 ? 1 : urlJuz;
      setCurrentJuz(targetJuz);
      setCurrentAyahIndex(isNaN(urlAyah) ? 0 : urlAyah);

      const data = await fetchJuzAyahs(targetJuz);
      setCurrentAyahs(data.ayahs);
      setCurrentJuzName(data.name);

      if (!data.ayahs || data.ayahs.length === 0) {
        setIsGatewayOffline(true);
      } else {
        setIsGatewayOffline(false);
      }
    } catch {
      setIsGatewayOffline(true);
    } finally {
      setIsLoadingJuz(false);
    }
  }, []);

  useEffect(() => {
    init();
  }, [init]);

  // Gentle auto-reconnect background ping every 4s when gateway is offline
  useEffect(() => {
    if (!isGatewayOffline) return;

    const interval = setInterval(async () => {
      const isOnline = await checkGatewayHealth();
      if (isOnline) {
        setIsGatewayOffline(false);
        init();
      }
    }, 4000);

    return () => clearInterval(interval);
  }, [isGatewayOffline, init]);

  // Fetch new Juz when currentJuz changes
  const handleSelectJuz = useCallback(async (juzId: number, targetAyahIdx: number = 0) => {
    setIsLoadingJuz(true);
    setCurrentJuz(juzId);
    setCurrentAyahIndex(targetAyahIdx);
    setIsPlaying(false);

    const url = new URL(window.location.href);
    url.searchParams.set("juz", juzId.toString());
    url.searchParams.set("ayah", targetAyahIdx.toString());
    window.history.replaceState({}, "", url.toString());

    try {
      const data = await fetchJuzAyahs(juzId);
      setCurrentAyahs(data.ayahs);
      setCurrentJuzName(data.name);

      if (targetAyahIdx > 0) {
        setTimeout(() => {
          const el = document.getElementById(`ayah-${targetAyahIdx}`);
          el?.scrollIntoView({ behavior: "smooth", block: "center" });
        }, 300);
      }
    } finally {
      setIsLoadingJuz(false);
    }
  }, []);

  // Navigate to a specific Surah
  const handleSelectSurah = useCallback(
    async (surahNum: number) => {
      setIsLoadingJuz(true);
      // Find starting Juz of this Surah
      const targetJuz = SURAH_STARTING_JUZ[surahNum] || 1;
      setCurrentJuz(targetJuz);
      setIsPlaying(false);

      try {
        const data = await fetchJuzAyahs(targetJuz);
        setCurrentAyahs(data.ayahs);
        setCurrentJuzName(data.name);

        // Find index of first Ayah of this Surah
        const targetAyahIdx = data.ayahs.findIndex((a) => a.surah_number === surahNum);
        const safeIdx = targetAyahIdx !== -1 ? targetAyahIdx : 0;
        setCurrentAyahIndex(safeIdx);

        const url = new URL(window.location.href);
        url.searchParams.set("juz", targetJuz.toString());
        url.searchParams.set("ayah", safeIdx.toString());
        window.history.replaceState({}, "", url.toString());

        setTimeout(() => {
          const el = document.getElementById(`ayah-${safeIdx}`);
          el?.scrollIntoView({ behavior: "smooth", block: "center" });
        }, 300);
      } finally {
        setIsLoadingJuz(false);
      }
    },
    []
  );

  // Navigate directly to a referenced Surah & Ayah from Scholar AI Citation chips
  const handleNavigateToAyah = useCallback(
    async (surahNum: number, ayahNum: number) => {
      // Check if ayah exists in current juz
      const idx = currentAyahs.findIndex(
        (a) => a.surah_number === surahNum && a.number_in_surah === ayahNum
      );

      if (idx !== -1) {
        setCurrentAyahIndex(idx);
        const el = document.getElementById(`ayah-${idx}`);
        el?.scrollIntoView({ behavior: "smooth", block: "center" });
        return;
      }

      // If not in current Juz, determine its Juz and navigate
      const targetJuz = SURAH_STARTING_JUZ[surahNum] || 1;
      await handleSelectJuz(targetJuz);

      setTimeout(() => {
        const newIdx = currentAyahs.findIndex(
          (a) => a.surah_number === surahNum && a.number_in_surah === ayahNum
        );
        if (newIdx !== -1) {
          setCurrentAyahIndex(newIdx);
          const el = document.getElementById(`ayah-${newIdx}`);
          el?.scrollIntoView({ behavior: "smooth", block: "center" });
        }
      }, 400);
    },
    [currentAyahs, handleSelectJuz]
  );

  // Next Ayah
  const handleNextAyah = useCallback(() => {
    if (currentAyahIndex < currentAyahs.length - 1) {
      const next = currentAyahIndex + 1;
      setCurrentAyahIndex(next);

      const url = new URL(window.location.href);
      url.searchParams.set("ayah", next.toString());
      window.history.replaceState({}, "", url.toString());
    } else if (currentJuz < 30) {
      handleSelectJuz(currentJuz + 1);
    } else {
      setIsPlaying(false);
    }
  }, [currentAyahIndex, currentAyahs.length, currentJuz, handleSelectJuz]);

  // Previous Ayah
  const handlePrevAyah = useCallback(() => {
    if (currentAyahIndex > 0) {
      const prev = currentAyahIndex - 1;
      setCurrentAyahIndex(prev);

      const url = new URL(window.location.href);
      url.searchParams.set("ayah", prev.toString());
      window.history.replaceState({}, "", url.toString());
    }
  }, [currentAyahIndex]);

  // Play Ayah directly from verse row click
  const handlePlayAyah = (index: number) => {
    if (currentAyahIndex === index) {
      setIsPlaying(!isPlaying);
    } else {
      setCurrentAyahIndex(index);
      setIsPlaying(true);
    }
  };

  // Surah summary string for header
  const currentSurah = currentAyahs[currentAyahIndex]?.surah_name || currentAyahs[0]?.surah_name || "";
  const currentSurahNumber = currentAyahs[currentAyahIndex]?.surah_number || currentAyahs[0]?.surah_number;

  const surahSummary =
    currentAyahs.length > 0
      ? `Surah ${currentSurah} • ${currentAyahs.length} Ayahs in this Juz`
      : "";

  return (
    <div className="h-screen w-screen flex bg-[#070A10] text-slate-100 overflow-hidden selection:bg-[#D4AF37]/30 selection:text-white">
      {/* 30 Juz & 114 Surahs Sidebar Workspace */}
      <Sidebar
        juzs={juzList}
        surahs={surahList}
        currentJuz={currentJuz}
        currentSurahNumber={currentSurahNumber}
        onSelectJuz={handleSelectJuz}
        onSelectSurah={handleSelectSurah}
        isOpen={isSidebarOpen}
        onClose={() => setIsSidebarOpen(false)}
      />

      {/* Center Quranic Scripture Workstation */}
      <div className="flex-1 flex flex-col min-w-0 h-full overflow-hidden relative">
        {/* Synchronized Header Horizon (h-16) */}
        <Header
          onToggleSidebar={handleToggleSidebar}
          onToggleScholar={handleToggleScholar}
          onOpenSearch={() => setIsSearchOpen(true)}
          isScholarOpen={isScholarOpen}
          isSidebarOpen={isSidebarOpen}
          juzName={currentJuzName}
          juzId={currentJuz}
          surahSummary={surahSummary}
          audioMode={audioMode}
          onChangeAudioMode={setAudioMode}
          isLoadingJuz={isLoadingJuz}
        />

        {/* Scrollable Sacred Reading Canvas */}
        <main className="flex-1 overflow-y-auto min-h-0">
          <DualPaneReader
            ayahs={currentAyahs}
            currentAyahIndex={currentAyahIndex}
            isPlaying={isPlaying}
            onPlayAyah={handlePlayAyah}
            onOpenContext={(ayah) => setActiveContextAyah(ayah)}
            audioMode={audioMode}
            isLoading={isLoadingJuz}
            isGatewayOffline={isGatewayOffline}
            onRetryConnection={init}
          />
        </main>

        {/* Dedicated Audio Recitation Deck (Pinned to Center Column ONLY) */}
        <AudioPlayerBar
          ayahs={currentAyahs}
          currentIndex={currentAyahIndex}
          isPlaying={isPlaying}
          onPlayPause={() => setIsPlaying(!isPlaying)}
          onNextAyah={handleNextAyah}
          onPrevAyah={handlePrevAyah}
          audioMode={audioMode}
        />
      </div>

      {/* Right Scholar AI Research Column / Sheet */}
      <ScholarDrawer
        isOpen={isScholarOpen}
        onClose={handleCloseScholar}
        onNavigateToAyah={handleNavigateToAyah}
      />

      {/* Contextual Tafseer & Hadith Modal/Drawer */}
      <VerseContextDrawer
        ayah={activeContextAyah}
        onClose={() => setActiveContextAyah(null)}
      />

      {/* Scripture Navigator Modal (Ctrl+K) */}
      <SearchModal
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        juzs={juzList}
        onSelectJuz={handleSelectJuz}
        onSelectSurah={handleSelectSurah}
      />
    </div>
  );
}

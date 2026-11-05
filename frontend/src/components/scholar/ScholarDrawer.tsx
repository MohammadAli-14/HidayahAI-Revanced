"use client";

import React, { useState, useRef, useEffect } from "react";
import {
  X,
  Send,
  Sparkles,
  FileText,
  Upload,
  ExternalLink,
  Bot,
  User,
  BookOpen,
  Cpu,
  BookCheck,
  ChevronDown,
  Maximize2,
  Minimize2,
} from "lucide-react";
import { ScholarSource, FiqhMatrix, API_BASE, DIRECT_BACKEND_URL } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "scholar";
  content: string;
  intent?: string;
  sources?: ScholarSource[];
  fiqh_matrix?: FiqhMatrix | null;
  isStreaming?: boolean;
  progressStep?: string;
}

interface ScholarDrawerProps {
  isOpen: boolean;
  onClose: () => void;
  onNavigateToAyah?: (surah: number, ayah: number) => void;
}

const SAMPLE_PROMPTS = [
  "Explain Asbab al-Nuzul of Surah Al-Baqarah 183",
  "Is the hadith about seeking knowledge in China authentic?",
  "Compare the 4 Sunni Madhhab positions on Raf' al-Yadayn",
  "Statutory inheritance shares in Surah An-Nisa 4:11-12",
];

// Helper to render text with bold tags and clickable scripture citations
function renderLineWithFormatting(
  text: string,
  onNavigateToAyah?: (surah: number, ayah: number) => void
) {
  const regex = /(\*\*[^*]+\*\*|\[(?:Q\s*|Q-|Surah\s*)?(\d{1,3}):(\d{1,3})\])/g;
  const parts: React.ReactNode[] = [];
  let lastIndex = 0;
  let match;

  while ((match = regex.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(text.substring(lastIndex, match.index));
    }

    const matchedStr = match[0];
    if (matchedStr.startsWith("**") && matchedStr.endsWith("**")) {
      parts.push(
        <strong key={`bold-${match.index}`} className="font-semibold text-white">
          {matchedStr.slice(2, -2)}
        </strong>
      );
    } else if (match[2] && match[3]) {
      const surahNum = parseInt(match[2], 10);
      const ayahNum = parseInt(match[3], 10);
      parts.push(
        <button
          key={`cite-${match.index}-${surahNum}-${ayahNum}`}
          onClick={() => onNavigateToAyah?.(surahNum, ayahNum)}
          className="inline-flex items-center space-x-0.5 px-1.5 py-0.5 mx-1 rounded-md bg-[#D4AF37]/20 hover:bg-[#D4AF37] text-[#D4AF37] hover:text-black border border-[#D4AF37]/40 font-mono text-[11px] font-semibold transition-all duration-150 cursor-pointer shadow-sm align-baseline group"
          title={`Jump directly to Surah ${surahNum}, Ayah ${ayahNum} in Reader`}
        >
          <BookOpen className="w-2.5 h-2.5 inline mr-0.5 text-[#D4AF37] group-hover:text-black" />
          <span>{surahNum}:{ayahNum}</span>
        </button>
      );
    }

    lastIndex = regex.lastIndex;
  }

  if (lastIndex < text.length) {
    parts.push(text.substring(lastIndex));
  }

  return parts;
}

// Rich Formatted Message Text with markdown headers, bold, bullets, and citation jumps
function FormattedMessageText({
  content,
  onNavigateToAyah,
}: {
  content: string;
  onNavigateToAyah?: (surah: number, ayah: number) => void;
}) {
  if (!content) return null;

  const lines = content.split("\n");

  return (
    <div className="space-y-2 text-xs sm:text-sm leading-relaxed">
      {lines.map((line, lineIdx) => {
        const trimmed = line.trim();
        if (!trimmed) return <div key={lineIdx} className="h-1" />;

        const isH3 = trimmed.startsWith("### ");
        const isH2 = trimmed.startsWith("## ");
        const isBullet = trimmed.startsWith("- ") || trimmed.startsWith("• ") || trimmed.startsWith("* ");

        const cleanLine = isH3
          ? trimmed.slice(4)
          : isH2
          ? trimmed.slice(3)
          : isBullet
          ? trimmed.slice(2)
          : line;

        const renderedContent = renderLineWithFormatting(cleanLine, onNavigateToAyah);

        if (isH2) {
          return (
            <h4
              key={lineIdx}
              className="text-sm font-serif font-bold text-[#D4AF37] mt-3 pb-1 border-b border-white/10"
            >
              {renderedContent}
            </h4>
          );
        }

        if (isH3) {
          return (
            <h5 key={lineIdx} className="text-xs font-serif font-bold text-emerald-300 mt-2">
              {renderedContent}
            </h5>
          );
        }

        if (isBullet) {
          return (
            <div key={lineIdx} className="flex items-start space-x-2 pl-2">
              <span className="text-[#D4AF37] font-bold leading-normal">•</span>
              <span className="flex-1">{renderedContent}</span>
            </div>
          );
        }

        return (
          <p key={lineIdx} className="leading-relaxed">
            {renderedContent}
          </p>
        );
      })}
    </div>
  );
}

// Collapsible Sources Component: Collapsed by default to keep answers 100% visible
function CollapsibleSources({
  sources,
  onNavigateToAyah,
}: {
  sources?: ScholarSource[];
  onNavigateToAyah?: (surah: number, ayah: number) => void;
}) {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!sources || sources.length === 0) return null;

  return (
    <div className="mt-3 pt-2.5 border-t border-white/10 space-y-2">
      {/* Accordion Toggle Bar */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="w-full flex items-center justify-between p-2 rounded-xl bg-black/40 hover:bg-[#D4AF37]/10 border border-[#D4AF37]/30 hover:border-[#D4AF37]/60 transition-all cursor-pointer group shadow-sm"
      >
        <div className="flex items-center space-x-2">
          <BookCheck className="w-3.5 h-3.5 text-[#D4AF37] group-hover:scale-110 transition-transform flex-shrink-0" />
          <span className="text-[11px] font-bold text-slate-200 group-hover:text-[#D4AF37] tracking-wide">
            Authenticated Evidence & Sources
          </span>
          <span className="px-1.5 py-0.2 rounded-full bg-emerald-950/80 border border-emerald-600/40 text-[9px] font-bold text-emerald-300 font-mono">
            {sources.length} Canonical
          </span>
        </div>
        <div className="flex items-center space-x-1 text-slate-400 group-hover:text-[#D4AF37]">
          <span className="text-[10px] font-sans font-medium">
            {isExpanded ? "Hide" : "Show All"}
          </span>
          <ChevronDown
            className={`w-3.5 h-3.5 transition-transform duration-200 ${
              isExpanded ? "rotate-180 text-[#D4AF37]" : ""
            }`}
          />
        </div>
      </button>

      {/* When Collapsed: Compact preview row of top 3 citations with direct jump */}
      {!isExpanded && (
        <div className="flex flex-wrap gap-1 px-1">
          {sources.slice(0, 3).map((s, idx) => {
            const match = s.label.match(/\((\d{1,3}):(\d{1,3})\)/);
            const surah = match ? parseInt(match[1], 10) : null;
            const ayah = match ? parseInt(match[2], 10) : null;
            const shortLabel = s.label.split("|")[0].trim().replace(/canonical:verified/g, "").trim();

            return (
              <span
                key={idx}
                className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md bg-white/[0.04] border border-white/10 text-[10px] text-slate-300"
              >
                <span className="truncate max-w-[190px]">{shortLabel}</span>
                {surah && ayah && onNavigateToAyah && (
                  <button
                    onClick={() => onNavigateToAyah(surah, ayah)}
                    className="text-[#D4AF37] hover:underline cursor-pointer ml-0.5 font-mono text-[9px] font-semibold"
                    title={`Jump to ${surah}:${ayah}`}
                  >
                    [Jump ↗]
                  </button>
                )}
              </span>
            );
          })}
          {sources.length > 3 && (
            <span
              onClick={() => setIsExpanded(true)}
              className="text-[10px] text-[#D4AF37]/80 hover:text-[#D4AF37] hover:underline cursor-pointer self-center ml-1"
            >
              +{sources.length - 3} more
            </span>
          )}
        </div>
      )}

      {/* When Expanded: Full Detailed Verified Evidence List */}
      {isExpanded && (
        <div className="space-y-1.5 animate-in fade-in duration-200 max-h-56 overflow-y-auto overscroll-contain pr-1">
          {sources.map((s, idx) => {
            const match = s.label.match(/\((\d{1,3}):(\d{1,3})\)/);
            const surah = match ? parseInt(match[1], 10) : null;
            const ayah = match ? parseInt(match[2], 10) : null;

            return (
              <div
                key={idx}
                className="p-2 rounded-lg bg-black/50 border border-white/[0.08] hover:border-[#D4AF37]/40 transition-colors flex items-center justify-between text-[11px]"
              >
                <div className="truncate pr-2">
                  <span className="text-slate-200 font-mono leading-relaxed select-text">
                    {s.label.replace(/canonical:verified/g, "").trim()}
                  </span>
                </div>
                <div className="flex items-center space-x-1.5 flex-shrink-0">
                  {surah && ayah && onNavigateToAyah && (
                    <button
                      onClick={() => onNavigateToAyah(surah, ayah)}
                      className="px-1.5 py-0.5 rounded bg-[#D4AF37]/20 hover:bg-[#D4AF37] text-[#D4AF37] hover:text-black font-semibold text-[10px] transition-colors cursor-pointer flex items-center gap-0.5"
                      title={`Jump to Surah ${surah}, Ayah ${ayah} in Reader`}
                    >
                      <BookOpen className="w-2.5 h-2.5" />
                      <span>{surah}:{ayah}</span>
                    </button>
                  )}
                  {s.url && (
                    <a
                      href={s.url}
                      target="_blank"
                      rel="noreferrer"
                      className="p-1 rounded bg-white/5 hover:bg-[#D4AF37]/20 text-[#D4AF37] transition-colors cursor-pointer"
                      title="Open source documentation"
                    >
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}

export function ScholarDrawer({
  isOpen,
  onClose,
  onNavigateToAyah,
}: ScholarDrawerProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "scholar",
      content:
        "Assalamu Alaikum. I am Hidayah AI, an Islamic scholarly research companion. Ask me about Quranic exegesis (Tafseer), Hadith authentication (Takhrīj), comparative jurisprudence (Ikhtilaf), or upload scholarly PDFs.",
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [activePdf, setActivePdf] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [selectedModel, setSelectedModel] = useState<"gemini" | "ollama">("gemini");
  const [gatewayStatus, setGatewayStatus] = useState<"checking" | "online" | "offline">("checking");
  const [isOllamaOnline, setIsOllamaOnline] = useState<boolean | null>(null);
  const [isMaximized, setIsMaximized] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);
  const messagesContainerRef = useRef<HTMLDivElement | null>(null);
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [userIsScrolledUp, setUserIsScrolledUp] = useState(false);

  // Monitor user scroll position to avoid jerking view during active reading
  const handleMessagesScroll = () => {
    if (!messagesContainerRef.current) return;
    const { scrollTop, scrollHeight, clientHeight } = messagesContainerRef.current;
    const isScrolledUp = scrollHeight - scrollTop - clientHeight > 100;
    setUserIsScrolledUp(isScrolledUp);
  };

  // Monitor FastAPI Theological Gateway Connectivity (Port 8001) & Ollama
  useEffect(() => {
    let isMounted = true;
    const checkGateway = async () => {
      try {
        const res = await fetch(`${API_BASE}/health`, { method: "GET" });
        if (isMounted) {
          setGatewayStatus(res.ok ? "online" : "offline");
        }
      } catch {
        if (isMounted) {
          setGatewayStatus("offline");
        }
      }

      try {
        const ollamaRes = await fetch(`${API_BASE}/scholar/ollama-status`, { method: "GET" });
        if (ollamaRes.ok) {
          const data = await ollamaRes.json();
          if (isMounted) {
            setIsOllamaOnline(data.online === true);
          }
        } else {
          if (isMounted) setIsOllamaOnline(false);
        }
      } catch {
        if (isMounted) setIsOllamaOnline(false);
      }
    };
    checkGateway();
    const timer = setInterval(checkGateway, 15000);
    return () => {
      isMounted = false;
      clearInterval(timer);
    };
  }, []);

  useEffect(() => {
    if (!userIsScrolledUp) {
      messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, userIsScrolledUp]);

  // Send message with SSE streaming
  const handleSendMessage = async (textToSend?: string) => {
    const query = textToSend || inputValue;
    if (!query.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: "user",
      content: query,
    };

    const botMessageId = (Date.now() + 1).toString();
    const botMessage: Message = {
      id: botMessageId,
      role: "scholar",
      content: "",
      isStreaming: true,
      progressStep: selectedModel === "ollama" ? "Loading local HidayahLM 3B & searching corpus..." : "Authenticating Hadith & Quran corpus...",
      sources: [],
    };

    setMessages((prev) => [...prev, userMessage, botMessage]);
    setInputValue("");
    setIsLoading(true);
    setUserIsScrolledUp(false);

    try {
      const payload = {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          query,
          active_pdf_name: activePdf,
          use_local_llm: selectedModel === "ollama",
        }),
      };

      let response: Response;
      const targetEndpoint = API_BASE.startsWith("http")
        ? `${API_BASE}/scholar/stream`
        : `${DIRECT_BACKEND_URL}/scholar/stream`;

      try {
        response = await fetch(targetEndpoint, payload);
        if (!response.ok && targetEndpoint !== `${API_BASE}/scholar/stream`) {
          response = await fetch(`${API_BASE}/scholar/stream`, payload);
        }
      } catch {
        response = await fetch(`${DIRECT_BACKEND_URL}/scholar/stream`, payload);
      }

      if (!response.ok || !response.body) {
        throw new Error("Failed to connect to Scholar stream");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder("utf-8");
      let buffer = "";

      while (true) {
        const { value, done } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split(/\r?\n\r?\n/);
        buffer = lines.pop() || "";

        for (const line of lines) {
          if (!line.trim() || line.trim().startsWith(":")) continue;

          let eventType = "message";
          let dataStr = "";

          for (const rawLine of line.split(/\r?\n/)) {
            const trimmed = rawLine.trim();
            if (trimmed.startsWith("event: ")) {
              eventType = trimmed.replace("event: ", "").trim();
            } else if (trimmed.startsWith("data: ")) {
              dataStr = trimmed.replace("data: ", "").trim();
            }
          }

          if (dataStr) {
            try {
              const parsed = JSON.parse(dataStr);

              if (eventType === "meta") {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === botMessageId
                      ? { ...msg, intent: parsed.intent }
                      : msg
                  )
                );
              } else if (eventType === "progress") {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === botMessageId
                      ? { ...msg, progressStep: parsed.step }
                      : msg
                  )
                );
              } else if (eventType === "fiqh_matrix") {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === botMessageId
                      ? { ...msg, fiqh_matrix: parsed.fiqh_matrix || null }
                      : msg
                  )
                );
              } else if (eventType === "sources") {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === botMessageId
                      ? { ...msg, sources: parsed.sources || [] }
                      : msg
                  )
                );
              } else if (eventType === "token") {
                setMessages((prev) =>
                  prev.map((msg) =>
                    msg.id === botMessageId
                      ? { ...msg, content: msg.content + parsed.token }
                      : msg
                  )
                );
              } else if (eventType === "done") {
                setMessages((prev) =>
                  prev.map((msg) => {
                    if (msg.id !== botMessageId) return msg;
                    const finalContent =
                      msg.content && msg.content.trim().length > 0
                        ? msg.content
                        : "⚠️ The scholar model was unable to stream content. If you selected HidayahLM (Local), ensure Ollama is running (`ollama serve`), or switch to Gemini 2.5 Flash.";
                    return { ...msg, content: finalContent, isStreaming: false };
                  })
                );
              }
            } catch (err) {
              console.warn("SSE parse error:", err);
            }
          }
        }
      }
    } catch (err) {
      console.warn("Scholar stream unavailable:", err);
      setMessages((prev) =>
        prev.map((msg) =>
          msg.id === botMessageId
            ? {
                ...msg,
                content:
                  "⚠️ Unable to reach the Scholar Agent: The backend gateway is offline (Port 8001).\n\nPlease start the theological gateway by running `python run_platform.py` or `.\\run.ps1` in your project terminal and try again.",
                isStreaming: false,
              }
            : msg
        )
      );
    } finally {
      setIsLoading(false);
    }
  };

  // Handle PDF upload into LanceDB
  const handlePdfUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/rag/upload`, {
        method: "POST",
        body: formData,
      });

      if (!res.ok) throw new Error("Upload failed");
      const data = await res.json();
      setActivePdf(file.name);

      setMessages((prev) => [
        ...prev,
        {
          id: Date.now().toString(),
          role: "scholar",
          content: `📄 **Document Indexed Successfully:** \`${file.name}\` has been processed into LanceDB (${data.chunks_indexed} semantic chunks). You can now ask specific research questions about this text.`,
        },
      ]);
    } catch (err) {
      console.error("PDF upload error:", err);
      alert("Failed to process and index PDF. Please check file format.");
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Mobile Backdrop only on small screens (<1024px) */}
      <div
        onClick={onClose}
        className="fixed inset-0 z-30 bg-black/70 backdrop-blur-sm lg:hidden transition-opacity cursor-pointer"
      />

      {/* Full-Height Dedicated Research Column: in-flow flex child on desktop, slide-over on mobile */}
      <aside
        className={`fixed lg:relative inset-y-0 right-0 z-40 lg:z-10 h-full flex flex-col bg-[#0A0E17] border-l border-[#D4AF37]/20 shadow-2xl transition-all duration-300 ease-in-out flex-shrink-0 ${
          isOpen
            ? isMaximized
              ? "translate-x-0 w-full lg:w-[65vw] xl:w-[60vw]"
              : "translate-x-0 w-full sm:w-[440px] xl:w-[480px]"
            : "translate-x-full lg:translate-x-0 lg:w-0 lg:opacity-0 lg:overflow-hidden lg:pointer-events-none lg:border-l-0"
        }`}
      >
        {/* Drawer Header: Standardized to h-16 to match App Header baseline */}
        <div className="h-16 flex-shrink-0 px-3.5 sm:px-4 border-b border-white/[0.08] flex items-center justify-between bg-black/40">
          <div className="flex items-center space-x-2.5 min-w-0">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[#064E3B] to-[#0A261E] border border-[#D4AF37]/50 flex items-center justify-center shadow-md flex-shrink-0">
              <Sparkles className="w-4 h-4 text-[#D4AF37]" />
            </div>
            <div className="min-w-0">
              <div className="flex items-center space-x-2">
                <h3 className="text-xs sm:text-sm font-serif font-bold text-white tracking-wide truncate">
                  Scholar AI Copilot
                </h3>
                {gatewayStatus === "online" ? (
                  <span
                    className="flex items-center space-x-1 px-1.5 py-0.5 rounded bg-emerald-950/80 border border-emerald-600/40 text-[9px] font-bold text-emerald-300 uppercase flex-shrink-0"
                    title="Theological Gateway Connected (Port 8001)"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
                    Grounded
                  </span>
                ) : gatewayStatus === "checking" ? (
                  <span
                    className="flex items-center space-x-1 px-1.5 py-0.5 rounded bg-slate-900 border border-slate-700 text-[9px] font-bold text-slate-400 uppercase flex-shrink-0"
                    title="Checking gateway status..."
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-slate-400 animate-ping" />
                    Connecting
                  </span>
                ) : (
                  <span
                    className="flex items-center space-x-1 px-1.5 py-0.5 rounded bg-amber-950/80 border border-amber-600/40 text-[9px] font-bold text-amber-300 uppercase flex-shrink-0"
                    title="Gateway offline on port 8001. Start via python run_platform.py"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-amber-400" />
                    Offline
                  </span>
                )}
              </div>
              <p className="text-[10px] text-slate-400 font-sans truncate">
                Usul al-Fiqh & Canonical Hadiths
              </p>
            </div>
          </div>

          {/* Action Icons */}
          <div className="flex items-center space-x-1 sm:space-x-1.5 flex-shrink-0">
            <input
              type="file"
              ref={fileInputRef}
              accept=".pdf"
              onChange={handlePdfUpload}
              className="hidden"
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className="p-1.5 rounded-lg hover:bg-white/5 text-slate-400 hover:text-[#D4AF37] transition-all cursor-pointer hover:scale-105 active:scale-95"
              title="Upload PDF to LanceDB Knowledge Base"
            >
              <Upload className="w-4 h-4" />
            </button>

            {/* Maximize / Restore Toggle (Desktop) */}
            <button
              onClick={() => setIsMaximized(!isMaximized)}
              className="p-1.5 rounded-lg hover:bg-white/5 text-slate-400 hover:text-[#D4AF37] transition-all cursor-pointer hidden sm:flex items-center justify-center hover:scale-105 active:scale-95"
              title={
                isMaximized
                  ? "Restore Standard Width (480px)"
                  : "Maximize to Wide Research Mode (60% Screen Width)"
              }
              aria-label={isMaximized ? "Restore Width" : "Maximize Drawer"}
            >
              {isMaximized ? (
                <Minimize2 className="w-4 h-4 text-[#D4AF37]" />
              ) : (
                <Maximize2 className="w-4 h-4" />
              )}
            </button>

            <button
              onClick={onClose}
              className="p-1.5 rounded-lg hover:bg-white/5 text-slate-400 hover:text-white transition-all cursor-pointer hover:scale-105 active:scale-95"
              aria-label="Close Scholar Drawer"
              title="Close Panel"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Dedicated Model Engine Selector Bar: 100% visible, zero truncation */}
        <div className="px-3.5 sm:px-4 py-2 bg-black/40 border-b border-white/[0.06] flex items-center justify-between text-xs flex-shrink-0">
          <div className="flex items-center space-x-1.5 text-[11px] text-slate-400">
            <Cpu className="w-3.5 h-3.5 text-[#D4AF37]" />
            <span className="font-medium">Inference Engine:</span>
          </div>
          <div className="flex items-center space-x-1.5 p-0.5 rounded-lg bg-black/60 border border-white/10 text-[10px]">
            <button
              onClick={() => setSelectedModel("gemini")}
              className={`px-2.5 py-1 rounded-md transition-all flex items-center space-x-1.5 cursor-pointer ${
                selectedModel === "gemini"
                  ? "bg-[#D4AF37]/20 text-[#D4AF37] border border-[#D4AF37]/40 font-semibold shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
              title="Google Gemini 2.5 Flash (Ultra-fast cloud inference)"
            >
              <Sparkles className="w-3 h-3 text-[#D4AF37]" />
              <span>Gemini 2.5 Flash</span>
            </button>
            <button
              onClick={() => setSelectedModel("ollama")}
              className={`px-2.5 py-1 rounded-md transition-all flex items-center space-x-1.5 cursor-pointer ${
                selectedModel === "ollama"
                  ? "bg-emerald-950/80 text-emerald-300 border border-emerald-500/40 font-semibold shadow-sm"
                  : "text-slate-400 hover:text-slate-200"
              }`}
              title={
                isOllamaOnline === false
                  ? "HidayahLM 3B (Ollama offline on port 11434 — queries will failover to Gemini)"
                  : "Fine-tuned HidayahLM 3B running locally via Ollama (100% Private & Offline)"
              }
            >
              <BookOpen className="w-3 h-3 text-emerald-400" />
              <span>HidayahLM 3B</span>
              {isOllamaOnline === false && (
                <span className="text-[8px] px-1.5 py-0.2 rounded bg-amber-950/80 text-amber-300 border border-amber-600/30 font-mono">
                  Offline
                </span>
              )}
              {isOllamaOnline === true && (
                <span className="text-[8px] px-1.5 py-0.2 rounded bg-emerald-900/60 text-emerald-300 border border-emerald-600/30 font-mono">
                  Ready
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Gateway Offline Notice Banner */}
        {gatewayStatus === "offline" && (
          <div className="mx-3.5 mt-2.5 p-2.5 rounded-xl bg-amber-950/40 border border-amber-500/30 text-amber-200 text-xs flex items-start gap-2 animate-in fade-in duration-200">
            <span className="text-amber-400 font-bold mt-0.5">⚠️</span>
            <div className="text-[11px] leading-relaxed">
              <span className="font-semibold text-white">Theological Gateway (Port 8001) is offline.</span>
              <p className="text-amber-300/80 mt-0.5">
                Run <code className="px-1 py-0.5 rounded bg-black/60 text-[#D4AF37] font-mono">python run_platform.py</code> or <code className="px-1 py-0.5 rounded bg-black/60 text-[#D4AF37] font-mono">.\run.ps1</code> in your terminal to activate the AI Scholar backend.
              </p>
            </div>
          </div>
        )}

        {/* Active PDF Indicator */}
        {activePdf && (
          <div className="px-4 py-2 bg-[#D4AF37]/10 border-b border-[#D4AF37]/20 flex items-center justify-between text-xs">
            <span className="flex items-center space-x-1.5 text-[#D4AF37] truncate">
              <FileText className="w-3.5 h-3.5 flex-shrink-0" />
              <span className="truncate">Active PDF: {activePdf}</span>
            </span>
            <button
              onClick={() => setActivePdf(null)}
              className="text-slate-400 hover:text-white ml-2 text-[10px] cursor-pointer hover:underline"
            >
              Clear
            </button>
          </div>
        )}

        {/* Messages Feed */}
        <div
          ref={messagesContainerRef}
          onScroll={handleMessagesScroll}
          className="flex-1 overflow-y-auto overscroll-contain p-3.5 xl:p-4 space-y-3.5"
        >
          {messages.map((msg) => (
            <div
              key={msg.id}
              className={`flex flex-col space-y-1 ${
                msg.role === "user" ? "items-end" : "items-start"
              }`}
            >
              <div className="flex items-center space-x-1.5 text-[10px] text-slate-400 px-1">
                {msg.role === "user" ? (
                  <>
                    <span>Researcher</span>
                    <User className="w-3 h-3 text-slate-400" />
                  </>
                ) : (
                  <>
                    <Bot className="w-3 h-3 text-[#D4AF37]" />
                    <span>AI Scholar</span>
                    {msg.intent && (
                      <span className="ml-1 px-1.5 py-0.2 rounded bg-white/5 border border-white/10 text-[9px] text-[#D4AF37] font-mono">
                        {msg.intent}
                      </span>
                    )}
                  </>
                )}
              </div>

              <div
                className={`p-3.5 rounded-xl text-xs sm:text-sm leading-relaxed max-w-[92%] whitespace-pre-wrap ${
                  msg.role === "user"
                    ? "bg-[#D4AF37]/20 border border-[#D4AF37]/40 text-slate-100 rounded-tr-none shadow-sm"
                    : "glass-panel text-slate-200 rounded-tl-none border-white/[0.08]"
                }`}
              >
                {msg.isStreaming && !msg.content && (
                  <div className="p-3 my-1 rounded-xl bg-black/40 border border-[#D4AF37]/30 shadow-inner flex items-start space-x-2.5">
                    <div className="w-6 h-6 rounded-lg bg-emerald-950/80 border border-emerald-500/40 flex items-center justify-center flex-shrink-0 mt-0.5 shadow-sm">
                      <Cpu className="w-3.5 h-3.5 text-emerald-300 animate-pulse" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <span className="text-[10px] font-mono uppercase font-bold text-emerald-300 tracking-wider">
                          Active Inference
                        </span>
                        <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping" />
                      </div>
                      <p className="text-xs text-slate-200 font-sans mt-0.5 leading-snug">
                        {msg.progressStep || "Consulting canonical Hadith & Quranic exegesis..."}
                      </p>
                    </div>
                  </div>
                )}

                <FormattedMessageText
                  content={msg.content}
                  onNavigateToAyah={onNavigateToAyah}
                />

                {msg.isStreaming && msg.content && (
                  <span className="inline-block w-1.5 h-3.5 ml-1 bg-[#D4AF37] animate-pulse align-middle" />
                )}

                {/* Collapsible Authenticated Evidence & Sources */}
                <CollapsibleSources
                  sources={msg.sources}
                  onNavigateToAyah={onNavigateToAyah}
                />

                {/* 4-Madhhab Comparative Fiqh Matrix Card */}
                {msg.fiqh_matrix && (
                  <div className="mt-3 p-3.5 rounded-xl bg-black/40 border border-[#D4AF37]/40 shadow-lg space-y-2.5">
                    <div className="flex items-center justify-between border-b border-white/[0.08] pb-2">
                      <div className="flex items-center space-x-1.5">
                        <span className="text-xs">⚖️</span>
                        <h5 className="text-xs font-serif font-bold text-[#D4AF37]">
                          4-Madhhab Comparative Jurisprudence (Fiqh al-Muqāran)
                        </h5>
                      </div>
                      <span className="text-[9px] uppercase font-mono px-1.5 py-0.5 rounded bg-[#064E3B]/80 text-[#D4AF37] border border-[#D4AF37]/30">
                        Canonical Matrix
                      </span>
                    </div>

                    <p className="text-[11px] text-slate-300 font-sans leading-relaxed">
                      <strong className="text-[#D4AF37]">Consensus (Ijmāʿ): </strong>
                      {msg.fiqh_matrix.classical_consensus}
                    </p>

                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 pt-1">
                      {Object.entries(msg.fiqh_matrix.schools).map(([school, sData]) => (
                        <div
                          key={school}
                          className="p-2.5 rounded-lg bg-white/[0.03] border border-white/[0.06] hover:border-[#D4AF37]/30 transition-colors space-y-1"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-[11px] font-bold text-emerald-300 font-serif">
                              {school} School
                            </span>
                            <span className="text-[9px] text-slate-500 font-mono">Madhhab</span>
                          </div>
                          <p className="text-[11px] text-slate-200 font-sans leading-snug">
                            {sData.ruling}
                          </p>
                          <p className="text-[10px] text-slate-400 font-mono line-clamp-2" title={sData.proofs}>
                            <span className="text-[#D4AF37]">Dalil: </span>
                            {sData.proofs}
                          </p>
                        </div>
                      ))}
                    </div>

                    {msg.fiqh_matrix.adab_note && (
                      <p className="text-[10px] text-slate-400 italic pt-1 border-t border-white/[0.06]">
                        <strong className="text-slate-300">Adab al-Ikhtilāf: </strong>
                        {msg.fiqh_matrix.adab_note}
                      </p>
                    )}
                  </div>
                )}
              </div>
            </div>
          ))}

          {/* Quick Prompts */}
          {messages.length === 1 && (
            <div className="pt-3 space-y-2">
              <p className="text-[10px] font-bold tracking-wider uppercase text-slate-400 px-1">
                Suggested Research Inquiries
              </p>
              <div className="grid grid-cols-1 gap-1.5">
                {SAMPLE_PROMPTS.map((p, idx) => (
                  <button
                    key={idx}
                    onClick={() => handleSendMessage(p)}
                    className="p-2.5 text-left rounded-xl bg-white/[0.03] hover:bg-[#D4AF37]/10 border border-white/[0.05] hover:border-[#D4AF37]/40 text-xs text-slate-300 hover:text-white transition-all duration-200 cursor-pointer hover:scale-[1.01] active:scale-[0.99] shadow-sm"
                  >
                    {p}
                  </button>
                ))}
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input Bar */}
        <div className="p-3.5 sm:p-4 border-t border-white/[0.08] bg-black/50 backdrop-blur-md">
          <form
            onSubmit={(e) => {
              e.preventDefault();
              handleSendMessage();
            }}
            className="flex items-center space-x-2"
          >
            <input
              type="text"
              placeholder="Ask a scholarly question or enter Hadith coordinate..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              disabled={isLoading}
              className="flex-1 bg-black/50 border border-white/10 rounded-xl px-3 py-2 text-xs sm:text-sm text-slate-200 placeholder-slate-500 focus:outline-none focus:border-[#D4AF37]/70 transition-colors"
            />
            <button
              type="submit"
              disabled={!inputValue.trim() || isLoading}
              className="p-2 rounded-xl bg-[#D4AF37] text-black hover:bg-[#F3E5AB] disabled:opacity-30 disabled:hover:bg-[#D4AF37] transition-all duration-200 cursor-pointer disabled:cursor-not-allowed hover:scale-105 active:scale-95 shadow-md shadow-[#D4AF37]/20"
              aria-label="Send Query"
              title="Send Inquiry"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>

          <p className="text-[9px] text-center text-slate-500 mt-2">
            Hidayah AI provides academic research assistance. For personal binding verdicts, consult qualified human jurists.
          </p>
        </div>
      </aside>
    </>
  );
}

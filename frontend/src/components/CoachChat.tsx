import { useEffect, useRef, useState } from "react";
import { Send, Lightbulb, Search, BarChart2, Loader2, Cpu } from "lucide-react";
import clsx from "clsx";
import type { UseCoachReturn, CoachMessage } from "../hooks/useCoach";
import type { GameState } from "../types/chess";
import { motion, AnimatePresence } from "framer-motion";

interface CoachChatProps {
  coachHook: UseCoachReturn;
  gameState: GameState;
  moveHistoryUci: string[];
}

export default function CoachChat({ coachHook, gameState, moveHistoryUci }: CoachChatProps) {
  const { messages, isLoading, getHint, explainLastMove, getPostgameAnalysis, sendChatMessage } =
    coachHook;
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [messages.length]);

  const handleHint = () => {
    getHint(gameState.fen, "white", moveHistoryUci, gameState.difficulty);
  };

  const handleExplain = () => {
    if (!gameState.lastAiMove || !gameState.lastAiMoveSan) return;
    explainLastMove(
      gameState.fen,
      gameState.lastAiMove,
      gameState.lastAiMoveSan,
      moveHistoryUci,
      gameState.difficulty
    );
  };

  const handlePostGame = () => {
    if (!gameState.pgn) return;
    const result = gameState.isCheckmate
      ? gameState.turn === "white" ? "black_wins" : "white_wins"
      : "unknown";
    getPostgameAnalysis(gameState.pgn, gameState.difficulty, "white", result);
  };

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;
    sendChatMessage(inputValue.trim(), gameState.fen, moveHistoryUci);
    setInputValue("");
  };

  return (
    <div className="flex flex-col h-full min-h-0 bg-transparent">
      {/* Header Info */}
      <div className="flex items-center justify-between mb-2 px-1">
        <div className="flex items-center gap-1.5">
          <Cpu size={12} className="text-neon-cyan" />
          <h2 className="font-tech text-[9px] tracking-[0.2em] text-neon-cyan uppercase">AI Strategic Core</h2>
        </div>
        <div className="text-[8px] font-tech text-neon-cyan/40 tracking-wider">SECURE // 0xCC1</div>
      </div>

      {/* Quick actions */}
      <div className="grid grid-cols-3 gap-1.5 mb-2">
        <QuickActionButton
          icon={<Lightbulb size={10} />}
          label="HINT"
          onClick={handleHint}
          disabled={isLoading || gameState.isGameOver || gameState.isThinking}
        />
        <QuickActionButton
          icon={<Search size={10} />}
          label="WHY?"
          onClick={handleExplain}
          disabled={isLoading || !gameState.lastAiMove}
        />
        <QuickActionButton
          icon={<BarChart2 size={10} />}
          label="REPORT"
          onClick={handlePostGame}
          disabled={isLoading || !gameState.isGameOver}
        />
      </div>

      {/* Messages */}
      <div className="flex-1 min-h-0 overflow-y-auto space-y-3 mb-2 pr-1 scrollbar-thin scrollbar-thumb-neon-cyan/20 scrollbar-track-transparent">
        <AnimatePresence initial={false}>
          {messages.map((message) => (
            <MessagePacket key={message.id} message={message} />
          ))}
        </AnimatePresence>

        {isLoading && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="flex items-center gap-3 px-3 py-2 text-neon-cyan/60"
          >
            <Loader2 size={14} className="animate-spin" />
            <span className="font-tech text-[10px] tracking-widest uppercase animate-pulse">Processing Neural Net...</span>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form onSubmit={handleSend} className="relative group">
        <div className="absolute -inset-0.5 bg-neon-cyan/20 blur opacity-0 group-focus-within:opacity-100 transition-opacity rounded-lg" />
        <div className="relative flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="COMMUNICATE WITH CORE..."
            disabled={isLoading}
            className="flex-1 bg-surface-card/80 backdrop-blur-md text-white text-[11px] font-tech tracking-wider rounded border border-neon-cyan/20 px-3 py-2.5 focus:border-neon-cyan/60 focus:outline-none placeholder:text-white/20 uppercase"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="flex items-center justify-center w-10 h-10 bg-neon-cyan/10 border border-neon-cyan/30 text-neon-cyan rounded hover:bg-neon-cyan/20 disabled:opacity-20 transition-all shadow-neon"
          >
            <Send size={15} />
          </button>
        </div>
      </form>
    </div>
  );
}

function QuickActionButton({
  icon,
  label,
  onClick,
  disabled,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  disabled?: boolean;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className="flex flex-col items-center justify-center gap-1 p-1.5 glass-panel border-neon-cyan/20 hover:border-neon-cyan/60 text-neon-cyan/60 hover:text-neon-cyan disabled:opacity-20 transition-all active:scale-95 group"
    >
      <div className="group-hover:shadow-neon transition-shadow">{icon}</div>
      <span className="font-tech text-[8px] tracking-widest uppercase">{label}</span>
    </button>
  );
}

function MessagePacket({ message }: { message: CoachMessage }) {
  const isCoach = message.role === "coach";
  const isSystem = message.role === "system";

  return (
    <motion.div
      initial={{ x: isCoach ? -10 : 10, opacity: 0 }}
      animate={{ x: 0, opacity: 1 }}
      className={clsx(
        "flex flex-col",
        isCoach ? "items-start" : "items-end"
      )}
    >
      <div className={clsx(
        "max-w-[90%] p-3 relative overflow-hidden",
        isSystem ? "bg-neon-red/10 border-l-2 border-neon-red text-neon-red" : 
        isCoach ? "bg-neon-cyan/5 border-l-2 border-neon-cyan text-slate-200" :
        "bg-white/5 border-r-2 border-white/40 text-slate-300"
      )}>
        {/* Subtle background decoration */}
        <div className="absolute top-0 right-0 w-8 h-8 opacity-[0.03] pointer-events-none">
          <Cpu size={32} />
        </div>
        
        <div className="flex items-center justify-between mb-1.5">
          <span className={clsx(
            "font-tech text-[9px] tracking-[0.2em] font-bold uppercase",
            isSystem ? "text-neon-red" : isCoach ? "text-neon-cyan" : "text-white/60"
          )}>
            {isSystem ? "SYSTEM_CRITICAL" : isCoach ? "STRATEGIST" : "COMMANDER"}
          </span>
          <span className="text-[8px] font-mono opacity-30">
            {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
        
        <p className="text-xs leading-relaxed tracking-wide font-sans line-clamp-none">
          {message.content}
        </p>

        {isCoach && message.type && (
          <div className="mt-2 pt-2 border-t border-neon-cyan/10 flex items-center gap-2">
            <div className="w-1 h-1 bg-neon-cyan rounded-full animate-pulse" />
            <span className="text-[8px] font-tech text-neon-cyan/40 uppercase tracking-[0.3em]">
              {message.type} data stream
            </span>
          </div>
        )}
      </div>
    </motion.div>
  );
}


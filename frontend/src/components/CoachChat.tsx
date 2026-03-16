/**
 * CoachChat — generative AI coaching interface.
 *
 * Chat panel with preset coaching actions and free-form messaging.
 */

import { useEffect, useRef, useState } from "react";
import { MessageSquare, Send, Lightbulb, Search, BarChart2, Loader2 } from "lucide-react";
import clsx from "clsx";
import type { UseCoachReturn } from "../hooks/useCoach";
import type { CoachMessage } from "../hooks/useCoach";
import type { GameState } from "../types/chess";

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

  // Auto-scroll
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
    <div className="card flex flex-col h-full min-h-[400px]">
      {/* Header */}
      <div className="flex items-center gap-2 p-4 border-b border-surface-border">
        <MessageSquare size={16} className="text-brand-400" />
        <h2 className="text-sm font-semibold text-white">Coach</h2>
        <span className="ml-auto text-xs badge-blue">Gemini</span>
      </div>

      {/* Quick actions */}
      <div className="flex gap-1.5 p-3 border-b border-surface-border flex-wrap">
        <QuickActionButton
          icon={<Lightbulb size={13} />}
          label="Hint"
          onClick={handleHint}
          disabled={isLoading || gameState.isGameOver || gameState.isThinking}
          title="Get a strategic hint"
        />
        <QuickActionButton
          icon={<Search size={13} />}
          label="Explain Move"
          onClick={handleExplain}
          disabled={isLoading || !gameState.lastAiMove}
          title="Explain the AI's last move"
        />
        <QuickActionButton
          icon={<BarChart2 size={13} />}
          label="Analyze Game"
          onClick={handlePostGame}
          disabled={isLoading || !gameState.isGameOver}
          title="Post-game analysis (only after game ends)"
        />
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}

        {isLoading && (
          <div className="flex items-center gap-2 text-xs text-muted">
            <Loader2 size={14} className="animate-spin text-brand-400" />
            <span className="animate-thinking">Thinking...</span>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <form
        onSubmit={handleSend}
        className="p-3 border-t border-surface-border"
      >
        <div className="flex gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder="Ask anything about the game..."
            disabled={isLoading}
            className="flex-1 bg-surface text-white text-sm rounded-lg px-3 py-2 border border-surface-border focus:border-brand-600 focus:outline-none focus:ring-1 focus:ring-brand-600 placeholder:text-slate-500 disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !inputValue.trim()}
            className="btn-primary p-2 disabled:opacity-40"
          >
            <Send size={15} />
          </button>
        </div>
      </form>
    </div>
  );
}

// ─── Sub-components ───────────────────────────────────────────

function QuickActionButton({
  icon,
  label,
  onClick,
  disabled,
  title,
}: {
  icon: React.ReactNode;
  label: string;
  onClick: () => void;
  disabled?: boolean;
  title?: string;
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={clsx(
        "flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium transition-all duration-150",
        "bg-surface-border text-slate-300 border border-surface-border",
        "hover:bg-brand-900/40 hover:text-brand-300 hover:border-brand-700",
        "disabled:opacity-40 disabled:cursor-not-allowed disabled:hover:bg-surface-border disabled:hover:text-slate-300"
      )}
    >
      {icon}
      {label}
    </button>
  );
}

function MessageBubble({ message }: { message: CoachMessage }) {
  const isCoach = message.role === "coach";
  const isSystem = message.role === "system";

  if (isSystem) {
    return (
      <div className="text-xs text-red-400 bg-red-900/20 rounded-lg px-3 py-2 border border-red-800/50">
        {message.content}
      </div>
    );
  }

  return (
    <div
      className={clsx(
        "animate-fade-in",
        isCoach ? "mr-4" : "ml-4"
      )}
    >
      <div className={clsx(isCoach ? "coach-message-ai" : "coach-message-user")}>
        {isCoach && (
          <div className="flex items-center gap-1.5 mb-1.5">
            <span className="text-xs font-semibold text-brand-400">Coach</span>
            {message.type && (
              <span className="text-xs text-muted">· {messageTypeLabel(message.type)}</span>
            )}
          </div>
        )}
        <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
      </div>
      <div
        className={clsx(
          "text-xs text-muted mt-1",
          isCoach ? "text-left" : "text-right"
        )}
      >
        {formatTime(message.timestamp)}
      </div>
    </div>
  );
}

function messageTypeLabel(type: CoachMessage["type"]): string {
  switch (type) {
    case "hint": return "Hint";
    case "explain": return "Move explanation";
    case "postgame": return "Game analysis";
    case "chat": return "";
    default: return "";
  }
}

function formatTime(date: Date): string {
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

/**
 * useCoach — generative AI coaching interactions.
 */

import { useCallback, useState } from "react";
import { coachApi } from "../services/api";
import type { Difficulty, PlayerColor } from "../types/chess";

export type CoachMessageRole = "user" | "coach" | "system";

export interface CoachMessage {
  id: string;
  role: CoachMessageRole;
  content: string;
  timestamp: Date;
  type?: "hint" | "explain" | "postgame" | "chat";
}

export interface UseCoachReturn {
  messages: CoachMessage[];
  isLoading: boolean;
  error: string | null;
  getHint: (fen: string, playerColor: PlayerColor, moveHistory: string[], difficulty: Difficulty) => Promise<void>;
  explainLastMove: (fen: string, aiMove: string, aiMoveSan: string, moveHistory: string[], difficulty: Difficulty) => Promise<void>;
  getPostgameAnalysis: (pgn: string, difficulty: Difficulty, playerColor: PlayerColor, result: string) => Promise<void>;
  sendChatMessage: (message: string, fen: string, moveHistory: string[]) => Promise<void>;
  clearMessages: () => void;
}

let messageCounter = 0;
const nextId = () => `msg-${++messageCounter}`;

export function useCoach(): UseCoachReturn {
  const [messages, setMessages] = useState<CoachMessage[]>([
    {
      id: "welcome",
      role: "coach",
      content:
        "Hey! Make a move and I'll follow along. You can ask for a hint, get a breakdown of my last move, or just chat about what's happening on the board.",
      timestamp: new Date(),
      type: "chat",
    },
  ]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const addMessage = useCallback(
    (role: CoachMessageRole, content: string, type?: CoachMessage["type"]) => {
      setMessages((prev) => [
        ...prev,
        { id: nextId(), role, content, timestamp: new Date(), type },
      ]);
    },
    []
  );

  const withLoading = useCallback(
    async (fn: () => Promise<void>) => {
      setIsLoading(true);
      setError(null);
      try {
        await fn();
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Coach unavailable";
        setError(msg);
        addMessage("system", `⚠️ ${msg}`);
      } finally {
        setIsLoading(false);
      }
    },
    [addMessage]
  );

  const getHint = useCallback(
    (fen: string, playerColor: PlayerColor, moveHistory: string[], difficulty: Difficulty) =>
      withLoading(async () => {
        addMessage("user", "What should I be thinking about here?", "hint");
        const result = await coachApi.getHint({ fen, player_color: playerColor, move_history: moveHistory, difficulty });
        addMessage("coach", result.hint, "hint");
      }),
    [withLoading, addMessage]
  );

  const explainLastMove = useCallback(
    (fen: string, aiMove: string, aiMoveSan: string, moveHistory: string[], difficulty: Difficulty) =>
      withLoading(async () => {
        addMessage("user", `Why did the AI play ${aiMoveSan}?`, "explain");
        const result = await coachApi.explainMove({
          fen,
          ai_move: aiMove,
          ai_move_san: aiMoveSan,
          move_history: moveHistory,
          difficulty,
        });
        addMessage("coach", result.explanation, "explain");
      }),
    [withLoading, addMessage]
  );

  const getPostgameAnalysis = useCallback(
    (pgn: string, difficulty: Difficulty, playerColor: PlayerColor, result: string) =>
      withLoading(async () => {
        addMessage("user", "How did I play overall? Walk me through the game.", "postgame");
        const response = await coachApi.postgameAnalysis({ pgn, difficulty, player_color: playerColor, result });
        addMessage("coach", response.summary, "postgame");
      }),
    [withLoading, addMessage]
  );

  const sendChatMessage = useCallback(
    (message: string, fen: string, moveHistory: string[]) =>
      withLoading(async () => {
        addMessage("user", message, "chat");
        const result = await coachApi.chat({
          message,
          fen,
          move_history: moveHistory,
        });
        addMessage("coach", result.response, "chat");
      }),
    [withLoading, addMessage]
  );

  const clearMessages = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return {
    messages,
    isLoading,
    error,
    getHint,
    explainLastMove,
    getPostgameAnalysis,
    sendChatMessage,
    clearMessages,
  };
}

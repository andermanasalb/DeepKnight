/**
 * useGame — central game state management hook.
 *
 * Handles:
 * - Creating new games
 * - Submitting player moves
 * - Tracking board/game state
 * - Coordinating with the backend API
 */

import { useCallback, useState } from "react";
import { gameApi } from "../services/api";
import type {
  Difficulty,
  GameOverReason,
  GameState,
  Move,
  PlayerColor,
} from "../types/chess";
import { STARTING_FEN } from "../types/chess";
import type { AnalysisInfo } from "../types/api";

const INITIAL_STATE: GameState = {
  gameId: null,
  fen: STARTING_FEN,
  turn: "white",
  difficulty: "medium",
  legalMoves: [],
  isCheck: false,
  isCheckmate: false,
  isStalemate: false,
  isGameOver: false,
  gameOverReason: null,
  pgn: "",
  moveHistory: [],
  isThinking: false,
  lastAiMove: null,
  lastAiMoveSan: null,
};

export interface UseGameReturn {
  gameState: GameState;
  analysis: AnalysisInfo | null;
  error: string | null;
  startNewGame: (difficulty: Difficulty) => Promise<void>;
  makeMove: (moveUci: string) => Promise<void>;
  clearError: () => void;
}

export function useGame(): UseGameReturn {
  const [gameState, setGameState] = useState<GameState>(INITIAL_STATE);
  const [analysis, setAnalysis] = useState<AnalysisInfo | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [moveHistoryUci, setMoveHistoryUci] = useState<string[]>([]);

  const startNewGame = useCallback(async (difficulty: Difficulty) => {
    setError(null);
    setGameState((prev) => ({ ...prev, isThinking: true }));
    setMoveHistoryUci([]);

    try {
      const response = await gameApi.newGame({ difficulty });
      setGameState({
        gameId: response.game_id,
        fen: response.fen,
        turn: response.turn,
        difficulty,
        legalMoves: response.legal_moves,
        isCheck: false,
        isCheckmate: false,
        isStalemate: false,
        isGameOver: false,
        gameOverReason: null,
        pgn: "",
        moveHistory: [],
        isThinking: false,
        lastAiMove: null,
        lastAiMoveSan: null,
      });
      setAnalysis(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to start game");
      setGameState((prev) => ({ ...prev, isThinking: false }));
    }
  }, []);

  const makeMove = useCallback(
    async (moveUci: string) => {
      if (gameState.isThinking || gameState.isGameOver) return;
      setError(null);
      setGameState((prev) => ({ ...prev, isThinking: true }));

      try {
        const updatedHistory = [...moveHistoryUci, moveUci];
        const response = await gameApi.makeMove({
          fen: gameState.fen,
          move_uci: moveUci,
          difficulty: gameState.difficulty,
          move_history: moveHistoryUci,
        });

        // Update move history UCI
        const allMoves = [...updatedHistory];
        if (response.ai_move) allMoves.push(response.ai_move);
        setMoveHistoryUci(allMoves);

        // Build Move objects for history
        const newMoves: Move[] = [...gameState.moveHistory];
        const currentMoveNumber = Math.floor(gameState.moveHistory.length / 2) + 1;

        newMoves.push({
          uci: response.player_move,
          san: response.player_move_san,
          player: "white" as PlayerColor,
          moveNumber: currentMoveNumber,
        });

        if (response.ai_move && response.ai_move_san) {
          newMoves.push({
            uci: response.ai_move,
            san: response.ai_move_san,
            player: "black" as PlayerColor,
            moveNumber: currentMoveNumber,
          });
        }

        setGameState((prev) => ({
          ...prev,
          fen: response.fen,
          turn: response.turn,
          legalMoves: response.legal_moves,
          isCheck: response.is_check,
          isCheckmate: response.is_checkmate,
          isStalemate: response.is_stalemate,
          isGameOver: response.is_game_over,
          gameOverReason: response.game_over_reason as GameOverReason,
          pgn: response.pgn,
          moveHistory: newMoves,
          isThinking: false,
          lastAiMove: response.ai_move,
          lastAiMoveSan: response.ai_move_san,
        }));

        setAnalysis(response.analysis);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Move failed");
        setGameState((prev) => ({ ...prev, isThinking: false }));
      }
    },
    [gameState, moveHistoryUci]
  );

  const clearError = useCallback(() => setError(null), []);

  return {
    gameState,
    analysis,
    error,
    startNewGame,
    makeMove,
    clearError,
  };
}

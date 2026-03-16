/**
 * ChessGame — main page layout.
 *
 * Layout:
 *   ┌─────────────────────────────────────────────┐
 *   │                   Header                    │
 *   ├──────────────────┬──────────────────────────┤
 *   │                  │   Controls + Analysis     │
 *   │    Chess Board   │   Coach Chat              │
 *   │                  │   Move History            │
 *   └──────────────────┴──────────────────────────┘
 */

import { useCallback, useEffect, useRef, useState } from "react";
import Header from "../components/Header";
import ChessBoard from "../components/ChessBoard";
import DifficultySelector from "../components/DifficultySelector";
import AnalysisPanel from "../components/AnalysisPanel";
import CoachChat from "../components/CoachChat";
import MoveHistory from "../components/MoveHistory";
import NewGameButton from "../components/NewGameButton";
import { useGame } from "../hooks/useGame";
import { useCoach } from "../hooks/useCoach";
import type { Difficulty } from "../types/chess";
import { AlertCircle, X } from "lucide-react";

export default function ChessGame() {
  const { gameState, analysis, error, startNewGame, makeMove, clearError } = useGame();
  const coachHook = useCoach();

  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty>("medium");
  const [boardWidth, setBoardWidth] = useState(480);
  const boardContainerRef = useRef<HTMLDivElement>(null);

  // Responsive board size
  useEffect(() => {
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const width = entry.contentRect.width;
        setBoardWidth(Math.min(Math.max(280, width - 16), 560));
      }
    });

    if (boardContainerRef.current) {
      observer.observe(boardContainerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  // Extract UCI history from move history for coach
  const moveHistoryUci = gameState.moveHistory.map((m) => m.uci);

  const handleNewGame = useCallback(async () => {
    await startNewGame(selectedDifficulty);
    coachHook.clearMessages();
  }, [selectedDifficulty, startNewGame, coachHook]);

  const handleMove = useCallback(
    async (moveUci: string) => {
      await makeMove(moveUci);
    },
    [makeMove]
  );

  // Auto-start a game on first load
  useEffect(() => {
    if (!gameState.gameId) {
      startNewGame("medium");
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1 max-w-7xl mx-auto w-full px-4 sm:px-6 lg:px-8 py-6">
        {/* Error Banner */}
        {error && (
          <div className="mb-4 flex items-center gap-3 p-3 bg-red-900/30 border border-red-800 rounded-lg text-sm text-red-300 animate-fade-in">
            <AlertCircle size={16} className="shrink-0" />
            <span className="flex-1">{error}</span>
            <button
              onClick={clearError}
              className="text-red-400 hover:text-red-200 transition-colors"
            >
              <X size={16} />
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-[1fr_360px] gap-6">
          {/* ─── Left: Chess Board ─── */}
          <div className="flex flex-col items-center gap-4">
            {/* Player indicators */}
            <PlayerBadge name="Engine" color="black" difficulty={gameState.difficulty} />

            <div ref={boardContainerRef} className="w-full max-w-[560px]">
              <ChessBoard
                gameState={gameState}
                onMove={handleMove}
                boardWidth={boardWidth}
              />
            </div>

            <PlayerBadge name="You" color="white" />

            {/* Mobile controls */}
            <div className="lg:hidden w-full max-w-[560px] space-y-3">
              <DifficultySelector
                value={selectedDifficulty}
                onChange={setSelectedDifficulty}
                disabled={gameState.isThinking}
              />
              <NewGameButton
                onClick={handleNewGame}
                isLoading={gameState.isThinking && !gameState.gameId}
              />
            </div>
          </div>

          {/* ─── Right: Controls + Panels ─── */}
          <div className="flex flex-col gap-4">
            {/* Game controls — desktop only */}
            <div className="hidden lg:block card p-4 space-y-4">
              <DifficultySelector
                value={selectedDifficulty}
                onChange={setSelectedDifficulty}
                disabled={gameState.isThinking}
              />
              <NewGameButton
                onClick={handleNewGame}
                isLoading={gameState.isThinking && !gameState.gameId}
              />
            </div>

            {/* Analysis */}
            <AnalysisPanel gameState={gameState} analysis={analysis} />

            {/* Coach Chat */}
            <div className="flex-1 min-h-[320px]">
              <CoachChat
                coachHook={coachHook}
                gameState={gameState}
                moveHistoryUci={moveHistoryUci}
              />
            </div>

            {/* Move History */}
            <div className="h-[220px]">
              <MoveHistory
                moves={gameState.moveHistory}
                pgn={gameState.pgn}
              />
            </div>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-surface-border py-4 text-center">
        <p className="text-xs text-muted">
          DeepKnight · React · FastAPI · PyTorch · Gemini
        </p>
      </footer>
    </div>
  );
}

function PlayerBadge({
  name,
  color,
  difficulty,
}: {
  name: string;
  color: "white" | "black";
  difficulty?: string;
}) {
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 bg-surface-card rounded-full border border-surface-border">
      <span
        className="w-4 h-4 rounded-sm border border-slate-600"
        style={{ backgroundColor: color === "white" ? "#f0d9b5" : "#333" }}
      />
      <span className="text-sm font-medium text-slate-200">{name}</span>
      {difficulty && (
        <span className="text-xs text-muted">({difficulty})</span>
      )}
    </div>
  );
}

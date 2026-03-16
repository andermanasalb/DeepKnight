/**
 * ChessBoard — interactive drag-and-drop chess board.
 *
 * Uses react-chessboard for rendering.
 * chess.js handles frontend move validation for UX only.
 * The backend (python-chess) is the source of truth.
 */

import { useCallback, useMemo } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";
import type { Square } from "chess.js";
import clsx from "clsx";
import type { GameState } from "../types/chess";

interface ChessBoardProps {
  gameState: GameState;
  onMove: (moveUci: string) => void;
  boardWidth?: number;
}

export default function ChessBoard({
  gameState,
  onMove,
  boardWidth = 480,
}: ChessBoardProps) {
  const { fen, isThinking, isGameOver, legalMoves, lastAiMove, isCheck } =
    gameState;

  // Use chess.js only for lightweight frontend helpers
  const chessInstance = useMemo(() => {
    try {
      const chess = new Chess(fen);
      return chess;
    } catch {
      return new Chess();
    }
  }, [fen]);

  // Highlight squares: last AI move + check
  const customSquareStyles = useMemo(() => {
    const styles: Record<string, React.CSSProperties> = {};

    if (lastAiMove && lastAiMove.length >= 4) {
      const from = lastAiMove.slice(0, 2) as Square;
      const to = lastAiMove.slice(2, 4) as Square;
      styles[from] = { backgroundColor: "rgba(205, 209, 106, 0.4)" };
      styles[to] = { backgroundColor: "rgba(205, 209, 106, 0.55)" };
    }

    if (isCheck) {
      const kingSquare = findKingSquare(chessInstance, "w");
      if (kingSquare) {
        styles[kingSquare] = { backgroundColor: "rgba(231, 76, 60, 0.55)" };
      }
    }

    return styles;
  }, [lastAiMove, isCheck, chessInstance]);

  const onDrop = useCallback(
    (sourceSquare: Square, targetSquare: Square, piece: string): boolean => {
      if (isThinking || isGameOver) return false;
      if (gameState.turn !== "white") return false;

      // Validate the move shape using chess.js for smooth UX
      const moveUci = `${sourceSquare}${targetSquare}`;

      // Handle promotion (auto-queen)
      const isPromotion =
        piece === "wP" &&
        targetSquare[1] === "8" &&
        sourceSquare[1] === "7";

      const finalUci = isPromotion ? `${moveUci}q` : moveUci;

      // Check if it's in our legal moves list (from backend)
      const isLegal = legalMoves.some(
        (m) =>
          m === finalUci ||
          m.startsWith(moveUci) // handle promotion variants
      );

      if (!isLegal) return false;

      onMove(finalUci);
      return true;
    },
    [isThinking, isGameOver, gameState.turn, legalMoves, onMove]
  );

  return (
    <div className="chess-board-container select-none">
      {/* Thinking indicator */}
      {isThinking && (
        <div className="absolute inset-0 z-10 flex items-center justify-center rounded-xl bg-black/30 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-3">
            <div className="flex gap-1.5">
              {[0, 1, 2].map((i) => (
                <div
                  key={i}
                  className="w-2.5 h-2.5 rounded-full bg-brand-400 animate-thinking"
                  style={{ animationDelay: `${i * 0.2}s` }}
                />
              ))}
            </div>
            <span className="text-sm text-slate-300 font-medium">
              Calculating...
            </span>
          </div>
        </div>
      )}

      {/* Game over overlay */}
      {isGameOver && (
        <div className="absolute inset-0 z-10 flex items-center justify-center rounded-xl bg-black/50 backdrop-blur-sm">
          <div className="text-center p-6 bg-surface-card rounded-xl border border-surface-border shadow-2xl">
            <div className="text-4xl mb-2">
              {gameState.isCheckmate ? "♚" : "½"}
            </div>
            <p className="text-lg font-bold text-white">
              {gameState.isCheckmate
                ? gameState.turn === "white"
                  ? "Black wins by checkmate!"
                  : "White wins by checkmate!"
                : "Draw!"}
            </p>
            <p className="text-sm text-muted mt-1">
              {gameState.gameOverReason?.replace(/_/g, " ")}
            </p>
          </div>
        </div>
      )}

      <Chessboard
        id="main-board"
        position={fen}
        onPieceDrop={onDrop}
        boardWidth={boardWidth}
        boardOrientation="white"
        customSquareStyles={customSquareStyles}
        customDarkSquareStyle={{ backgroundColor: "#b58863" }}
        customLightSquareStyle={{ backgroundColor: "#f0d9b5" }}
        animationDuration={200}
        arePiecesDraggable={!isThinking && !isGameOver && gameState.turn === "white"}
      />
    </div>
  );
}

function findKingSquare(chess: Chess, color: "w" | "b"): Square | null {
  const board = chess.board();
  for (let rank = 0; rank < 8; rank++) {
    for (let file = 0; file < 8; file++) {
      const piece = board[rank][file];
      if (piece && piece.type === "k" && piece.color === color) {
        const files = "abcdefgh";
        return `${files[file]}${8 - rank}` as Square;
      }
    }
  }
  return null;
}

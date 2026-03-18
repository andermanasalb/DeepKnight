import { useCallback, useEffect, useMemo, useState } from "react";
import { Chessboard } from "react-chessboard";
import { Chess } from "chess.js";
import type { Square } from "chess.js";
import type { GameState } from "../types/chess";
import { motion, AnimatePresence } from "framer-motion";

interface ChessBoardProps {
  gameState: GameState;
  onMove: (moveUci: string) => void;
  boardWidth?: number;
  suggestedMove?: string | null;
}

export default function ChessBoard({
  gameState,
  onMove,
  boardWidth = 480,
  suggestedMove,
}: ChessBoardProps) {
  const { fen, isThinking, isGameOver, legalMoves, lastAiMove, isCheck } =
    gameState;

  const [selectedSquare, setSelectedSquare] = useState<Square | null>(null);
  const [moveOptions, setMoveOptions] = useState<Square[]>([]);

  const chessInstance = useMemo(() => {
    try {
      const chess = new Chess(fen);
      return chess;
    } catch {
      return new Chess();
    }
  }, [fen]);

  // Clear selection after any move (FEN changes)
  useEffect(() => {
    setSelectedSquare(null);
    setMoveOptions([]);
  }, [fen]);

  const getMoveOptions = useCallback((square: Square): Square[] => {
    return chessInstance.moves({ square, verbose: true }).map((m) => m.to as Square);
  }, [chessInstance]);

  const onSquareClick = useCallback((square: Square) => {
    if (isThinking || isGameOver || gameState.turn !== "white") return;

    if (selectedSquare && moveOptions.includes(square)) {
      const moveUci = `${selectedSquare}${square}`;
      const piece = chessInstance.get(selectedSquare);
      const isPromotion = piece?.type === "p" && piece.color === "w" && square[1] === "8";
      onMove(isPromotion ? `${moveUci}q` : moveUci);
      return;
    }

    const piece = chessInstance.get(square);
    if (piece && piece.color === "w") {
      setSelectedSquare(square);
      setMoveOptions(getMoveOptions(square));
    } else {
      setSelectedSquare(null);
      setMoveOptions([]);
    }
  }, [isThinking, isGameOver, gameState.turn, selectedSquare, moveOptions, chessInstance, getMoveOptions, onMove]);

  // Use neon cyan for last move and red for check
  const customSquareStyles = useMemo(() => {
    const styles: Record<string, React.CSSProperties> = {};

    if (lastAiMove && lastAiMove.length >= 4) {
      const from = lastAiMove.slice(0, 2) as Square;
      const to = lastAiMove.slice(2, 4) as Square;
      styles[from] = { 
        background: "rgba(0, 229, 255, 0.1)",
        boxShadow: "inset 0 0 10px rgba(0, 229, 255, 0.2)"
      };
      styles[to] = { 
        background: "rgba(0, 229, 255, 0.25)",
        boxShadow: "inset 0 0 15px rgba(0, 229, 255, 0.4)"
      };
    }

    if (isCheck) {
      const color = gameState.turn === "white" ? "w" : "b";
      const kingSquare = findKingSquare(chessInstance, color);
      if (kingSquare) {
        styles[kingSquare] = { 
          background: "radial-gradient(circle, rgba(255, 61, 61, 0.6) 0%, rgba(255, 61, 61, 0.2) 100%)",
          boxShadow: "0 0 20px rgba(255, 61, 61, 0.6)"
        };
      }
    }

    // Suggested move from coach — amber/gold, applied last to take priority
    if (suggestedMove && suggestedMove.length >= 4) {
      const from = suggestedMove.slice(0, 2) as Square;
      const to = suggestedMove.slice(2, 4) as Square;
      styles[from] = {
        background: "rgba(251, 191, 36, 0.2)",
        boxShadow: "inset 0 0 12px rgba(251, 191, 36, 0.4)",
      };
      styles[to] = {
        background: "rgba(251, 191, 36, 0.45)",
        boxShadow: "inset 0 0 20px rgba(251, 191, 36, 0.7)",
      };
    }

    // Selected square highlight
    if (selectedSquare) {
      styles[selectedSquare] = {
        background: "rgba(0, 229, 255, 0.35)",
        boxShadow: "inset 0 0 12px rgba(0, 229, 255, 0.5)"
      };
    }

    // Legal move dots
    for (const sq of moveOptions) {
      const hasPiece = !!chessInstance.get(sq);
      styles[sq] = hasPiece
        ? { background: "radial-gradient(circle, rgba(255,255,255,0.3) 60%, transparent 65%)", border: "2px solid rgba(255,255,255,0.35)" }
        : { background: "radial-gradient(circle, rgba(255,255,255,0.35) 22%, transparent 27%)" };
    }

    return styles;
  }, [suggestedMove, lastAiMove, isCheck, chessInstance, gameState.turn, selectedSquare, moveOptions]);

  const onDrop = useCallback(
    (sourceSquare: Square, targetSquare: Square, piece: string): boolean => {
      if (isThinking || isGameOver) return false;
      if (gameState.turn !== "white") return false;

      const moveUci = `${sourceSquare}${targetSquare}`;
      const isPromotion = piece === "wP" && targetSquare[1] === "8" && sourceSquare[1] === "7";
      const finalUci = isPromotion ? `${moveUci}q` : moveUci;

      const isLegal = legalMoves.some(
        (m) => m === finalUci || m.startsWith(moveUci)
      );

      if (!isLegal) return false;
      onMove(finalUci);
      return true;
    },
    [isThinking, isGameOver, gameState.turn, legalMoves, onMove]
  );

  return (
    <div className="relative select-none group">
      {/* Decorative Frame */}
      <div className="absolute inset-0 bg-neon-cyan/20 blur opacity-25 group-hover:opacity-40 transition-opacity duration-500 rounded-lg" />
      
      <div className="relative rounded-lg border border-neon-cyan/30 overflow-hidden">
        <AnimatePresence>
          {isThinking && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="absolute inset-0 z-20 flex items-center justify-center bg-surface/40 backdrop-blur-sm"
            >
              <div className="flex flex-col items-center gap-4">
                <div className="relative w-16 h-16">
                  <div className="absolute inset-0 border-2 border-neon-cyan/20 rounded-full" />
                  <motion.div 
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                    className="absolute inset-0 border-2 border-t-neon-cyan rounded-full shadow-neon"
                  />
                </div>
                <span className="font-tech text-xs tracking-widest text-neon-cyan uppercase animate-pulse">
                  Analyzing Tactics...
                </span>
              </div>
            </motion.div>
          )}

          {isGameOver && (
            <motion.div 
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              className="absolute inset-0 z-30 flex items-center justify-center bg-black/60 backdrop-blur-md"
            >
              <div className="text-center p-8 glass-panel border-neon-cyan/40 scale-110">
                <div className="font-tech text-4xl mb-4 text-neon-cyan neon-text">
                  {gameState.isCheckmate ? "TERMINATED" : "STALEMATE"}
                </div>
                <p className="font-tech text-lg text-white mb-2 tracking-widest">
                  {gameState.isCheckmate
                    ? gameState.turn === "white"
                      ? "AI CORE DOMINANCE"
                      : "HUMAN CALCULATION SUCCESS"
                    : "LOGICAL DEADLOCK"}
                </p>
                <div className="h-[1px] w-full bg-gradient-to-r from-transparent via-neon-cyan/50 to-transparent my-4" />
                <p className="text-xs uppercase tracking-tighter text-neon-cyan/60 font-tech">
                  {gameState.gameOverReason?.replace(/_/g, " ")}
                </p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <Chessboard
          id="main-board"
          position={fen}
          onPieceDrop={onDrop}
          boardWidth={boardWidth}
          boardOrientation="white"
          onSquareClick={onSquareClick}
          customSquareStyles={customSquareStyles}
          customDarkSquareStyle={{
            background: "linear-gradient(135deg, rgba(0, 229, 255, 0.1) 0%, rgba(0, 0, 0, 0.4) 100%)",
            boxShadow: "inset 0 0 0 1px rgba(0, 229, 255, 0.05)"
          }}
          customLightSquareStyle={{
            background: "linear-gradient(135deg, rgba(255, 255, 255, 0.05) 0%, rgba(255, 255, 255, 0.02) 100%)",
            boxShadow: "inset 0 0 0 1px rgba(255, 255, 255, 0.02)"
          }}
          animationDuration={300}
          arePiecesDraggable={false}
        />
      </div>
      
      {/* Global CSS for pieces within this board */}
      <style dangerouslySetInnerHTML={{ __html: `
        [data-boardid="main-board"] img {
          filter: brightness(1.2) contrast(1.1) drop-shadow(0 0 2px rgba(0, 229, 255, 0.4)) !important;
          transition: filter 0.3s ease;
        }
        [data-boardid="main-board"] [data-square]:hover img {
          filter: brightness(1.4) contrast(1.2) drop-shadow(0 0 5px rgba(0, 229, 255, 0.6)) !important;
        }
      `}} />
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


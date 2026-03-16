/**
 * MoveHistory — displays the move list in SAN notation.
 */

import { useEffect, useRef } from "react";
import { List } from "lucide-react";
import clsx from "clsx";
import type { Move } from "../types/chess";

interface MoveHistoryProps {
  moves: Move[];
  pgn?: string;
}

export default function MoveHistory({ moves, pgn }: MoveHistoryProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest move
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [moves.length]);

  // Group moves into pairs (White, Black)
  const movePairs = groupMoves(moves);

  return (
    <div className="card flex flex-col h-full min-h-[200px]">
      <div className="flex items-center gap-2 p-4 border-b border-surface-border">
        <List size={16} className="text-brand-400" />
        <h2 className="text-sm font-semibold text-white">Move History</h2>
        <span className="ml-auto text-xs text-muted">
          {moves.length > 0 ? `${Math.ceil(moves.length / 2)} moves` : "No moves"}
        </span>
      </div>

      <div className="flex-1 overflow-y-auto p-3">
        {moves.length === 0 ? (
          <div className="flex items-center justify-center h-full py-6">
            <p className="text-xs text-muted">No moves yet — start playing!</p>
          </div>
        ) : (
          <div className="space-y-0.5">
            {movePairs.map((pair, index) => (
              <MovePairRow
                key={index}
                moveNumber={pair.moveNumber}
                whiteMove={pair.white}
                blackMove={pair.black}
                isLastPair={index === movePairs.length - 1}
              />
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* PGN export */}
      {pgn && (
        <div className="p-3 border-t border-surface-border">
          <details className="group">
            <summary className="text-xs text-muted cursor-pointer hover:text-white transition-colors select-none">
              PGN ▸
            </summary>
            <pre className="mt-2 text-xs font-mono text-slate-300 bg-surface p-2 rounded overflow-x-auto whitespace-pre-wrap">
              {pgn}
            </pre>
          </details>
        </div>
      )}
    </div>
  );
}

interface MovePair {
  moveNumber: number;
  white: Move | null;
  black: Move | null;
}

function groupMoves(moves: Move[]): MovePair[] {
  const pairs: MovePair[] = [];

  for (let i = 0; i < moves.length; i += 2) {
    const white = moves[i] || null;
    const black = moves[i + 1] || null;
    pairs.push({
      moveNumber: white?.moveNumber ?? Math.ceil((i + 1) / 2),
      white,
      black,
    });
  }

  return pairs;
}

function MovePairRow({
  moveNumber,
  whiteMove,
  blackMove,
  isLastPair,
}: {
  moveNumber: number;
  whiteMove: Move | null;
  blackMove: Move | null;
  isLastPair: boolean;
}) {
  return (
    <div
      className={clsx(
        "grid grid-cols-[2rem_1fr_1fr] gap-1 items-center px-1 py-0.5 rounded",
        isLastPair && "bg-brand-900/20"
      )}
    >
      <span className="text-xs text-muted font-mono">{moveNumber}.</span>
      <MoveToken
        move={whiteMove}
        isLast={isLastPair && !blackMove}
      />
      <MoveToken
        move={blackMove}
        isLast={isLastPair && !!blackMove}
      />
    </div>
  );
}

function MoveToken({
  move,
  isLast,
}: {
  move: Move | null;
  isLast: boolean;
}) {
  if (!move) return <span />;

  return (
    <span
      className={clsx(
        "text-xs font-mono px-1 py-0.5 rounded transition-colors",
        isLast
          ? "text-brand-300 bg-brand-900/30 font-semibold"
          : "text-slate-300 hover:text-white hover:bg-surface cursor-pointer"
      )}
    >
      {move.san}
    </span>
  );
}

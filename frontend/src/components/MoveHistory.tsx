import { useEffect, useRef } from "react";
import { Terminal } from "lucide-react";
import clsx from "clsx";
import type { Move } from "../types/chess";
import { motion } from "framer-motion";

interface MoveHistoryProps {
  moves: Move[];
  pgn?: string;
}

export default function MoveHistory({ moves, pgn }: MoveHistoryProps) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "nearest" });
  }, [moves.length]);

  const movePairs = groupMoves(moves);

  return (
    <div className="flex flex-col h-full bg-transparent">
      {/* Header */}
      <div className="flex items-center justify-between mb-4 px-1">
        <div className="flex items-center gap-2">
          <Terminal size={14} className="text-neon-cyan" />
          <h2 className="font-tech text-xs tracking-[0.2em] text-neon-cyan uppercase">Tactical Log</h2>
        </div>
        <div className="text-[10px] font-mono text-white/30 tabular-nums">
          L: {moves.length}
        </div>
      </div>

      {/* Log Body */}
      <div className="flex-1 glass-panel border-neon-cyan/10 overflow-hidden flex flex-col">
        <div className="flex-1 overflow-y-auto no-scrollbar p-3 font-mono text-[11px] space-y-1">
          {moves.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full opacity-20 italic">
              <span className="mb-2">AWAITING FIRST COMMAND...</span>
              <span className="text-[10px]">NO TELEMETRY DETECTED</span>
            </div>
          ) : (
            movePairs.map((pair, index) => (
              <motion.div 
                key={index}
                initial={{ opacity: 0, x: -5 }}
                animate={{ opacity: 1, x: 0 }}
                className={clsx(
                  "grid grid-cols-[30px_1fr_1fr] gap-4 py-1.5 px-2 transition-colors border-b border-white/5",
                  index === movePairs.length - 1 ? "bg-neon-cyan/5 border-neon-cyan/20" : "hover:bg-white/5"
                )}
              >
                <span className="text-neon-cyan/40 font-bold">{pair.moveNumber.toString().padStart(2, '0')}</span>
                <span className={clsx(
                  "uppercase tracking-wider font-bold",
                  index === movePairs.length - 1 && !pair.black ? "text-neon-cyan neon-text" : "text-white"
                )}>
                  {pair.white?.san || "---"}
                </span>
                <span className={clsx(
                  "uppercase tracking-wider font-bold",
                  index === movePairs.length - 1 && pair.black ? "text-neon-cyan neon-text" : "text-white/60"
                )}>
                  {pair.black?.san || "---"}
                </span>
              </motion.div>
            ))
          )}
          <div ref={bottomRef} />
        </div>

        {/* Binary Overlay (Aesthetic) */}
        <div className="h-4 bg-neon-cyan/5 border-t border-neon-cyan/10 px-2 flex items-center justify-between overflow-hidden">
          <span className="text-[8px] font-mono text-neon-cyan/40 whitespace-nowrap">01001001 01010011 00100000 01000010 01000101 01010011 01010100</span>
          <span className="text-[8px] font-mono text-neon-cyan/40">SYSTEM_OK</span>
        </div>
      </div>

      {/* PGN readout */}
      {pgn && (
        <details className="mt-3 group">
          <summary className="font-tech text-[9px] text-white/30 cursor-pointer hover:text-neon-cyan transition-colors uppercase tracking-widest list-none flex items-center gap-2">
            <div className="w-1 h-1 bg-white/30 rounded-full group-open:bg-neon-cyan" />
            Raw Telemetry (PGN)
          </summary>
          <div className="mt-2 glass-panel bg-black/40 p-3 max-h-32 overflow-y-auto no-scrollbar font-mono text-[10px] text-white/40 leading-relaxed border-white/5">
            {pgn}
          </div>
        </details>
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


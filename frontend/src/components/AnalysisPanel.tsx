import { Activity, Cpu, Brain } from "lucide-react";
import type { AnalysisInfo } from "../types/api";
import type { GameState } from "../types/chess";
import { interpretScore, scoreToBarPercent } from "../types/ml";
import { motion } from "framer-motion";

interface AnalysisPanelProps {
  gameState: GameState;
  analysis: AnalysisInfo | null;
}

export default function AnalysisPanel({ gameState, analysis }: AnalysisPanelProps) {
  const { isThinking } = gameState;

  const classicalScore = analysis?.classical_score ?? 0;
  const barPercent = scoreToBarPercent(classicalScore);
  const interpretation = interpretScore(classicalScore);

  return (
    <div className="w-full flex flex-col gap-2">
      {/* Top Meta Info */}
      <div className="flex items-center justify-between px-1">
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <Activity size={14} className="text-neon-cyan" />
            <span className="font-tech text-[10px] tracking-[0.2em] text-neon-cyan uppercase">Neural Evaluation</span>
          </div>
          <div className="h-[10px] w-[1px] bg-white/10" />
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 opacity-60">
              <Cpu size={12} className="text-neon-cyan" />
              <span className="font-tech text-[9px] text-white tracking-widest uppercase">Depth: {analysis?.depth_searched ?? 0}</span>
            </div>
            <div className="flex items-center gap-2 opacity-60">
              <Brain size={12} className="text-neon-cyan" />
              <span className="font-tech text-[9px] text-white tracking-widest uppercase">Neural: {analysis?.pytorch_score?.toFixed(3) ?? "0.000"}</span>
            </div>
          </div>
        </div>
        
        <div className="flex items-center gap-3">
          {isThinking && (
            <span className="font-tech text-[10px] text-neon-cyan animate-pulse tracking-widest uppercase">Recalculating...</span>
          )}
          <span className="font-tech text-[10px] text-white/40 tracking-widest uppercase">Status: </span>
          <StatusLabel gameState={gameState} />
        </div>
      </div>

      {/* Main Eval Bar Container */}
      <div className="relative h-12 w-full overflow-hidden border border-white/10 group" style={{ background: '#0a0f1a' }}>
        {/* White advantage fill from RIGHT */}
        <motion.div
          initial={{ width: "50%" }}
          animate={{ width: `${barPercent}%` }}
          transition={{ type: "spring", stiffness: 50, damping: 20 }}
          className="absolute inset-y-0 right-0 bg-gradient-to-l from-white/90 to-white/55"
        >
          {/* Glowing divider at the left edge of white fill */}
          <div className="absolute left-0 inset-y-0 w-[2px] bg-white shadow-[0_0_8px_3px_rgba(255,255,255,0.6)]" />
        </motion.div>

        {/* Black Side Label */}
        <div className="absolute left-4 inset-y-0 flex items-center z-10 pointer-events-none">
          <span className="font-tech text-xs tracking-[0.3em] text-white/70 drop-shadow-[0_0_4px_rgba(0,0,0,1)]">BLACK</span>
        </div>

        {/* White Side Label */}
        <div className="absolute right-4 inset-y-0 flex items-center z-10 pointer-events-none">
          <span className="font-tech text-xs tracking-[0.3em] text-slate-800 drop-shadow-[0_0_4px_rgba(255,255,255,0.8)]">WHITE</span>
        </div>

        {/* Score Interpretation + Value */}
        <div className="absolute inset-0 flex items-center justify-center z-20 pointer-events-none gap-2">
          <motion.div
            key={interpretation}
            initial={{ y: 5, opacity: 0 }}
            animate={{ y: 0, opacity: 1 }}
            className="flex items-center gap-2 px-3 py-0.5 bg-black/60 backdrop-blur-md rounded border border-white/15"
          >
            <span className="font-tech text-[10px] tracking-[0.2em] text-white uppercase">{interpretation}</span>
            <span className="font-mono text-[10px] text-neon-cyan/70 tabular-nums">
              {classicalScore >= 0 ? "+" : ""}{classicalScore.toFixed(2)}
            </span>
          </motion.div>
        </div>
      </div>
    </div>
  );
}

function StatusLabel({ gameState }: { gameState: GameState }) {
  const { isGameOver, isCheckmate, isStalemate, isCheck, turn } = gameState;

  if (isCheckmate) return <span className="text-neon-red font-tech text-[10px] tracking-widest uppercase mb-[-1px]">TERMINATED // CHECKMATE</span>;
  if (isStalemate) return <span className="text-neon-pink font-tech text-[10px] tracking-widest uppercase mb-[-1px]">LOCKED // STALEMATE</span>;
  if (isGameOver) return <span className="text-white/60 font-tech text-[10px] tracking-widest uppercase mb-[-1px]">COMPLETED</span>;
  if (isCheck) return <span className="text-neon-red font-tech text-[10px] tracking-widest uppercase mb-[-1px] animate-pulse">BREACH // CHECK</span>;
  
  return (
    <span className="text-neon-cyan font-tech text-[10px] tracking-widest uppercase mb-[-1px]">
      WAITING // {turn === "white" ? "WHITE_UNIT" : "AI_CORE"}
    </span>
  );
}


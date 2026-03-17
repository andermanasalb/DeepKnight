import clsx from "clsx";
import type { Difficulty } from "../types/chess";
import { DIFFICULTY_LABELS } from "../types/chess";
import { motion } from "framer-motion";

interface DifficultySelectorProps {
  value: Difficulty;
  onChange: (difficulty: Difficulty) => void;
  disabled?: boolean;
}

const DIFFICULTY_CONFIG: Record<Difficulty, { color: string; shadow: string }> = {
  easy: { color: "text-neon-cyan", shadow: "shadow-neon" },
  medium: { color: "text-neon-blue", shadow: "shadow-[0_0_15px_rgba(0,178,255,0.4)]" },
  hard: { color: "text-neon-red", shadow: "shadow-[0_0_15px_rgba(255,61,61,0.4)]" },
};

export default function DifficultySelector({
  value,
  onChange,
  disabled = false,
}: DifficultySelectorProps) {
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex items-center justify-between">
        <label className="font-tech text-[9px] tracking-[0.15em] text-white/30 uppercase">
          AI Complexity
        </label>
        <div className="h-[1px] flex-1 mx-3 bg-white/5" />
      </div>

      <div className="grid grid-cols-3 gap-2">
        {(["easy", "medium", "hard"] as Difficulty[]).map((level) => {
          const isSelected = value === level;
          const config = DIFFICULTY_CONFIG[level];

          return (
            <button
              key={level}
              onClick={() => onChange(level)}
              disabled={disabled}
              className={clsx(
                "relative group flex items-center justify-center p-1.5 transition-all duration-300 disabled:opacity-20",
                "border bg-surface-card/40 backdrop-blur-md",
                isSelected
                  ? `${config.color} border-white/20 ${config.shadow} shadow-lg z-10`
                  : "border-white/5 text-white/40 hover:border-white/20 hover:text-white/80"
              )}
            >
              {/* Selected Highlight Overlay */}
              {isSelected && (
                <motion.div
                  layoutId="difficulty-glow"
                  className="absolute inset-0 border border-inherit pointer-events-none"
                  transition={{ type: "spring", bounce: 0.2, duration: 0.6 }}
                >
                  <div className="absolute top-0 left-0 w-1.5 h-1.5 border-t border-l border-white/60" />
                  <div className="absolute top-0 right-0 w-1.5 h-1.5 border-t border-r border-white/60" />
                  <div className="absolute bottom-0 left-0 w-1.5 h-1.5 border-b border-l border-white/60" />
                  <div className="absolute bottom-0 right-0 w-1.5 h-1.5 border-b border-r border-white/60" />
                </motion.div>
              )}

              <span className="font-tech text-[9px] tracking-[0.15em] font-bold uppercase">
                {DIFFICULTY_LABELS[level]}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}


import clsx from "clsx";
import type { Difficulty } from "../types/chess";
import { DIFFICULTY_DESCRIPTIONS, DIFFICULTY_LABELS } from "../types/chess";

interface DifficultySelectorProps {
  value: Difficulty;
  onChange: (difficulty: Difficulty) => void;
  disabled?: boolean;
}

const DIFFICULTY_COLORS: Record<Difficulty, string> = {
  easy: "text-emerald-400 border-emerald-700 bg-emerald-900/20",
  medium: "text-yellow-400 border-yellow-700 bg-yellow-900/20",
  hard: "text-red-400 border-red-700 bg-red-900/20",
};

const DIFFICULTY_SELECTED: Record<Difficulty, string> = {
  easy: "ring-2 ring-emerald-500 border-emerald-500",
  medium: "ring-2 ring-yellow-500 border-yellow-500",
  hard: "ring-2 ring-red-500 border-red-500",
};

export default function DifficultySelector({
  value,
  onChange,
  disabled = false,
}: DifficultySelectorProps) {
  return (
    <div className="space-y-2">
      <label className="text-xs font-medium text-muted uppercase tracking-wider">
        Difficulty
      </label>
      <div className="grid grid-cols-3 gap-2">
        {(["easy", "medium", "hard"] as Difficulty[]).map((level) => (
          <button
            key={level}
            onClick={() => onChange(level)}
            disabled={disabled}
            className={clsx(
              "relative flex flex-col items-center p-2.5 rounded-lg border transition-all duration-200 text-center disabled:opacity-40 disabled:cursor-not-allowed",
              DIFFICULTY_COLORS[level],
              value === level
                ? DIFFICULTY_SELECTED[level]
                : "opacity-60 hover:opacity-90"
            )}
          >
            <span className="text-xs font-semibold">{DIFFICULTY_LABELS[level]}</span>
          </button>
        ))}
      </div>
      <p className="text-xs text-muted">{DIFFICULTY_DESCRIPTIONS[value]}</p>
    </div>
  );
}

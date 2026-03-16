/**
 * AnalysisPanel — displays evaluation scores and game info.
 */

import { Activity, Cpu, Brain, ChevronRight } from "lucide-react";
import clsx from "clsx";
import type { AnalysisInfo } from "../types/api";
import type { GameState } from "../types/chess";
import { interpretScore, scoreToBarPercent } from "../types/ml";

interface AnalysisPanelProps {
  gameState: GameState;
  analysis: AnalysisInfo | null;
}

export default function AnalysisPanel({ gameState, analysis }: AnalysisPanelProps) {
  const { turn, difficulty, isCheck, isCheckmate, isGameOver, isThinking } = gameState;

  const classicalScore = analysis?.classical_score ?? 0;
  const pytorchScore = analysis?.pytorch_score ?? 0;
  const barPercent = scoreToBarPercent(classicalScore);
  const interpretation = interpretScore(classicalScore);

  return (
    <div className="card p-4 space-y-4">
      <div className="flex items-center gap-2">
        <Activity size={16} className="text-brand-400" />
        <h2 className="text-sm font-semibold text-white">Analysis</h2>
      </div>

      {/* Game status */}
      <div className="flex items-center justify-between py-2 border-b border-surface-border">
        <StatusIndicator gameState={gameState} />
        <DifficultyBadge difficulty={difficulty} />
      </div>

      {/* Evaluation bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-xs text-muted">
          <span>Black</span>
          <span className="text-white font-medium">{interpretation}</span>
          <span>White</span>
        </div>

        <div className="relative h-3 rounded-full bg-gray-800 overflow-hidden">
          {/* Black side */}
          <div className="absolute inset-0 bg-gray-900 rounded-full" />
          {/* White side */}
          <div
            className="absolute inset-y-0 left-0 bg-gradient-to-r from-slate-300 to-white rounded-full transition-all duration-500"
            style={{ width: `${barPercent}%` }}
          />
          {/* Center line */}
          <div className="absolute inset-y-0 left-1/2 w-0.5 bg-gray-600/50 -translate-x-1/2" />
        </div>

        <div className="flex justify-between text-xs text-muted">
          <span>
            {classicalScore < 0
              ? `${Math.abs(classicalScore).toFixed(2)} ▲`
              : ""}
          </span>
          <span>
            {classicalScore > 0
              ? `${classicalScore.toFixed(2)} ▲`
              : ""}
          </span>
        </div>
      </div>

      {/* Score breakdown */}
      <div className="space-y-2">
        <ScoreRow
          icon={<Cpu size={13} className="text-blue-400" />}
          label="Classical"
          value={classicalScore}
          subtitle={`Depth ${analysis?.depth_searched ?? 0}`}
        />
        <ScoreRow
          icon={<Brain size={13} className="text-purple-400" />}
          label="Neural"
          value={pytorchScore}
          subtitle="ValueNet"
          normalize
        />
      </div>

      {/* Turn / check info */}
      <div className="pt-2 border-t border-surface-border space-y-1.5">
        <InfoRow
          label="Turn"
          value={
            isGameOver
              ? "Game over"
              : isThinking
              ? "Calculating..."
              : `${turn === "white" ? "White" : "Black"} to move`
          }
        />
        {isCheck && !isCheckmate && (
          <div className="flex items-center gap-1.5 text-xs text-red-400">
            <span className="w-1.5 h-1.5 rounded-full bg-red-400 animate-pulse" />
            Check!
          </div>
        )}
      </div>
    </div>
  );
}

// ─── Sub-components ───────────────────────────────────────────

function StatusIndicator({ gameState }: { gameState: GameState }) {
  const { isGameOver, isCheckmate, isStalemate, isCheck, isThinking } = gameState;

  if (isCheckmate) {
    return <span className="badge-red">Checkmate</span>;
  }
  if (isStalemate) {
    return <span className="badge-yellow">Stalemate</span>;
  }
  if (isGameOver) {
    return <span className="badge-yellow">Draw</span>;
  }
  if (isThinking) {
    return (
      <span className="badge bg-brand-900/50 text-brand-300 border border-brand-700 animate-pulse">
        Thinking...
      </span>
    );
  }
  if (isCheck) {
    return <span className="badge-red">Check</span>;
  }
  return <span className="badge-green">Playing</span>;
}

function DifficultyBadge({ difficulty }: { difficulty: string }) {
  const colorMap: Record<string, string> = {
    easy: "badge-green",
    medium: "badge-yellow",
    hard: "badge-red",
  };
  return (
    <span className={colorMap[difficulty] ?? "badge-blue"}>
      {difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
    </span>
  );
}

function ScoreRow({
  icon,
  label,
  value,
  subtitle,
  normalize = false,
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  subtitle?: string;
  normalize?: boolean;
}) {
  const displayValue = normalize
    ? value.toFixed(3)
    : (value >= 0 ? "+" : "") + value.toFixed(3);

  const color =
    Math.abs(value) < 0.05
      ? "text-slate-400"
      : value > 0
      ? "text-emerald-400"
      : "text-red-400";

  return (
    <div className="flex items-center justify-between py-1.5 px-2 rounded-lg bg-surface hover:bg-surface-hover transition-colors">
      <div className="flex items-center gap-2">
        {icon}
        <div>
          <div className="text-xs font-medium text-slate-200">{label}</div>
          {subtitle && (
            <div className="text-xs text-muted">{subtitle}</div>
          )}
        </div>
      </div>
      <span className={clsx("text-sm font-mono font-semibold", color)}>
        {displayValue}
      </span>
    </div>
  );
}

function InfoRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between text-xs">
      <span className="text-muted">{label}</span>
      <span className="text-slate-300">{value}</span>
    </div>
  );
}

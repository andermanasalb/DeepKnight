/**
 * ML / analysis types for the frontend.
 */

export interface AnalysisState {
  classicalScore: number;
  pytorchScore: number;
  depthSearched: number;
  phase: string;
  materialBalance: number;
  legalMoveCount: number;
  isLoading: boolean;
}

export interface ScoreDisplay {
  value: number;
  label: string;
  color: string;
  interpretation: string;
}

/**
 * Convert a centipawn score to a human-readable advantage string.
 */
export function interpretScore(score: number): string {
  const abs = Math.abs(score);
  const side = score > 0 ? "White" : score < 0 ? "Black" : "";

  if (abs === 0) return "Equal position";
  if (abs < 0.3) return `${side} slightly better`;
  if (abs < 0.8) return `${side} is better`;
  if (abs < 2.0) return `${side} is clearly better`;
  if (abs < 5.0) return `${side} is winning`;
  return `${side} is completely winning`;
}

/**
 * Convert normalized score [-1, 1] to bar percentage [0, 100].
 * 50 = equal, >50 = White advantage, <50 = Black advantage.
 */
export function scoreToBarPercent(score: number): number {
  const clamped = Math.max(-1, Math.min(1, score));
  return ((clamped + 1) / 2) * 100;
}

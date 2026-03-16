/**
 * API request and response types.
 * Must stay in sync with backend Pydantic schemas.
 */

import type { Difficulty, PlayerColor } from "./chess";

// ─── Game API ────────────────────────────────────────────────

export interface NewGameRequest {
  difficulty: Difficulty;
}

export interface NewGameResponse {
  game_id: string;
  fen: string;
  turn: PlayerColor;
  difficulty: Difficulty;
  legal_moves: string[];
}

export interface MakeMoveRequest {
  fen: string;
  move_uci: string;
  difficulty: Difficulty;
  move_history?: string[];
}

export interface AnalysisInfo {
  classical_score: number;
  pytorch_score: number;
  depth_searched: number;
}

export interface MakeMoveResponse {
  player_move: string;
  player_move_san: string;
  ai_move: string | null;
  ai_move_san: string | null;
  fen: string;
  turn: PlayerColor;
  is_check: boolean;
  is_checkmate: boolean;
  is_stalemate: boolean;
  is_game_over: boolean;
  game_over_reason: string | null;
  pgn: string;
  legal_moves: string[];
  analysis: AnalysisInfo;
}

export interface BestMoveResponse {
  best_move: string;
  best_move_san: string;
  score: number;
  depth: number;
  nodes_searched: number;
}

// ─── Analysis API ────────────────────────────────────────────

export interface EvaluateRequest {
  fen: string;
}

export interface EvaluateResponse {
  classical_score: number;
  pytorch_score: number;
  turn: PlayerColor;
  material_balance: number;
  phase: string;
  is_check: boolean;
  legal_move_count: number;
}

// ─── Coach API ───────────────────────────────────────────────

export interface HintRequest {
  fen: string;
  player_color: PlayerColor;
  move_history: string[];
  difficulty: Difficulty;
}

export interface HintResponse {
  hint: string;
  suggested_concept: string;
  tokens_used: number;
}

export interface ExplainMoveRequest {
  fen: string;
  ai_move: string;
  ai_move_san: string;
  move_history: string[];
  difficulty: Difficulty;
}

export interface ExplainMoveResponse {
  explanation: string;
  themes: string[];
  tokens_used: number;
}

export interface PostGameRequest {
  pgn: string;
  difficulty: Difficulty;
  player_color: PlayerColor;
  result: string;
}

export interface MistakeInfo {
  move_number: number;
  move: string;
  issue: string;
  severity: "blunder" | "mistake" | "inaccuracy";
}

export interface PostGameResponse {
  summary: string;
  mistakes: MistakeInfo[];
  key_moments: string[];
  improvement_areas: string[];
  opening_name: string;
  tokens_used: number;
}

export interface ChatRequest {
  message: string;
  fen?: string;
  move_history?: string[];
  context?: string;
}

export interface ChatResponse {
  response: string;
  tokens_used: number;
}

// ─── Error ───────────────────────────────────────────────────

export interface ApiError {
  detail: string;
  error_code?: string;
}

/**
 * Chess domain types.
 */

export type Difficulty = "easy" | "medium" | "hard";
export type PlayerColor = "white" | "black";
export type GamePhase = "opening" | "middlegame" | "endgame";
export type GameStatus =
  | "waiting"
  | "in_progress"
  | "checkmate"
  | "stalemate"
  | "draw"
  | "game_over";
export type GameOverReason =
  | "checkmate"
  | "stalemate"
  | "insufficient_material"
  | "seventy_five_moves"
  | "fivefold_repetition"
  | null;

export interface Move {
  uci: string;
  san: string;
  player: PlayerColor;
  moveNumber: number;
}

export interface GameState {
  gameId: string | null;
  fen: string;
  turn: PlayerColor;
  difficulty: Difficulty;
  legalMoves: string[];
  isCheck: boolean;
  isCheckmate: boolean;
  isStalemate: boolean;
  isGameOver: boolean;
  gameOverReason: GameOverReason;
  pgn: string;
  moveHistory: Move[];
  isThinking: boolean;
  lastAiMove: string | null;
  lastAiMoveSan: string | null;
}

export const STARTING_FEN =
  "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1";

export const DIFFICULTY_LABELS: Record<Difficulty, string> = {
  easy: "Easy",
  medium: "Medium",
  hard: "Hard",
};

export const DIFFICULTY_DESCRIPTIONS: Record<Difficulty, string> = {
  easy: "Shallow search · Random moves · Beatable",
  medium: "Alpha-beta pruning · Move ordering · Challenging",
  hard: "Deep search · Neural evaluation · Best play",
};

/**
 * Centralized API service layer.
 * All backend calls go through this module.
 */

import axios, { AxiosError } from "axios";
import type {
  BestMoveResponse,
  ChatRequest,
  ChatResponse,
  EvaluateRequest,
  EvaluateResponse,
  ExplainMoveRequest,
  ExplainMoveResponse,
  HintRequest,
  HintResponse,
  MakeMoveRequest,
  MakeMoveResponse,
  NewGameRequest,
  NewGameResponse,
  PostGameRequest,
  PostGameResponse,
} from "../types/api";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const apiClient = axios.create({
  baseURL: `${BASE_URL}/api/v1`,
  timeout: 30000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Response interceptor for consistent error handling
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    const message =
      (error.response?.data as { detail?: string })?.detail ||
      error.message ||
      "An unexpected error occurred";
    return Promise.reject(new Error(message));
  }
);

// ─── Game API ────────────────────────────────────────────────

export const gameApi = {
  newGame: async (request: NewGameRequest): Promise<NewGameResponse> => {
    const { data } = await apiClient.post<NewGameResponse>("/game/new_game", request);
    return data;
  },

  makeMove: async (request: MakeMoveRequest): Promise<MakeMoveResponse> => {
    const { data } = await apiClient.post<MakeMoveResponse>("/game/make_move", request);
    return data;
  },

  getBestMove: async (fen: string, difficulty: string): Promise<BestMoveResponse> => {
    const { data } = await apiClient.get<BestMoveResponse>("/game/best_move", {
      params: { fen, difficulty },
    });
    return data;
  },
};

// ─── Analysis API ────────────────────────────────────────────

export const analysisApi = {
  evaluate: async (request: EvaluateRequest): Promise<EvaluateResponse> => {
    const { data } = await apiClient.post<EvaluateResponse>("/analysis/evaluate", request);
    return data;
  },
};

// ─── Coach API ───────────────────────────────────────────────

export const coachApi = {
  getHint: async (request: HintRequest): Promise<HintResponse> => {
    const { data } = await apiClient.post<HintResponse>("/coach/hint", request);
    return data;
  },

  explainMove: async (request: ExplainMoveRequest): Promise<ExplainMoveResponse> => {
    const { data } = await apiClient.post<ExplainMoveResponse>("/coach/explain", request);
    return data;
  },

  postgameAnalysis: async (request: PostGameRequest): Promise<PostGameResponse> => {
    const { data } = await apiClient.post<PostGameResponse>("/coach/postgame", request);
    return data;
  },

  chat: async (request: ChatRequest): Promise<ChatResponse> => {
    const { data } = await apiClient.post<ChatResponse>("/coach/chat", request);
    return data;
  },
};

export default apiClient;

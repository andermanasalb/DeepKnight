/**
 * useAnalysis — fetch position evaluation on demand.
 */

import { useCallback, useState } from "react";
import { analysisApi } from "../services/api";
import type { EvaluateResponse } from "../types/api";

export interface UseAnalysisReturn {
  evaluation: EvaluateResponse | null;
  isLoading: boolean;
  error: string | null;
  evaluatePosition: (fen: string) => Promise<void>;
}

export function useAnalysis(): UseAnalysisReturn {
  const [evaluation, setEvaluation] = useState<EvaluateResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const evaluatePosition = useCallback(async (fen: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const result = await analysisApi.evaluate({ fen });
      setEvaluation(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Evaluation failed");
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { evaluation, isLoading, error, evaluatePosition };
}

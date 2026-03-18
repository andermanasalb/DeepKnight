import { useCallback, useEffect, useRef, useState } from "react";
import Header from "../components/Header";
import ChessBoard from "../components/ChessBoard";
import DifficultySelector from "../components/DifficultySelector";
import AnalysisPanel from "../components/AnalysisPanel";
import CoachChat from "../components/CoachChat";
import MoveHistory from "../components/MoveHistory";
import NewGameButton from "../components/NewGameButton";
import CyberLayout from "../components/CyberLayout";
import { useGame } from "../hooks/useGame";
import { useCoach } from "../hooks/useCoach";
import type { Difficulty } from "../types/chess";
import { AlertCircle, X, Shield, User } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export default function ChessGame() {
  const { gameState, analysis, error, startNewGame, makeMove, clearError } = useGame();
  const coachHook = useCoach();

  const [selectedDifficulty, setSelectedDifficulty] = useState<Difficulty>("medium");
  const [boardWidth, setBoardWidth] = useState(480);
  const boardContainerRef = useRef<HTMLDivElement>(null);

  // Responsive board size
  useEffect(() => {
    const observer = new ResizeObserver((entries) => {
      for (const entry of entries) {
        const width = entry.contentRect.width;
        const height = entry.contentRect.height;
        // Adjust width to fit both height and width of container
        const size = Math.min(width - 60, height - 200, 460);
        setBoardWidth(Math.max(280, size));
      }
    });

    if (boardContainerRef.current) {
      observer.observe(boardContainerRef.current);
    }

    return () => observer.disconnect();
  }, []);

  const moveHistoryUci = gameState.moveHistory.map((m) => m.uci);

  const handleNewGame = useCallback(async () => {
    await startNewGame(selectedDifficulty);
    coachHook.clearMessages();
  }, [selectedDifficulty, startNewGame, coachHook]);

  const handleMove = useCallback(
    async (moveUci: string) => {
      coachHook.clearSuggestedMove();
      await makeMove(moveUci);
    },
    [makeMove, coachHook]
  );

  useEffect(() => {
    if (!gameState.gameId) {
      startNewGame("medium");
    }
  }, []);

  return (
    <div className="min-h-screen xl:h-screen flex flex-col bg-slate-950 text-white xl:overflow-hidden selection:bg-neon-cyan/30">
      <Header />

      <AnimatePresence>
        {error && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="absolute top-20 left-1/2 -translate-x-1/2 z-[100] w-full max-w-xl px-4"
          >
            <div className="flex items-center gap-3 p-4 bg-black/80 backdrop-blur-xl border border-neon-red/50 shadow-neon-red/20 shadow-lg rounded text-sm text-neon-red">
              <AlertCircle size={18} className="shrink-0 animate-pulse" />
              <div className="flex-1">
                <span className="font-tech tracking-wider uppercase block text-[10px] mb-1 opacity-60">System Fault // Error_Core</span>
                <span className="font-medium">{error}</span>
              </div>
              <button
                onClick={clearError}
                className="p-1 hover:bg-white/5 transition-colors rounded"
              >
                <X size={18} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <CyberLayout
        leftPanel={
          <div className="flex flex-col h-full gap-3">
            <div className="space-y-2">
               <div className="flex items-center gap-2 px-1">
                 <div className="p-1.5 glass-panel border-neon-cyan/20">
                    <Shield size={13} className="text-neon-cyan" />
                 </div>
                 <div>
                   <h3 className="font-tech text-[10px] tracking-[0.2em] text-white uppercase">System Matrix</h3>
                   <span className="text-[8px] text-neon-cyan/40 font-tech uppercase tracking-widest leading-none">AI Control Node</span>
                 </div>
               </div>

               <DifficultySelector
                 value={selectedDifficulty}
                 onChange={setSelectedDifficulty}
                 disabled={gameState.isThinking}
               />

               <NewGameButton
                 onClick={handleNewGame}
                 isLoading={gameState.isThinking && !gameState.gameId}
                 label="Initiate Protocol"
               />
            </div>

            <div className="flex-1 min-h-0">
               <MoveHistory
                 moves={gameState.moveHistory}
                 pgn={gameState.pgn}
               />
            </div>
          </div>
        }
        rightPanel={
          <div className="flex flex-col h-full">
             <CoachChat
                coachHook={coachHook}
                gameState={gameState}
                moveHistoryUci={moveHistoryUci}
              />
          </div>
        }
        bottomPanel={
          <AnalysisPanel gameState={gameState} analysis={analysis} />
        }
      >
        <div ref={boardContainerRef} className="w-full h-full flex flex-col items-center justify-center relative p-3">
           {/* Background Grid Accent */}
           <div className="absolute inset-0 z-0 pointer-events-none opacity-20 bg-[radial-gradient(circle_at_center,rgba(0,229,255,0.05)_0%,transparent_70%)]" />

           {/* Initial load indicator */}
           {!gameState.gameId && (
             <div className="absolute inset-0 z-40 flex items-center justify-center bg-slate-950/80 backdrop-blur-sm">
               <div className="flex flex-col items-center gap-4">
                 <motion.div
                   animate={{ rotate: 360 }}
                   transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                   className="w-10 h-10 border-2 border-t-neon-cyan border-neon-cyan/20 rounded-full"
                 />
                 <span className="font-tech text-[10px] tracking-widest text-neon-cyan uppercase animate-pulse">
                   Initializing...
                 </span>
               </div>
             </div>
           )}

           <div className="relative z-10 flex flex-col items-center gap-5">
             {/* Player Top (AI) */}
             <motion.div 
               initial={{ opacity: 0, y: -10 }}
               animate={{ opacity: 1, y: 0 }}
               className="flex items-center gap-4 group shrink-0"
             >
                <div className="h-[1px] w-12 bg-gradient-to-r from-transparent to-white/10" />
                <div className="flex items-center gap-3 glass-panel border-white/5 px-4 py-2">
                   <div className="w-8 h-8 glass-panel border-neon-cyan/20 flex items-center justify-center bg-black/40">
                      <Shield size={14} className="text-neon-cyan opacity-60" />
                   </div>
                   <div className="flex flex-col">
                      <span className="font-tech text-[10px] tracking-[0.2em] text-white/40 uppercase">Opposition</span>
                      <span className="font-tech text-xs tracking-widest text-white group-hover:text-neon-cyan transition-colors">AI_ENTITY_{gameState.difficulty.toUpperCase()}</span>
                   </div>
                </div>
                <div className="h-[1px] w-12 bg-gradient-to-l from-transparent to-white/10" />
             </motion.div>

             {/* Board Container */}
             <div className="relative">
               <ChessBoard
                 gameState={gameState}
                 onMove={handleMove}
                 boardWidth={boardWidth}
                 suggestedMove={coachHook.suggestedMove}
               />
             </div>

             {/* Player Bottom (User) */}
             <motion.div 
               initial={{ opacity: 0, y: 10 }}
               animate={{ opacity: 1, y: 0 }}
               className="flex items-center gap-4 group shrink-0"
             >
                <div className="h-[1px] w-12 bg-gradient-to-r from-transparent to-white/10" />
                <div className="flex items-center gap-3 glass-panel border-white/10 px-4 py-2 bg-white/5 border-neon-cyan/30">
                   <div className="w-8 h-8 glass-panel border-neon-cyan flex items-center justify-center bg-neon-cyan/10">
                      <User size={14} className="text-neon-cyan" />
                   </div>
                   <div className="flex flex-col">
                      <span className="font-tech text-[10px] tracking-[0.2em] text-neon-cyan uppercase">Authorized User</span>
                      <span className="font-tech text-xs tracking-widest text-white uppercase">Commander_Unit_01</span>
                   </div>
                </div>
                <div className="h-[1px] w-12 bg-gradient-to-l from-transparent to-white/10" />
             </motion.div>
           </div>
        </div>
      </CyberLayout>
    </div>
  );
}


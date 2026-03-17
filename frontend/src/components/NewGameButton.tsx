import { RotateCcw } from "lucide-react";
import clsx from "clsx";
import { motion } from "framer-motion";

interface NewGameButtonProps {
  onClick: () => void;
  isLoading?: boolean;
  label?: string;
}

export default function NewGameButton({
  onClick,
  isLoading = false,
  label = "New Game",
}: NewGameButtonProps) {
  return (
    <button
      onClick={onClick}
      disabled={isLoading}
      className="relative group w-full outline-none"
    >
      <div className={clsx(
        "relative flex items-center justify-center gap-2 py-1 px-4 transition-all duration-300 overflow-hidden",
        "border border-neon-cyan/40 bg-neon-cyan/10 backdrop-blur-md",
        "group-hover:border-neon-cyan group-hover:bg-neon-cyan/20 group-active:scale-[0.98]",
        isLoading && "opacity-50 cursor-not-allowed border-white/10"
      )}>
        {/* Corner Accents */}
        <div className="absolute top-0 left-0 w-1 h-1 border-t border-l border-neon-cyan" />
        <div className="absolute top-0 right-0 w-1 h-1 border-t border-r border-neon-cyan" />
        <div className="absolute bottom-0 left-0 w-1 h-1 border-b border-l border-neon-cyan" />
        <div className="absolute bottom-0 right-0 w-1 h-1 border-b border-r border-neon-cyan" />

        <RotateCcw
          size={11}
          className={clsx(
            "text-neon-cyan transition-transform duration-500",
            isLoading ? "animate-spin" : "group-hover:rotate-180"
          )}
        />

        <span className="font-tech text-[9px] tracking-[0.25em] font-bold text-neon-cyan group-hover:text-white transition-colors uppercase">
          {isLoading ? "Synchronizing..." : label}
        </span>
      </div>

      {/* Outer Glow */}
      <div className="absolute -inset-[1px] bg-neon-cyan/20 blur-sm opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
    </button>
  );
}


import { RotateCcw } from "lucide-react";
import clsx from "clsx";

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
      className={clsx(
        "btn-primary w-full py-2.5 text-sm font-semibold shadow-glow",
        isLoading && "opacity-70 cursor-not-allowed"
      )}
    >
      <RotateCcw size={16} className={clsx(isLoading && "animate-spin")} />
      {isLoading ? "Starting..." : label}
    </button>
  );
}

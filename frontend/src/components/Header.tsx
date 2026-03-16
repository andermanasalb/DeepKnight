import { Brain, Github, Cpu } from "lucide-react";

export default function Header() {
  return (
    <header className="border-b border-surface-border glass sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-9 h-9 rounded-lg bg-brand-600">
              <span className="text-lg">♟️</span>
            </div>
            <div>
              <h1 className="text-lg font-bold gradient-text leading-tight">
                DeepKnight
              </h1>
              <p className="text-xs text-muted">
                Alpha-Beta · Neural Net · Gemini Coach
              </p>
            </div>
          </div>

          {/* Tech badges */}
          <div className="hidden md:flex items-center gap-2">
            <TechBadge icon={<Cpu size={12} />} label="Alpha-Beta" />
            <TechBadge icon={<Brain size={12} />} label="ValueNet" />
            <TechBadge icon={<span className="text-xs">✦</span>} label="Gemini" />
          </div>

          {/* Actions */}
          <div className="flex items-center gap-3">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="btn-ghost p-2 rounded-lg"
              aria-label="GitHub"
            >
              <Github size={18} />
            </a>
          </div>
        </div>
      </div>
    </header>
  );
}

function TechBadge({ icon, label }: { icon: React.ReactNode; label: string }) {
  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium bg-surface-border text-slate-300 border border-surface-border">
      {icon}
      {label}
    </span>
  );
}

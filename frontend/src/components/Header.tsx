import { Brain, Github, Cpu, Shield } from "lucide-react";

export default function Header() {
  return (
    <header className="border-b border-neon-cyan/20 bg-black/40 backdrop-blur-xl sticky top-0 z-50 overflow-hidden group">
      {/* Scanline Effect */}
      <div className="absolute inset-0 bg-scanline pointer-events-none opacity-5" />
      
      <div className="w-full px-3">
        <div className="flex items-center justify-between h-14">
          {/* Logo Area */}
          <div className="flex items-center gap-4">
            <div className="relative">
              <div className="flex items-center justify-center w-8 h-8 glass-panel border-neon-cyan/40 overflow-hidden">
                <Shield size={16} className="text-neon-cyan" />
                <div className="absolute inset-0 bg-neon-cyan/5 animate-pulse-cyan" />
              </div>
              {/* Decorative corner */}
              <div className="absolute -top-1 -left-1 w-2 h-2 border-t border-l border-neon-cyan/60" />
            </div>
            
            <div className="flex flex-col">
              <h1 className="font-tech text-sm tracking-[0.4em] text-white uppercase group-hover:neon-text transition-all">
                DEEP_KNIGHT <span className="text-neon-cyan">v2.0</span>
              </h1>
              <div className="flex items-center gap-2 mt-0.5">
                <span className="w-1 h-1 bg-neon-cyan rounded-full animate-pulse" />
                <span className="font-tech text-grow text-[8px] tracking-[0.2em] text-neon-cyan/60 uppercase">System Operational // Link Stable</span>
              </div>
            </div>
          </div>

          {/* Center Readouts */}
          <div className="hidden lg:flex items-center gap-8 font-tech text-[9px] tracking-[0.2em] text-white/40 uppercase">
            <div className="flex items-center gap-2">
              <Cpu size={10} className="text-neon-cyan/60" />
              <span>Core: Alpha-Beta</span>
            </div>
            <div className="w-[1px] h-3 bg-white/10" />
            <div className="flex items-center gap-2">
              <Brain size={10} className="text-neon-cyan/60" />
              <span>Neural: ValueNet_v4</span>
            </div>
            <div className="w-[1px] h-3 bg-white/10" />
            <div className="flex items-center gap-2">
              <span className="text-neon-cyan/60 text-[12px]">✦</span>
              <span>Coach: Gemini_Ultra</span>
            </div>
          </div>

          {/* Actions */}
          <div className="flex items-center gap-6">
            <div className="hidden sm:flex flex-col items-end mr-2">
               <span className="font-tech text-[8px] tracking-[0.2em] text-white/30 uppercase">Protocol</span>
               <span className="font-tech text-[10px] tracking-[0.1em] text-neon-cyan uppercase">Secure_Channel</span>
            </div>
            
            <a
              href="https://github.com/andermanasalb/DeepKnight"
              target="_blank"
              rel="noopener noreferrer"
              className="relative group/btn p-2 glass-panel border-white/5 hover:border-neon-cyan/40 transition-all overflow-hidden"
              aria-label="Access Source"
            >
              <Github size={16} className="text-white/60 group-hover/btn:text-neon-cyan transition-colors" />
              <div className="absolute inset-0 bg-neon-cyan/0 group-hover/btn:bg-neon-cyan/5 transition-colors" />
            </a>
          </div>
        </div>
      </div>

      {/* Ambient bottom glow */}
      <div className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1/3 h-[1px] bg-gradient-to-r from-transparent via-neon-cyan/20 to-transparent" />
    </header>
  );
}


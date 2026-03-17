import React from "react";
import { motion } from "framer-motion";

interface CyberLayoutProps {
  leftPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  bottomPanel: React.ReactNode;
  children: React.ReactNode;
}

export default function CyberLayout({
  leftPanel,
  rightPanel,
  bottomPanel,
  children,
}: CyberLayoutProps) {
  return (
    <div className="flex-1 w-full bg-slate-950 text-white overflow-auto xl:overflow-hidden flex flex-col relative select-none">
      {/* Background Decor */}
      <div className="absolute inset-0 bg-grid opacity-10 pointer-events-none" />

      {/* Main Container */}
      <main className="flex-1 min-h-0 grid grid-cols-1 xl:grid-cols-[260px_1fr_280px] p-2 xl:p-3 gap-2 xl:gap-3 relative z-10">
        {/* Left Sidebar */}
        <motion.aside
          initial={{ x: -20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex flex-col xl:h-full overflow-hidden order-2 xl:order-1"
        >
          <div className="flex-1 overflow-y-auto no-scrollbar glass-panel border-white/5 p-4">
             {leftPanel}
          </div>
        </motion.aside>

        {/* Center Canvas */}
        <motion.section
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.5 }}
          className="flex flex-col xl:h-full min-h-0 relative glass-panel border-white/5 overflow-hidden order-1 xl:order-2"
        >
          <div className="absolute inset-0 bg-scanline pointer-events-none opacity-5" />
          <div className="flex-1 min-h-0">
            {children}
          </div>
        </motion.section>

        {/* Right Sidebar */}
        <motion.aside
          initial={{ x: 20, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="flex flex-col xl:h-full overflow-hidden order-3"
        >
          <div className="flex-1 min-h-0 overflow-hidden glass-panel border-white/5 p-4">
            {rightPanel}
          </div>
        </motion.aside>
      </main>

      {/* Evaluation Zone */}
      <motion.footer
        initial={{ y: 20, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, delay: 0.4 }}
        className="px-3 pb-3 pt-1 relative z-10"
      >
        <div className="glass-panel border-white/5 p-3 bg-black/40 backdrop-blur-md">
          {bottomPanel}
        </div>
      </motion.footer>

      {/* Scanline & Noise Overlays */}
      <div className="absolute inset-0 pointer-events-none opacity-[0.03] bg-[url('https://grainy-gradients.vercel.app/noise.svg')] mix-blend-overlay" />
    </div>
  );
}


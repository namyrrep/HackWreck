
import React from 'react';

const Navbar: React.FC = () => {
  return (
    <nav className="sticky top-0 z-50 bg-slate-950/80 backdrop-blur-md border-b border-emerald-500/20">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-emerald-500 rounded flex items-center justify-center">
            <span className="text-slate-950 font-black text-xl">H</span>
          </div>
          <span className="text-xl font-black tracking-tighter text-white font-mono">
            HACK<span className="text-emerald-500">WRECK</span>
          </span>
        </div>
        
        <div className="hidden md:flex items-center space-x-8 font-mono text-sm">
          <a href="#add-hack" className="text-slate-300 hover:text-emerald-400 transition-colors uppercase tracking-widest text-xs">Add Hack</a>
          <a href="#optimize" className="text-slate-300 hover:text-amber-400 transition-colors uppercase tracking-widest text-xs">Optimize</a>
          <a href="#wreck" className="text-slate-300 hover:text-emerald-400 transition-colors uppercase tracking-widest text-xs">Wreck</a>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

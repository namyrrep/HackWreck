
import React from 'react';

const Hero: React.FC = () => {
  return (
    <section className="relative overflow-hidden pt-12 pb-4">
      <div className="text-center relative z-10">
        <div className="inline-block px-3 py-1 mb-6 border border-emerald-500/30 rounded-full bg-emerald-500/10 text-emerald-400 text-xs font-mono uppercase tracking-[0.2em] animate-pulse">
          Created by Edwin Barrack and William Perryman
        </div>
        <h1 className="text-5xl md:text-7xl font-black mb-6 tracking-tight text-white leading-tight">
          <span className="text-emerald-500">HACKS FOR</span> HACKERS <br />
          HACK <span className="text-emerald-500">WRECK</span>
        </h1>
        <p className="max-w-2xl mx-auto text-slate-400 text-lg md:text-xl font-light mb-10">
          HackWreck uses Gemini AI to Wrecommend Hacks for Hackers. 
        </p>
        <div className="flex flex-col sm:flex-row justify-center items-center space-y-4 sm:space-y-0 sm:space-x-4">
          <a href="#trends" className="w-full sm:w-auto px-8 py-3 bg-white text-slate-950 font-bold rounded-lg hover:bg-slate-200 transition-all uppercase text-sm">
            WRECK HACK
          </a>
        </div>
      </div>
      
      {/* Decorative background grid/lines */}
      <div className="absolute top-0 left-0 w-full h-full -z-10 opacity-20 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-emerald-500/10 blur-[120px] rounded-full"></div>
        <div className="h-full w-full bg-[linear-gradient(to_right,#1e293b_1px,transparent_1px),linear-gradient(to_bottom,#1e293b_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)]"></div>
      </div>
    </section>
  );
};

export default Hero;

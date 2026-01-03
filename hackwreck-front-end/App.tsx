
import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import AnalyzeSection from './components/AnalyzeSection';
import TrendsSection from './components/TrendsSection';
import AnalyzeProjectSection from './components/AnalyzeProjectSection';

const API_BASE_URL = 'http://localhost:8000';

interface Stats {
  total_projects: number;
  total_winners: number;
  total_participants: number;
  avg_winner_score: number;
}

const App: React.FC = () => {
  const [stats, setStats] = useState<Stats | null>(null);

  const fetchStats = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/stats`);
      if (response.ok) {
        const data = await response.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return (
    <div className="min-h-screen hacker-gradient">
      <Navbar />
      
      <main className="container mx-auto px-4 py-8 space-y-16">
        <Hero />
        
        <div id="analyze">
          <AnalyzeSection onComplete={() => fetchStats()} hackCount={stats?.total_projects || 0} />
        </div>

        <div id="optimize" className="scroll-mt-20">
          <AnalyzeProjectSection />
        </div>

        <div id="trends" className="scroll-mt-20">
          <TrendsSection />
        </div>
      </main>

      <footer className="border-t border-slate-800 py-8 mt-16 bg-slate-950">
        <div className="container mx-auto px-4 text-center text-slate-500 text-sm font-mono uppercase tracking-widest">
          <p>&copy; {new Date().getFullYear()} HACKWRECK.</p>
          <p className="mt-2 text-emerald-500/50">POWERED BY GEMINI 2.5 FLASH</p>
        </div>
      </footer>
    </div>
  );
};

export default App;

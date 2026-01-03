
import React, { useState, useEffect, useCallback } from 'react';
import Navbar from './components/Navbar';
import Hero from './components/Hero';
import AnalyzeSection from './components/AnalyzeSection';
import SearchSection from './components/SearchSection';
import { HackProject } from './types';

const API_BASE_URL = 'http://localhost:8000';

const App: React.FC = () => {
  const [projects, setProjects] = useState<HackProject[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchProjects = useCallback(async (query: string = '') => {
    setIsSearching(true);
    setError(null);
    try {
      const response = await fetch(`${API_BASE_URL}/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query }),
      });
      
      if (!response.ok) throw new Error('Failed to fetch projects');
      
      const data = await response.json();
      setProjects(data.projects || []);
    } catch (err) {
      console.error(err);
      setError('Could not connect to the backend server. Make sure FastAPI is running on port 8000.');
    } finally {
      setIsSearching(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="min-h-screen hacker-gradient">
      <Navbar />
      
      <main className="container mx-auto px-4 py-8 space-y-16">
        <Hero />
        
        <div id="analyze">
          <AnalyzeSection onComplete={() => fetchProjects()} />
        </div>

        <div id="search" className="scroll-mt-20">
          <SearchSection 
            projects={projects} 
            isSearching={isSearching} 
            onSearch={fetchProjects} 
            error={error}
          />
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


import React, { useState } from 'react';
import ProjectCard from './ProjectCard';
import { HackProject } from '../types';

interface SearchSectionProps {
  projects: HackProject[];
  isSearching: boolean;
  onSearch: (query: string) => void;
  error: string | null;
}

const SearchSection: React.FC<SearchSectionProps> = ({ projects, isSearching, onSearch, error }) => {
  const [query, setQuery] = useState('');

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(query);
  };

  return (
    <section className="space-y-10">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div>
          <h2 className="text-3xl font-bold text-white mb-2 font-mono uppercase tracking-tighter">
            HACK ARCHIVE
          </h2>
          <p className="text-slate-500 font-mono text-sm uppercase">TOTAL ENTRIES: {projects.length}</p>
        </div>

        <form onSubmit={handleSearch} className="flex-1 max-w-lg relative">
          <input 
            type="text"
            placeholder="Search by topic, framework, or keyword..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-full px-6 py-3 pl-12 text-white focus:outline-none focus:border-emerald-500 transition-all font-mono"
          />
          <svg className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <button 
            type="submit"
            className="absolute right-2 top-1/2 -translate-y-1/2 bg-emerald-500 text-slate-950 p-2 rounded-full hover:bg-emerald-400 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 5l7 7-7 7M5 5l7 7-7 7" />
            </svg>
          </button>
        </form>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/20 text-red-400 p-6 rounded-xl font-mono text-center">
          <p className="font-bold mb-2 uppercase">SYSTEM ERROR</p>
          <p className="text-sm opacity-80">{error}</p>
        </div>
      )}

      {isSearching ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
          {[1, 2, 3].map(n => (
            <div key={n} className="h-64 bg-slate-900/50 rounded-xl hacker-border"></div>
          ))}
        </div>
      ) : projects.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {projects.map((project) => (
            <ProjectCard key={project.id} project={project} />
          ))}
        </div>
      ) : (
        <div className="text-center py-20 bg-slate-900/20 rounded-xl hacker-border border-dashed">
          <p className="text-slate-500 font-mono italic">No Matches Found.</p>
        </div>
      )}
    </section>
  );
};

export default SearchSection;

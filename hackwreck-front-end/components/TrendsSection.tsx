
import React, { useState } from 'react';
import ReactMarkdown from 'react-markdown';

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

const TrendsSection: React.FC = () => {
  const [category, setCategory] = useState('');
  const [framework, setFramework] = useState('');
  const [description, setDescription] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysis, setAnalysis] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!category || !framework || !description) {
      setError('All fields are required');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setAnalysis(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/trends`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category, framework, description }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setAnalysis(data.analysis);
    } catch (err: any) {
      setError(`ERROR: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const isFormValid = category && framework && description;

  return (
    <div className="bg-slate-900/50 hacker-border rounded-xl p-6 md:p-10 hacker-glow">
      <div className="flex items-center space-x-3 mb-8">
        <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
        <h2 className="text-2xl font-bold font-mono text-emerald-500 uppercase tracking-tight">WRECK YOUR HACK</h2>
      </div>

      <p className="text-slate-400 text-sm font-mono mb-6">
        Plan your next hackathon project. Describe your idea and get AI-powered recommendations based on winning trends from our database.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-xs font-mono text-slate-500 uppercase tracking-widest">PROJECT CATEGORY</label>
            <input 
              type="text" 
              required
              placeholder="e.g., AI, FinTech, HealthTech, Education"
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 transition-all font-mono"
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-xs font-mono text-slate-500 uppercase tracking-widest">FRAMEWORK / TECHNOLOGIES</label>
            <input 
              type="text" 
              required
              placeholder="e.g., React, Python, TensorFlow, Node.js"
              value={framework}
              onChange={(e) => setFramework(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 transition-all font-mono"
            />
          </div>
        </div>

        <div className="space-y-2">
          <label className="text-xs font-mono text-slate-500 uppercase tracking-widest">PROJECT DESCRIPTION</label>
          <textarea 
            required
            rows={4}
            placeholder="Describe your hackathon project idea... What problem does it solve? What makes it unique?"
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-emerald-500 transition-all font-mono resize-none"
          />
        </div>

        <button 
          type="submit"
          disabled={isAnalyzing || !isFormValid}
          className={`w-full md:w-auto px-10 py-3 rounded-lg font-black font-mono flex items-center justify-center space-x-2 transition-all ${isAnalyzing || !isFormValid ? 'bg-slate-800 cursor-not-allowed text-slate-600' : 'bg-emerald-500 text-slate-950 hover:bg-emerald-400 shadow-lg shadow-emerald-500/20'}`}
        >
          {isAnalyzing ? (
            <>
              <svg className="animate-spin h-5 w-5 text-slate-400" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="uppercase">ANALYZING TRENDS...</span>
            </>
          ) : (
            <span className="uppercase">WRECK IT</span>
          )}
        </button>

        {error && (
          <div className="p-4 rounded-lg font-mono text-sm border bg-red-500/10 border-red-500/30 text-red-400">
            {error}
          </div>
        )}
      </form>

      {analysis && (
        <div className="mt-8 p-6 bg-slate-950 border border-emerald-500/30 rounded-lg">
          <div className="flex items-center space-x-2 mb-4">
            <h3 className="text-lg font-bold font-mono text-emerald-500 uppercase">AI ANALYSIS</h3>
          </div>
          <div className="prose prose-invert prose-emerald max-w-none text-slate-300 font-mono text-sm leading-relaxed">
            <ReactMarkdown 
              components={{
                a: ({ node, ...props }) => <a {...props} className="text-emerald-400 hover:text-emerald-300 underline" target="_blank" rel="noopener noreferrer" />,
                h2: ({ node, ...props }) => <h2 {...props} className="text-emerald-500 font-bold text-base mt-4 mb-2" />,
                h3: ({ node, ...props }) => <h3 {...props} className="text-slate-300 font-bold text-sm mt-3 mb-2" />,
                p: ({ node, ...props }) => <p {...props} className="mb-2" />,
                ul: ({ node, ...props }) => <ul {...props} className="list-disc list-inside mb-2" />,
                li: ({ node, ...props }) => <li {...props} className="mb-1" />,
                strong: ({ node, ...props }) => <strong {...props} className="text-white font-bold" />,
              }}
            >
              {analysis}
            </ReactMarkdown>
          </div>
        </div>
      )}
    </div>
  );
};

export default TrendsSection;

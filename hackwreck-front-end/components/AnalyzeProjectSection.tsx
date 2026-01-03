
import React, { useState } from 'react';

const API_BASE_URL = 'http://localhost:8000';

interface ProjectAnalysis {
  name: string;
  framework: string;
  topic: string;
  description: string;
  strengths: string[];
  weaknesses: string[];
  current_score: number;
}

interface RelatedWinner {
  name: string;
  framework: string;
  topic: string;
  score: number;
}

interface AnalysisResult {
  project_analysis: ProjectAnalysis;
  suggestions: string;
  related_winners: RelatedWinner[];
  hackathon_name: string;
  hackathon_theme: string;
}

const AnalyzeProjectSection: React.FC = () => {
  const [githubUrl, setGithubUrl] = useState('');
  const [hackathonName, setHackathonName] = useState('');
  const [hackathonTheme, setHackathonTheme] = useState('');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const validateGithub = (url: string) => {
    if (!url) return "GitHub URL is required";
    const regex = /^https?:\/\/(www\.)?github\.com\/[\w-]+\/[\w.-]+\/?$/;
    return regex.test(url) ? null : "Invalid GitHub URL format";
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const githubError = validateGithub(githubUrl);
    if (githubError || !hackathonName) {
      setError(githubError || 'Hackathon name is required');
      return;
    }

    setIsAnalyzing(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/analyze-project`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          github_url: githubUrl,
          hackathon_name: hackathonName,
          hackathon_theme: hackathonTheme
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      const data = await response.json();
      setResult(data);
    } catch (err: any) {
      setError(`ERROR: ${err.message}`);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const isFormValid = githubUrl && hackathonName && !validateGithub(githubUrl);

  return (
    <div className="bg-slate-900/50 hacker-border rounded-xl p-6 md:p-10 hacker-glow">
      <div className="flex items-center space-x-3 mb-8">
        <div className="w-3 h-3 bg-amber-500 rounded-full animate-pulse"></div>
        <h2 className="text-2xl font-bold font-mono text-amber-500 uppercase tracking-tight">OPTIMIZE YOUR PROJECT</h2>
      </div>

      <p className="text-slate-400 text-sm font-mono mb-6">
        Have an existing project? Get AI-powered suggestions on how to improve it for a specific hackathon based on winning trends.
      </p>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-2">
          <label className="text-xs font-mono text-slate-500 uppercase tracking-widest">YOUR GITHUB PROJECT URL</label>
          <input 
            type="text" 
            required
            placeholder="https://github.com/yourusername/your-project"
            value={githubUrl}
            onChange={(e) => setGithubUrl(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-amber-500 transition-all font-mono"
          />
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <label className="text-xs font-mono text-slate-500 uppercase tracking-widest">HACKATHON NAME</label>
            <input 
              type="text" 
              required
              placeholder="e.g., HackMIT, TreeHacks, PennApps"
              value={hackathonName}
              onChange={(e) => setHackathonName(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-amber-500 transition-all font-mono"
            />
          </div>
          
          <div className="space-y-2">
            <label className="text-xs font-mono text-slate-500 uppercase tracking-widest">HACKATHON THEME/TRACK (OPTIONAL)</label>
            <input 
              type="text" 
              placeholder="e.g., AI for Good, FinTech, Healthcare"
              value={hackathonTheme}
              onChange={(e) => setHackathonTheme(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-lg px-4 py-3 text-white focus:outline-none focus:border-amber-500 transition-all font-mono"
            />
          </div>
        </div>

        <button 
          type="submit"
          disabled={isAnalyzing || !isFormValid}
          className={`w-full md:w-auto px-10 py-3 rounded-lg font-black font-mono flex items-center justify-center space-x-2 transition-all ${isAnalyzing || !isFormValid ? 'bg-slate-800 cursor-not-allowed text-slate-600' : 'bg-amber-500 text-slate-950 hover:bg-amber-400 shadow-lg shadow-amber-500/20'}`}
        >
          {isAnalyzing ? (
            <>
              <svg className="animate-spin h-5 w-5 text-slate-400" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              <span className="uppercase">ANALYZING PROJECT...</span>
            </>
          ) : (
            <span className="uppercase">🚀 OPTIMIZE PROJECT</span>
          )}
        </button>

        {error && (
          <div className="p-4 rounded-lg font-mono text-sm border bg-red-500/10 border-red-500/30 text-red-400">
            {error}
          </div>
        )}
      </form>

      {result && (
        <div className="mt-8 space-y-6">
          {/* Project Summary Card */}
          <div className="p-6 bg-slate-950 border border-amber-500/30 rounded-lg">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center space-x-2">
                <span className="text-amber-500 text-lg">📊</span>
                <h3 className="text-lg font-bold font-mono text-amber-500 uppercase">PROJECT ANALYSIS</h3>
              </div>
              <div className="px-3 py-1 bg-amber-500/20 border border-amber-500/50 rounded-full">
                <span className="font-mono text-amber-400 font-bold">{result.project_analysis.current_score}/10</span>
              </div>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4 text-sm font-mono">
              <div>
                <span className="text-slate-500">Project:</span>
                <span className="text-white ml-2">{result.project_analysis.name}</span>
              </div>
              <div>
                <span className="text-slate-500">Category:</span>
                <span className="text-white ml-2">{result.project_analysis.topic}</span>
              </div>
              <div>
                <span className="text-slate-500">Framework:</span>
                <span className="text-white ml-2">{result.project_analysis.framework}</span>
              </div>
              <div>
                <span className="text-slate-500">Hackathon:</span>
                <span className="text-amber-400 ml-2">{result.hackathon_name}</span>
              </div>
            </div>

            <div className="mt-4 grid md:grid-cols-2 gap-4">
              <div>
                <h4 className="text-xs font-mono text-emerald-500 uppercase mb-2">STRENGTHS</h4>
                <ul className="space-y-1">
                  {result.project_analysis.strengths?.map((s, i) => (
                    <li key={i} className="text-sm text-slate-300 font-mono flex items-start">
                      <span className="text-emerald-500 mr-2">+</span>{s}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className="text-xs font-mono text-red-500 uppercase mb-2">WEAKNESSES</h4>
                <ul className="space-y-1">
                  {result.project_analysis.weaknesses?.map((w, i) => (
                    <li key={i} className="text-sm text-slate-300 font-mono flex items-start">
                      <span className="text-red-500 mr-2">-</span>{w}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Related Winners */}
          {result.related_winners.length > 0 && (
            <div className="p-6 bg-slate-950 border border-slate-700 rounded-lg">
              <div className="flex items-center space-x-2 mb-4">
                <span className="text-emerald-500 text-lg">🏆</span>
                <h3 className="text-lg font-bold font-mono text-slate-300 uppercase">SIMILAR WINNING PROJECTS</h3>
              </div>
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-3">
                {result.related_winners.map((winner, i) => (
                  <div key={i} className="p-3 bg-slate-900 border border-slate-800 rounded-lg">
                    <div className="font-mono text-sm text-white font-bold truncate">{winner.name}</div>
                    <div className="text-xs text-slate-500 font-mono mt-1">{winner.topic}</div>
                    <div className="flex justify-between items-center mt-2">
                      <span className="text-xs text-slate-500 font-mono">{winner.framework}</span>
                      <span className="text-xs font-mono text-emerald-400">{winner.score}/10</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Suggestions */}
          <div className="p-6 bg-slate-950 border border-emerald-500/30 rounded-lg">
            <div className="flex items-center space-x-2 mb-4">
              <span className="text-emerald-500 text-lg">💡</span>
              <h3 className="text-lg font-bold font-mono text-emerald-500 uppercase">IMPROVEMENT PLAN</h3>
            </div>
            <div className="prose prose-invert prose-emerald max-w-none">
              <div className="text-slate-300 font-mono text-sm leading-relaxed whitespace-pre-wrap">
                {result.suggestions}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalyzeProjectSection;

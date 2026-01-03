
import React, { useState, useEffect } from 'react';

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

interface AnalyzeSectionProps {
  onComplete: () => void;
  hackCount: number;
}

const AnalyzeSection: React.FC<AnalyzeSectionProps> = ({ onComplete, hackCount }) => {
  const [githubUrl, setGithubUrl] = useState('');
  const [devpostUrl, setDevpostUrl] = useState('');
  const [status, setStatus] = useState<'win' | 'lose'>('lose');
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  
  // Validation state
  const [githubError, setGithubError] = useState<string | null>(null);
  const [devpostError, setDevpostError] = useState<string | null>(null);

  const validateGithub = (url: string) => {
    if (!url) return "GitHub URL is required";
    const regex = /^https?:\/\/(www\.)?github\.com\/[\w-]+\/[\w.-]+\/?$/;
    return regex.test(url) ? null : "Invalid GitHub repository format (e.g., https://github.com/user/repo)";
  };

  const validateDevpost = (url: string) => {
    if (!url) return null; // Optional field
    const regex = /^https?:\/\/(www\.)?devpost\.com\/software\/[\w-]+\/?$/;
    return regex.test(url) ? null : "Invalid Devpost format (e.g., https://devpost.com/software/project-name)";
  };

  useEffect(() => {
    if (githubUrl) setGithubError(validateGithub(githubUrl));
    else setGithubError(null);
  }, [githubUrl]);

  useEffect(() => {
    if (devpostUrl) setDevpostError(validateDevpost(devpostUrl));
    else setDevpostError(null);
  }, [devpostUrl]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    const gError = validateGithub(githubUrl);
    const dError = validateDevpost(devpostUrl);
    
    if (gError || dError) {
      setGithubError(gError);
      setDevpostError(dError);
      return;
    }

    setIsAnalyzing(true);
    setMessage(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/insert`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          github_url: githubUrl, 
          status: status === 'win' ? 'Winner' : 'Participant' 
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Analysis failed');
      }

      setMessage({ type: 'success', text: 'PROJECT ANALYZED AND ARCHIVED SUCCESSFULLY.' });
      setGithubUrl('');
      setDevpostUrl('');
      onComplete();
    } catch (err: any) {
      setMessage({ type: 'error', text: `ERROR: ${err.message}` });
    } finally {
      setIsAnalyzing(false);
    }
  };

  const isFormInvalid = !!validateGithub(githubUrl) || (!!devpostUrl && !!validateDevpost(devpostUrl));

  return (
    <div className="bg-slate-900/50 hacker-border rounded-xl p-6 md:p-10 hacker-glow">
      <div className="flex items-center justify-between mb-8">
        <div className="flex items-center space-x-3">
          <div className="w-3 h-3 bg-emerald-500 rounded-full animate-pulse"></div>
          <h2 className="text-2xl font-bold font-mono text-emerald-500 uppercase tracking-tight">ADD A HACK</h2>
        </div>
        <div className="flex items-center space-x-2 px-3 py-1.5 bg-slate-950 border border-emerald-500/30 rounded-lg">
          <span className="text-emerald-500 font-mono font-bold text-lg">{hackCount}</span>
          <span className="text-slate-400 font-mono text-xs uppercase">hacks stored</span>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="grid md:grid-cols-2 gap-6">
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-xs font-mono text-slate-500 uppercase tracking-widest">GITHUB REPOSITORY URL</label>
              {githubUrl && !githubError && <span className="text-[10px] font-mono text-emerald-500 uppercase">Valid Link</span>}
            </div>
            <input 
              type="text" 
              required
              placeholder="https://github.com/user/repo"
              value={githubUrl}
              onChange={(e) => setGithubUrl(e.target.value)}
              className={`w-full bg-slate-950 border rounded-lg px-4 py-3 text-white focus:outline-none transition-all font-mono ${githubError ? 'border-red-500/50 focus:border-red-500' : 'border-slate-800 focus:border-emerald-500'}`}
            />
            {githubError && <p className="text-[10px] font-mono text-red-400 mt-1 uppercase">{githubError}</p>}
          </div>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <label className="text-xs font-mono text-slate-500 uppercase tracking-widest">DEVPOST LINK (OPTIONAL)</label>
              {devpostUrl && !devpostError && <span className="text-[10px] font-mono text-emerald-500 uppercase">Valid Link</span>}
            </div>
            <input 
              type="text" 
              placeholder="https://devpost.com/software/slug"
              value={devpostUrl}
              onChange={(e) => setDevpostUrl(e.target.value)}
              className={`w-full bg-slate-950 border rounded-lg px-4 py-3 text-white focus:outline-none transition-all font-mono ${devpostError ? 'border-red-500/50 focus:border-red-500' : 'border-slate-800 focus:border-emerald-500'}`}
            />
            {devpostError && <p className="text-[10px] font-mono text-red-400 mt-1 uppercase">{devpostError}</p>}
          </div>
        </div>

        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div className="space-y-2">
            <label className="text-xs font-mono text-slate-500 uppercase tracking-widest">HACKATHON STATUS</label>
            <div className="flex p-1 bg-slate-950 rounded-lg border border-slate-800 w-fit">
              <button 
                type="button"
                onClick={() => setStatus('win')}
                className={`px-6 py-2 rounded-md font-mono text-sm transition-all ${status === 'win' ? 'bg-emerald-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white'}`}
              >
                WINNER
              </button>
              <button 
                type="button"
                onClick={() => setStatus('lose')}
                className={`px-6 py-2 rounded-md font-mono text-sm transition-all ${status === 'lose' ? 'bg-slate-800 text-white font-bold' : 'text-slate-400 hover:text-white'}`}
              >
                PARTICIPANT
              </button>
            </div>
          </div>

          <button 
            type="submit"
            disabled={isAnalyzing || isFormInvalid}
            className={`w-full md:w-auto px-10 py-3 rounded-lg font-black font-mono flex items-center justify-center space-x-2 transition-all ${isAnalyzing || isFormInvalid ? 'bg-slate-800 cursor-not-allowed text-slate-600' : 'bg-emerald-500 text-slate-950 hover:bg-emerald-400 shadow-lg shadow-emerald-500/20'}`}
          >
            {isAnalyzing ? (
              <>
                <svg className="animate-spin h-5 w-5 text-slate-400" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="uppercase">Entering...</span>
              </>
            ) : (
              <span className="uppercase">ADD ENTRY</span>
            )}
          </button>
        </div>

        {message && (
          <div className={`p-4 rounded-lg font-mono text-sm border ${message.type === 'success' ? 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400' : 'bg-red-500/10 border-red-500/30 text-red-400'}`}>
            {message.text}
          </div>
        )}
      </form>
    </div>
  );
};

export default AnalyzeSection;

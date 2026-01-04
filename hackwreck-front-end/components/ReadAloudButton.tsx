
import React, { useState, useRef } from 'react';

const API_BASE_URL = (import.meta.env.VITE_API_URL || 'http://localhost:8000').replace(/\/+$/, '');

interface ReadAloudButtonProps {
  text: string;
  accentColor?: 'emerald' | 'amber';
}

const ReadAloudButton: React.FC<ReadAloudButtonProps> = ({ text, accentColor = 'emerald' }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  const colorClasses = accentColor === 'amber' 
    ? 'border-amber-500/30 bg-amber-500/10 text-amber-400 hover:bg-amber-500/20 focus:ring-amber-500'
    : 'border-emerald-500/30 bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 focus:ring-emerald-500';

  const handleReadAloud = async () => {
    // If already playing, stop
    if (isPlaying && audioRef.current) {
      audioRef.current.pause();
      audioRef.current.currentTime = 0;
      setIsPlaying(false);
      return;
    }

    // Limit text to ~4000 chars for API limits
    const truncatedText = text.slice(0, 4000);

    if (!truncatedText.trim()) {
      return;
    }

    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/text-to-speech`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: truncatedText }),
      });

      if (!response.ok) {
        throw new Error('TTS request failed');
      }

      const audioBlob = await response.blob();
      const audioUrl = URL.createObjectURL(audioBlob);

      // Clean up previous audio
      if (audioRef.current) {
        audioRef.current.pause();
        URL.revokeObjectURL(audioRef.current.src);
      }

      const audio = new Audio(audioUrl);
      audioRef.current = audio;

      audio.onended = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
      };

      audio.onerror = () => {
        setIsPlaying(false);
        URL.revokeObjectURL(audioUrl);
      };

      await audio.play();
      setIsPlaying(true);
    } catch (err) {
      console.error('Read aloud error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <button
      type="button"
      onClick={handleReadAloud}
      disabled={isLoading}
      aria-label={isPlaying ? 'Stop reading' : 'Read aloud'}
      className={`flex items-center space-x-2 px-4 py-2 rounded-lg border focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-offset-slate-950 transition-all text-xs font-mono uppercase tracking-widest disabled:opacity-50 ${colorClasses}`}
    >
      {isLoading ? (
        <svg className="animate-spin h-4 w-4" viewBox="0 0 24 24">
          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
        </svg>
      ) : isPlaying ? (
        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
          <rect x="6" y="4" width="4" height="16" />
          <rect x="14" y="4" width="4" height="16" />
        </svg>
      ) : (
        <svg className="h-4 w-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M3 9v6h4l5 5V4L7 9H3zm13.5 3c0-1.77-1.02-3.29-2.5-4.03v8.05c1.48-.73 2.5-2.25 2.5-4.02zM14 3.23v2.06c2.89.86 5 3.54 5 6.71s-2.11 5.85-5 6.71v2.06c4.01-.91 7-4.49 7-8.77s-2.99-7.86-7-8.77z" />
        </svg>
      )}
      <span>{isLoading ? 'Loading...' : isPlaying ? 'Stop' : 'Read Aloud'}</span>
    </button>
  );
};

export default ReadAloudButton;

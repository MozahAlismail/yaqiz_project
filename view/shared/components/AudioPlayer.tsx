import React from 'react';
import { AudioPlayerState } from '../types';
import { IconPlay, IconPause, IconVolume, IconVolumeMute } from '../icons';

interface AudioPlayerProps {
  state: AudioPlayerState;
  onPlayPause: () => void;
  onSeek: (time: number) => void;
  onVolumeChange: (volume: number) => void;
  onMuteToggle: () => void;
  showWaveform?: boolean;
  className?: string;
  ariaLabel?: string;
}

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

export const AudioPlayer: React.FC<AudioPlayerProps> = ({
  state,
  onPlayPause,
  onSeek,
  onVolumeChange,
  onMuteToggle,
  showWaveform = true,
  className = '',
  ariaLabel,
}) => {
  const progress = state.duration > 0 ? (state.currentTime / state.duration) * 100 : 0;

  return (
    <div
      className={`bg-gray-50 rounded-lg p-4 ${className}`}
      role="region"
      aria-label={ariaLabel || 'Audio player'}
    >
      <div className="flex items-center gap-4">
        <button
          type="button"
          onClick={onPlayPause}
          className="flex-shrink-0 w-10 h-10 flex items-center justify-center rounded-full bg-[#0b5ac1] text-white hover:bg-[#0948a3] transition-colors"
          aria-label={state.isPlaying ? 'Pause' : 'Play'}
        >
          {state.isPlaying ? <IconPause size={20} /> : <IconPlay size={20} />}
        </button>

        <div className="flex-1">
          {showWaveform && (
            <div className="flex items-center gap-0.5 h-8 mb-2">
              {Array.from({ length: 40 }).map((_, i) => (
                <div
                  key={i}
                  className={`
                    w-1 rounded-full transition-all duration-150
                    ${i < (progress / 100) * 40 ? 'bg-[#0b5ac1]' : 'bg-gray-300'}
                  `}
                  style={{
                    height: `${Math.random() * 60 + 40}%`,
                  }}
                />
              ))}
            </div>
          )}

          <div className="relative">
            <input
              type="range"
              min={0}
              max={state.duration || 100}
              value={state.currentTime}
              onChange={(e) => onSeek(Number(e.target.value))}
              className="w-full h-1 rounded-full appearance-none bg-gray-200 cursor-pointer
                [&::-webkit-slider-thumb]:appearance-none
                [&::-webkit-slider-thumb]:w-3
                [&::-webkit-slider-thumb]:h-3
                [&::-webkit-slider-thumb]:rounded-full
                [&::-webkit-slider-thumb]:bg-[#0b5ac1]"
              aria-label="Seek"
            />
          </div>

          <div className="flex justify-between mt-1 text-xs text-gray-500">
            <span>{formatTime(state.currentTime)}</span>
            <span>{formatTime(state.duration)}</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onMuteToggle}
            className="p-2 text-gray-500 hover:text-gray-700 transition-colors"
            aria-label={state.isMuted ? 'Unmute' : 'Mute'}
          >
            {state.isMuted ? <IconVolumeMute size={20} /> : <IconVolume size={20} />}
          </button>
          <input
            type="range"
            min={0}
            max={100}
            value={state.isMuted ? 0 : state.volume}
            onChange={(e) => onVolumeChange(Number(e.target.value))}
            className="w-16 h-1 rounded-full appearance-none bg-gray-200 cursor-pointer
              [&::-webkit-slider-thumb]:appearance-none
              [&::-webkit-slider-thumb]:w-2
              [&::-webkit-slider-thumb]:h-2
              [&::-webkit-slider-thumb]:rounded-full
              [&::-webkit-slider-thumb]:bg-gray-600"
            aria-label="Volume"
          />
        </div>
      </div>
    </div>
  );
};

export default AudioPlayer;

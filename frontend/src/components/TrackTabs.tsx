import type { Track } from '../types/api';

interface TrackTabsProps {
  activeTrack: Track;
  onChange: (track: Track) => void;
}

const tracks: Array<{ key: Track; label: string; subtitle: string }> = [
  { key: 'python_backend', label: 'Python Backend', subtitle: 'Вакансии API/Server' },
  { key: 'swift', label: 'Swift', subtitle: 'Вакансии iOS/macOS' }
];

export function TrackTabs({ activeTrack, onChange }: TrackTabsProps): JSX.Element {
  return (
    <div className="tabs" role="tablist" aria-label="Выбор направления">
      {tracks.map((track) => (
        <button
          key={track.key}
          className={`tab ${activeTrack === track.key ? 'active' : ''}`}
          onClick={() => onChange(track.key)}
          role="tab"
          aria-selected={activeTrack === track.key}
        >
          <span className="tab-title">{track.label}</span>
          <span className="tab-subtitle">{track.subtitle}</span>
        </button>
      ))}
    </div>
  );
}

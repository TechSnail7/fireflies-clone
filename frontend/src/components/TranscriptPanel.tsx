'use client';

import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import {
  Search, Play, Pause, SkipBack, SkipForward,
  Volume2, VolumeX, ChevronUp, ChevronDown,
  X, FileText
} from 'lucide-react';
import { TranscriptSegment } from '@/lib/api';
import styles from './TranscriptPanel.module.css';

interface TranscriptPanelProps {
  segments: TranscriptSegment[];
  videoUrl?: string;
}

// Speaker colour palette — deterministic mapping from speaker name
const SPEAKER_COLORS = [
  '#818cf8', // indigo
  '#f59e0b', // amber
  '#10b981', // emerald
  '#f43f5e', // rose
  '#7c3aed', // purple
  '#06b6d4', // cyan
  '#ec4899', // pink
  '#14b8a6', // teal
];

function speakerColor(name: string): string {
  let hash = 0;
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash);
  return SPEAKER_COLORS[Math.abs(hash) % SPEAKER_COLORS.length];
}

// ── Waveform bars — pre-generated random heights ──────────────────
const WAVEFORM_HEIGHTS = Array.from({ length: 40 }, () => 8 + Math.random() * 28);

export default function TranscriptPanel({ segments, videoUrl }: TranscriptPanelProps) {
  // ── Player State ──────────────────────────────────────────────
  const [currentTime, setCurrentTime] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [duration, setDuration] = useState(0);
  const [volume, setVolume] = useState(0.8);
  const [isMuted, setIsMuted] = useState(false);
  const [playbackRate, setPlaybackRate] = useState(1);
  const videoRef = useRef<HTMLVideoElement>(null);
  const hasVideo = !!videoUrl;

  // ── Search State ──────────────────────────────────────────────
  const [searchQuery, setSearchQuery] = useState('');
  const [activeMatchIdx, setActiveMatchIdx] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);
  const segmentRefs = useRef<Map<number, HTMLDivElement>>(new Map());

  // ── Derived: filtered segments & match info ────────────────────
  const { filteredSegments, matchingIds } = useMemo(() => {
    if (!searchQuery.trim()) return { filteredSegments: segments, matchingIds: new Set<number>() };
    const q = searchQuery.toLowerCase();
    const matches = segments.filter(
      (s) => s.text.toLowerCase().includes(q) || s.speaker.toLowerCase().includes(q)
    );
    return { filteredSegments: matches, matchingIds: new Set(matches.map((s) => s.id)) };
  }, [segments, searchQuery]);

  // ── Duration init ──────────────────────────────────────────────
  useEffect(() => {
    if (!videoRef.current && segments.length > 0) {
      setDuration(segments[segments.length - 1].end_time);
    }
  }, [segments]);

  // ── Playback sync ─────────────────────────────────────────────
  useEffect(() => {
    const vid = videoRef.current;
    let interval: ReturnType<typeof setInterval>;

    if (isPlaying) {
      vid?.play().catch(() => {});
      interval = setInterval(() => {
        if (vid) {
          setCurrentTime(vid.currentTime);
          if (vid.ended) setIsPlaying(false);
        } else {
          setCurrentTime((prev) => {
            if (prev >= duration) { setIsPlaying(false); return duration; }
            return prev + 0.25;
          });
        }
      }, 250);
    } else {
      vid?.pause();
    }

    return () => clearInterval(interval);
  }, [isPlaying, duration]);

  // ── Volume sync ───────────────────────────────────────────────
  useEffect(() => {
    if (videoRef.current) {
      videoRef.current.volume = isMuted ? 0 : volume;
    }
  }, [volume, isMuted]);

  // ── Playback rate ─────────────────────────────────────────────
  useEffect(() => {
    if (videoRef.current) videoRef.current.playbackRate = playbackRate;
  }, [playbackRate]);

  // ── Auto-scroll active segment ────────────────────────────────
  useEffect(() => {
    if (searchQuery) return; // don't auto-scroll while searching
    const activeIdx = segments.findIndex(
      (s) => currentTime >= s.start_time && currentTime < s.end_time
    );
    if (activeIdx >= 0) {
      const el = segmentRefs.current.get(segments[activeIdx].id);
      el?.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    }
  }, [currentTime, segments, searchQuery]);

  // ── Scroll to active search match ─────────────────────────────
  useEffect(() => {
    if (filteredSegments.length > 0 && searchQuery) {
      const seg = filteredSegments[activeMatchIdx];
      if (seg) {
        const el = segmentRefs.current.get(seg.id);
        el?.scrollIntoView({ behavior: 'smooth', block: 'center' });
      }
    }
  }, [activeMatchIdx, filteredSegments, searchQuery]);

  // ── Helpers ───────────────────────────────────────────────────
  const formatTime = (seconds: number) => {
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) return `${h}:${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
  };

  const seekTo = useCallback((time: number) => {
    setCurrentTime(time);
    if (videoRef.current) videoRef.current.currentTime = time;
  }, []);

  const handleSegmentClick = useCallback((startTime: number) => {
    seekTo(startTime);
    setIsPlaying(true);
  }, [seekTo]);

  const togglePlayPause = useCallback(() => setIsPlaying((p) => !p), []);

  const cyclePlaybackRate = useCallback(() => {
    const rates = [0.5, 0.75, 1, 1.25, 1.5, 2];
    const idx = rates.indexOf(playbackRate);
    setPlaybackRate(rates[(idx + 1) % rates.length]);
  }, [playbackRate]);

  const skipBy = useCallback((delta: number) => {
    seekTo(Math.max(0, Math.min(duration, currentTime + delta)));
  }, [currentTime, duration, seekTo]);

  // ── Search nav ────────────────────────────────────────────────
  const goNextMatch = () => setActiveMatchIdx((i) => (i + 1) % filteredSegments.length);
  const goPrevMatch = () => setActiveMatchIdx((i) => (i - 1 + filteredSegments.length) % filteredSegments.length);

  // ── Highlight helper ──────────────────────────────────────────
  const renderHighlightedText = (text: string, query: string, isActiveMatch: boolean) => {
    if (!query.trim()) return <span>{text}</span>;
    // Escape regex special chars in query
    const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const parts = text.split(new RegExp(`(${escaped})`, 'gi'));
    return (
      <span>
        {parts.map((part, i) =>
          part.toLowerCase() === query.toLowerCase() ? (
            <mark
              key={i}
              className={`${styles.highlight} ${isActiveMatch ? styles.highlightActive : ''}`}
            >
              {part}
            </mark>
          ) : (
            <span key={i}>{part}</span>
          )
        )}
      </span>
    );
  };

  // ── Progress percentage ───────────────────────────────────────
  const progressPct = duration > 0 ? (currentTime / duration) * 100 : 0;

  // ── Display segments — show all but mark matches ──────────────
  const displaySegments = searchQuery ? filteredSegments : segments;

  return (
    <div className={styles.panel}>
      {/* ── Media Area ─────────────────────────────────────────── */}
      <div className={styles.mediaArea}>
        {hasVideo ? (
          <div className={styles.videoContainer}>
            <video
              ref={videoRef}
              src={videoUrl}
              className={styles.videoPlayer}
              onLoadedMetadata={() => setDuration(videoRef.current?.duration || duration)}
              onTimeUpdate={() => {
                if (videoRef.current) setCurrentTime(videoRef.current.currentTime);
              }}
              onClick={togglePlayPause}
            />
            <div className={styles.videoOverlay}>
              <div className={styles.overlayPlayBtn}>
                {isPlaying ? <Pause size={24} /> : <Play size={24} />}
              </div>
            </div>
          </div>
        ) : (
          <div className={styles.audioPlaceholder}>
            <div className={`${styles.waveformBars} ${isPlaying ? styles.waveformPlaying : ''}`}>
              {WAVEFORM_HEIGHTS.map((h, i) => {
                const barPct = (i / WAVEFORM_HEIGHTS.length) * 100;
                return (
                  <div
                    key={i}
                    className={`${styles.waveformBar} ${barPct <= progressPct ? styles.activeBar : ''}`}
                    style={{ height: `${h}px` }}
                  />
                );
              })}
            </div>
          </div>
        )}

        {/* ── Controls Row ──────────────────────────────────────── */}
        <div className={styles.playerControls}>
          <button
            className={styles.controlBtn}
            onClick={() => skipBy(-10)}
            title="Back 10s"
          >
            <SkipBack size={18} />
          </button>
          <button
            className={`${styles.controlBtn} ${styles.playBtn}`}
            onClick={togglePlayPause}
            title={isPlaying ? 'Pause' : 'Play'}
          >
            {isPlaying ? <Pause size={18} /> : <Play size={18} />}
          </button>
          <button
            className={styles.controlBtn}
            onClick={() => skipBy(10)}
            title="Forward 10s"
          >
            <SkipForward size={18} />
          </button>

          <div className={styles.timeDisplay}>
            <span>{formatTime(currentTime)}</span>
            <span className={styles.timeDivider}>/</span>
            <span>{formatTime(duration)}</span>
          </div>

          <div style={{ flex: 1 }} />

          <button
            className={styles.speedBtn}
            onClick={cyclePlaybackRate}
            title="Playback Speed"
          >
            {playbackRate}x
          </button>

          <div className={styles.volumeGroup}>
            <button
              className={styles.controlBtn}
              onClick={() => setIsMuted((m) => !m)}
              title={isMuted ? 'Unmute' : 'Mute'}
            >
              {isMuted || volume === 0 ? <VolumeX size={18} /> : <Volume2 size={18} />}
            </button>
            <input
              type="range"
              min={0}
              max={1}
              step={0.01}
              value={isMuted ? 0 : volume}
              onChange={(e) => { setVolume(Number(e.target.value)); setIsMuted(false); }}
              className={styles.volumeSlider}
              title="Volume"
            />
          </div>
        </div>

        {/* ── Progress Bar ──────────────────────────────────────── */}
        <div className={styles.progressArea}>
          <div className={styles.progressTrack}>
            <div className={styles.progressFill} style={{ width: `${progressPct}%` }} />
            <div className={styles.progressThumb} style={{ left: `${progressPct}%` }} />
            <input
              type="range"
              min={0}
              max={duration || 1}
              step={0.1}
              value={currentTime}
              onChange={(e) => seekTo(Number(e.target.value))}
              className={styles.progressInput}
              title="Seek"
            />
          </div>
        </div>
      </div>

      {/* ── Search Bar ───────────────────────────────────────────── */}
      <div className={styles.searchSection}>
        <div className={styles.searchContainer}>
          <Search size={15} className={styles.searchIcon} />
          <input
            type="text"
            placeholder="Search transcript…"
            value={searchQuery}
            onChange={(e) => { setSearchQuery(e.target.value); setActiveMatchIdx(0); }}
            onKeyDown={(e) => {
              if (e.key === 'Enter') { e.shiftKey ? goPrevMatch() : goNextMatch(); }
              if (e.key === 'Escape') setSearchQuery('');
            }}
            className={styles.searchInput}
            id="transcript-search-input"
          />
          {searchQuery && (
            <button className={styles.clearSearchBtn} onClick={() => setSearchQuery('')}>
              <X size={14} />
            </button>
          )}
        </div>

        {searchQuery && filteredSegments.length > 0 && (
          <div className={styles.searchNav}>
            <span className={styles.matchCount}>
              {activeMatchIdx + 1}/{filteredSegments.length}
            </span>
            <button
              className={styles.searchNavBtn}
              onClick={goPrevMatch}
              disabled={filteredSegments.length <= 1}
              title="Previous match"
            >
              <ChevronUp size={16} />
            </button>
            <button
              className={styles.searchNavBtn}
              onClick={goNextMatch}
              disabled={filteredSegments.length <= 1}
              title="Next match"
            >
              <ChevronDown size={16} />
            </button>
          </div>
        )}

        {searchQuery && filteredSegments.length === 0 && (
          <span className={styles.matchCount}>No results</span>
        )}
      </div>

      {/* ── Transcript ───────────────────────────────────────────── */}
      <div className={styles.transcriptList} ref={scrollRef}>
        {displaySegments.length === 0 ? (
          <div className={styles.emptyTranscript}>
            <FileText size={36} />
            <p>{searchQuery ? 'No matching segments found.' : 'No transcript available.'}</p>
          </div>
        ) : (
          displaySegments.map((seg, idx) => {
            const isActive = currentTime >= seg.start_time && currentTime < seg.end_time;
            const isActiveMatch = searchQuery && idx === activeMatchIdx;
            const color = speakerColor(seg.speaker);

            return (
              <div
                key={seg.id}
                ref={(el) => { if (el) segmentRefs.current.set(seg.id, el); }}
                className={[
                  styles.segment,
                  isActive ? styles.activeSegment : '',
                  isActiveMatch ? styles.focusedSegment : '',
                ].filter(Boolean).join(' ')}
                onClick={() => handleSegmentClick(seg.start_time)}
                role="button"
                tabIndex={0}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') handleSegmentClick(seg.start_time); }}
              >
                <div
                  className={styles.speakerAvatar}
                  style={{ backgroundColor: color }}
                >
                  {seg.speaker.charAt(0).toUpperCase()}
                  {isActive && <span className={styles.speakerPulse} />}
                </div>

                <div className={styles.segmentContent}>
                  <div className={styles.segmentHeader}>
                    <span className={styles.speakerName}>{seg.speaker}</span>
                    <span className={styles.timestamp}>{formatTime(seg.start_time)}</span>
                  </div>
                  <div className={styles.segmentText}>
                    {renderHighlightedText(seg.text, searchQuery, !!isActiveMatch)}
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}

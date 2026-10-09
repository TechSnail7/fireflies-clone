'use client';

import { useEffect, useState, useRef, Suspense } from 'react';
import { useSearchParams } from 'next/navigation';
import Sidebar from '@/components/Sidebar';
import Header from '@/components/Header';
import MeetingCard from '@/components/MeetingCard';
import SettingsModal from '@/components/SettingsModal';
import { api, Meeting, apiClient } from '@/lib/api';
import styles from './page.module.css';
import progressStyles from './progress.module.css';
import { Calendar, Upload, Plus, Settings } from 'lucide-react';

function DashboardContent() {
  const searchParams = useSearchParams();
  const searchQuery = searchParams.get('search') || '';

  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState("");
  const [isSettingsOpen, setIsSettingsOpen] = useState(false);
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadMeetings = async () => {
    setLoading(true);
    try {
      const params = searchQuery ? { search: searchQuery } : {};
      const data = await api.getMeetings(params);
      setMeetings(data);
    } catch (err) {
      console.error(err);
      setError('Failed to load meetings.');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteMeeting = async (id: number) => {
    if (confirm('Are you sure you want to delete this meeting?')) {
      try {
        await apiClient.delete(`/meetings/${id}`);
        await loadMeetings();
      } catch (err) {
        console.error('Failed to delete meeting', err);
        alert('Failed to delete meeting');
      }
    }
  };

  useEffect(() => {
    loadMeetings();
  }, [searchQuery]);

  const handleUploadClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size === 0) {
      alert(`The file "${file.name}" is completely empty (0 bytes). Please select a valid, non-empty video file.`);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setEstimatedTime("Calculating...");
    
    // Estimate duration based on file size (base 15s + ~1s per MB for upload & transcription)
    const sizeInMB = file.size / (1024 * 1024);
    const expectedDuration = 15000 + (sizeInMB * 1000); // e.g. 500MB = ~515 seconds, 10MB = 25 seconds
    const startTime = Date.now();
    
    const progressInterval = setInterval(() => {
      const elapsed = Date.now() - startTime;
      const progress = Math.min(95, Math.floor((elapsed / expectedDuration) * 100));
      setUploadProgress(progress);
      
      const remainingMs = Math.max(0, expectedDuration - elapsed);
      const remainingMins = Math.floor(remainingMs / 60000);
      const remainingSecs = Math.floor((remainingMs % 60000) / 1000);
      setEstimatedTime(`${remainingMins}m ${remainingSecs}s remaining`);
    }, 1000);

    try {
      // 1. Try to call the AI-Video-Transcriber API (assumed running on port 8001)
      let segments = [];
      let summaryData = null;

      let videoUrl = null;

      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('summary_language', 'en');

        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
        const transcriberRes = await fetch(`${apiUrl}/meetings/process-video`, {
          method: 'POST',
          body: formData
        });

        if (transcriberRes.ok) {
          const result = await transcriberRes.json();
          if (result.video_url) {
            videoUrl = result.video_url;
          }
          // Map AI-Video-Transcriber output to our schema
          if (result.transcript) {
          segments = result.transcript
            .filter((seg: any) => seg.text && seg.text.trim().length > 0)
            .map((seg: any) => ({
              speaker: seg.speaker || 'Speaker 1',
              text: seg.text.trim(),
              start_time: seg.start || 0,
              end_time: seg.end || 0
            }));
          }
          if (result.summary) {
            summaryData = {
              overview: result.summary,
              key_topics: [],
              chapters: [],
              outline: []
            };
          }
        } else {
          throw new Error('Transcriber API error');
        }
      } catch (transcriberErr) {
        console.warn('AI-Video-Transcriber service not reachable on :8001, falling back to mock data.', transcriberErr);
        // Fallback to mock data if service is not running locally
        segments = [
          { speaker: "You", text: "This is a fallback transcript since the AI-Video-Transcriber service is not running.", start_time: 0, end_time: 5 },
          { speaker: "AI Assistant", text: "Please start the transcriber backend on port 8001 to use real transcription.", start_time: 6, end_time: 10 }
        ];
        summaryData = {
          overview: "This meeting used fallback mocked data.",
          key_topics: [{ title: "Upload", description: "File processing fallback" }],
          chapters: [{ title: "Start", start_time: 0, end_time: 10, summary: "Initialization" }],
          outline: [{ heading: "Summary", points: ["File uploaded", "Fallback used"] }]
        };
      }

      // 2. Create the meeting in our own backend
      const newMeeting = {
        title: `Uploaded: ${file.name.replace(/\.[^/.]+$/, "")}`,
        date: new Date().toISOString(),
        duration_seconds: segments.length > 0 ? Math.round(segments[segments.length - 1].end_time) : 1800,
        host: "You",
        participants: ["You", "AI Assistant"],
        status: "completed",
        meeting_type: "video",
        video_url: videoUrl,
        tags: ["Uploaded"],
        transcript_segments: segments,
        summary: summaryData,
        action_items: [
          { text: "Review the uploaded transcript", assignee: "You", is_completed: false, due_date: null }
        ]
      };

      await apiClient.post('/meetings', newMeeting);
      await loadMeetings();
      
      setUploadProgress(100);
      setEstimatedTime("Done!");
    } catch (err: any) {
      console.error('Upload failed:', err);
      const detail = err.response?.data?.detail || err.message || err;
      alert('Failed to process uploaded file: ' + (typeof detail === 'string' ? detail : JSON.stringify(detail)));
    } finally {
      clearInterval(progressInterval);
      setTimeout(() => {
        setIsUploading(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }, 500); // short delay to show 100%
    }
  };

  return (
    <div className="main-content">
      <Header title="Home" />
      {isSettingsOpen && <SettingsModal onClose={() => setIsSettingsOpen(false)} />}
      
      {isUploading && (
        <div className={progressStyles.progressModal}>
          <div className={progressStyles.progressModalContent}>
            <h3>Transcribing Video...</h3>
            <p>Our AI is securely processing your file. This may take a few minutes depending on the file size.</p>
            <div className={progressStyles.progressBarContainer}>
              <div className={progressStyles.progressBar} style={{ width: `${uploadProgress}%` }}></div>
            </div>
            <div className={progressStyles.progressDetails}>
              <span>{uploadProgress}%</span>
              <span>{estimatedTime}</span>
            </div>
          </div>
        </div>
      )}
      
      <main className={styles.main}>
        <div className={styles.content}>
          
          <div className={styles.heroBanner}>
            <div className={styles.heroText}>
              <h2>Welcome Aboard, ANKIT!</h2>
              <p>Fireflies is now ready to automate your meetings and streamline your workflows.</p>
            </div>
            <div className={styles.heroVideo} onClick={() => setIsVideoPlaying(true)}>
              <img 
                src="https://img.youtube.com/vi/uZuFXgNfZmI/maxresdefault.jpg" 
                alt="Demo Video Thumbnail" 
                className={styles.thumbnail}
                onError={(e) => { e.currentTarget.src = "https://img.youtube.com/vi/uZuFXgNfZmI/hqdefault.jpg"; }}
              />
              <div className={styles.mockVideo}>
                <div className={styles.playBtn}>▶</div>
              </div>
            </div>

            {isVideoPlaying && (
              <div className={styles.videoModal} onClick={() => setIsVideoPlaying(false)}>
                <div className={styles.videoModalContent} onClick={e => e.stopPropagation()}>
                  <button className={styles.closeVideoBtn} onClick={() => setIsVideoPlaying(false)}>✕</button>
                  <iframe 
                    width="700" 
                    height="400" 
                    src="https://www.youtube.com/embed/uZuFXgNfZmI?autoplay=1" 
                    title="Fireflies AI Full Product Demo" 
                    frameBorder="0" 
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" 
                    allowFullScreen
                  ></iframe>
                </div>
              </div>
            )}
          </div>

          <div className={styles.quickStartSection}>
            <h3>Quick Start</h3>
            <p>Capture your first meeting or upload a recording to see Fireflies in action.</p>
            
            <div className={styles.quickStartGrid}>
              <button className={`${styles.quickStartCard} ${styles.qsRed}`}>
                <Calendar size={18} />
                <span>Schedule Meeting</span>
                <span className={styles.chevron}>&rsaquo;</span>
              </button>

              <button 
                className={`${styles.quickStartCard} ${styles.qsGreen}`}
                onClick={handleUploadClick}
                disabled={isUploading}
              >
                <Upload size={18} />
                <span>{isUploading ? 'Uploading...' : 'Upload File'}</span>
                <span className={styles.chevron}>&rsaquo;</span>
              </button>
              <input 
                type="file" 
                ref={fileInputRef} 
                style={{ display: 'none' }} 
                accept=".mp3,.mp4,.wav,.txt"
                onChange={handleFileUpload}
              />

              <button className={`${styles.quickStartCard} ${styles.qsPurple}`}>
                <Plus size={18} />
                <span>Capture Meeting</span>
                <span className={styles.chevron}>&rsaquo;</span>
              </button>
            </div>
          </div>

          <div className={styles.meetingsSection}>
            <div className={styles.meetingsHeader}>
              <div className={styles.tabs}>
                <button className={`${styles.tab} ${styles.activeTab}`}>Recent</button>
                <button className={styles.tab}>Upcoming</button>
                <button className={styles.tab}>AI Feed</button>
              </div>
              <button className={styles.settingsBtn} onClick={() => setIsSettingsOpen(true)}>
                <Settings size={14} /> Settings
              </button>
            </div>

            <div className={styles.meetingsList}>
              {loading ? (
                <div className={styles.loading}>Loading your meetings...</div>
              ) : error ? (
                <div className={styles.error}>{error}</div>
              ) : meetings.length === 0 ? (
                <div className={styles.empty}>
                  <p>{searchQuery ? `No meetings found for "${searchQuery}"` : 'No meetings found.'}</p>
                </div>
              ) : (
                meetings.map(meeting => (
                  <MeetingCard key={meeting.id} meeting={meeting} onDelete={handleDeleteMeeting} />
                ))
              )}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default function Dashboard() {
  return (
    <>
      <Sidebar />
      <Suspense fallback={<div className="main-content" style={{ display: 'flex', alignItems: 'center', justifyContent: 'center' }}>Loading dashboard...</div>}>
        <DashboardContent />
      </Suspense>
    </>
  );
}

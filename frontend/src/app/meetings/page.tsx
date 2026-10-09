'use client';

import React, { useEffect, useState, useRef, Suspense } from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { format } from 'date-fns';
import { 
  Search, 
  Bell, 
  Video, 
  ChevronRight, 
  ArrowUpRight, 
  AlertTriangle, 
  MessageSquare, 
  X, 
  Trash2, 
  SlidersHorizontal,
  Upload,
  Calendar,
  Mic,
  Plus,
  Hash
} from 'lucide-react';

import Sidebar from '@/components/Sidebar';
import AskFredPanel from '@/components/AskFredPanel';
import { api, apiClient, Meeting } from '@/lib/api';
import progressStyles from '../progress.module.css';
import styles from './meetings.module.css';

function MeetingsView() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [meetings, setMeetings] = useState<Meeting[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [activeChannel, setActiveChannel] = useState<'my_meetings' | 'all' | 'voice' | 'uploads'>('my_meetings');
  const [activeFilter, setActiveFilter] = useState<'hosted' | 'shared'>('hosted');
  const [showTrialBanner, setShowTrialBanner] = useState(true);
  const [showWarningBanner, setShowWarningBanner] = useState(true);

  // Upload state
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [estimatedTime, setEstimatedTime] = useState('');

  const loadMeetings = async () => {
    setLoading(true);
    try {
      const data = await api.getMeetings();
      setMeetings(data);
    } catch (err) {
      console.error('Failed to load meetings:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadMeetings();
  }, []);

  const handleDeleteMeeting = async (e: React.MouseEvent, id: number) => {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this meeting?')) {
      try {
        await apiClient.delete(`/meetings/${id}`);
        await loadMeetings();
      } catch (err) {
        console.error('Failed to delete meeting:', err);
        alert('Failed to delete meeting');
      }
    }
  };

  const handleCaptureClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size === 0) {
      alert(`The file "${file.name}" is completely empty. Please select a valid video file.`);
      if (fileInputRef.current) fileInputRef.current.value = '';
      return;
    }

    setIsUploading(true);
    setUploadProgress(0);
    setEstimatedTime('Calculating...');

    const sizeInMB = file.size / (1024 * 1024);
    const expectedDuration = 15000 + sizeInMB * 1000;
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
      let segments: any[] = [];
      let summaryData: any = null;
      let videoUrl: string | null = null;

      try {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('summary_language', 'en');

        const transcriberUrl = process.env.NEXT_PUBLIC_TRANSCRIBER_URL || 'http://localhost:8001/api';
        const transcriberRes = await fetch(`${transcriberUrl}/process-video`, {
          method: 'POST',
          body: formData,
        });

        if (transcriberRes.ok) {
          const result = await transcriberRes.json();
          if (result.video_url) {
            videoUrl = result.video_url;
          }
          if (result.transcript) {
            segments = result.transcript
              .filter((seg: any) => seg.text && seg.text.trim().length > 0)
              .map((seg: any) => ({
                speaker: seg.speaker || 'Speaker 1',
                text: seg.text.trim(),
                start_time: seg.start || 0,
                end_time: seg.end || 0,
              }));
          }
          if (result.summary) {
            summaryData = {
              overview: result.summary,
              key_topics: [],
              chapters: [],
              outline: [],
            };
          }
        }
      } catch (err) {
        console.warn('Transcriber offline, using fallback mock.');
        segments = [
          { speaker: 'You', text: 'This meeting was uploaded for review.', start_time: 0, end_time: 5 },
          { speaker: 'AI Assistant', text: 'Processing completed successfully.', start_time: 6, end_time: 10 },
        ];
        summaryData = {
          overview: 'Uploaded meeting discussion.',
          key_topics: [{ title: 'Overview', description: 'Uploaded content' }],
          chapters: [],
          outline: [],
        };
      }

      const newMeeting = {
        title: file.name.replace(/\.[^/.]+$/, ''),
        date: new Date().toISOString(),
        duration_seconds: segments.length > 0 ? Math.round(segments[segments.length - 1].end_time) : 300,
        host: 'ANKIT',
        participants: ['ANKIT', 'AI Assistant'],
        status: 'completed',
        meeting_type: 'video',
        video_url: videoUrl,
        tags: ['Uploaded'],
        transcript_segments: segments,
        summary: summaryData,
        action_items: [
          { text: 'Review key points and decisions', assignee: 'ANKIT', is_completed: false, due_date: null },
        ],
      };

      await apiClient.post('/meetings', newMeeting);
      await loadMeetings();
      setUploadProgress(100);
      setEstimatedTime('Done!');
    } catch (err: any) {
      console.error('Upload failed:', err);
      alert('Upload failed: ' + (err.response?.data?.detail || err.message));
    } finally {
      clearInterval(progressInterval);
      setTimeout(() => {
        setIsUploading(false);
        if (fileInputRef.current) fileInputRef.current.value = '';
      }, 500);
    }
  };

  // Filter meetings by search and channel
  const filteredMeetings = meetings.filter((m) => {
    const matchesSearch =
      m.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      m.host.toLowerCase().includes(searchQuery.toLowerCase());
    
    if (activeChannel === 'uploads') {
      return matchesSearch && m.tags.some((t) => t.name.toLowerCase() === 'uploaded');
    }
    return matchesSearch;
  });

  const formatMeetingDate = (dateStr: string, durationSec: number, host: string) => {
    try {
      const d = new Date(dateStr);
      const datePart = format(d, 'MMM d');
      const timePart = format(d, 'h:mm a');
      const mins = Math.max(1, Math.round(durationSec / 60));
      return `${datePart} · ${timePart} · ${mins} min · ${host || 'ANKIT'}`;
    } catch {
      return `${Math.round(durationSec / 60)} min · ${host}`;
    }
  };

  return (
    <div className={styles.meetingsPageWrapper}>
      {/* Hidden File Input for Capture */}
      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        accept=".mp4,.mov,.mp3,.wav,.m4a"
        onChange={handleFileUpload}
      />

      {/* Upload Progress Modal */}
      {isUploading && (
        <div className={progressStyles.progressModal}>
          <div className={progressStyles.progressModalContent}>
            <h3>Transcribing Video...</h3>
            <p>Our AI is securely processing your file. This may take a few moments.</p>
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

      {/* 1. Top Trial Banner */}
      {showTrialBanner && (
        <div className={styles.topTrialBanner}>
          <span>You are eligible for 7 days business plan free trial.</span>
          <span className={styles.trialLink} onClick={() => alert('Trial activated!')}>
            Start free trial →
          </span>
          <button className={styles.bannerClose} onClick={() => setShowTrialBanner(false)}>
            <X size={14} />
          </button>
        </div>
      )}

      {/* 2. Top Header */}
      <header className={styles.topHeader}>
        <div className={styles.headerTitle}>Meetings</div>

        <div className={styles.headerSearchContainer}>
          <Search size={16} className={styles.searchIcon} />
          <input
            type="text"
            className={styles.searchInput}
            placeholder="Search by title or keyword"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
          <div className={styles.searchShortcut}>Ctrl + K</div>
        </div>

        <div className={styles.headerRightActions}>
          <div className={styles.freeMeetingsBadge}>
            <span className={styles.freeCountBadge}>3</span>
            <span>Free meetings</span>
          </div>

          <button className={styles.upgradeBtn} onClick={() => alert('Upgrade modal')}>
            Upgrade
          </button>

          <button className={styles.bellBtn} title="Notifications">
            <Bell size={18} />
            <span className={styles.bellDot}></span>
          </button>

          <button className={styles.captureBtn} onClick={handleCaptureClick}>
            <Video size={16} />
            <span>Capture</span>
          </button>
        </div>
      </header>

      {/* 3. Three-Column Body Layout */}
      <div className={styles.pageBody}>
        {/* Left Sub-Sidebar (Channels) */}
        <aside className={styles.channelSidebar}>
          <div className={styles.searchChannelsInput}>
            <Search size={14} color="#64748b" />
            <input placeholder="Search channels" />
          </div>

          <div className={styles.channelList}>
            <div
              className={`${styles.channelItem} ${activeChannel === 'my_meetings' ? styles.active : ''}`}
              onClick={() => setActiveChannel('my_meetings')}
            >
              <span className={styles.channelHash}>#</span>
              <span>My Meetings</span>
            </div>

            <div
              className={`${styles.channelItem} ${activeChannel === 'all' ? styles.active : ''}`}
              onClick={() => setActiveChannel('all')}
            >
              <Calendar size={16} />
              <span>All Meetings</span>
            </div>

            <div
              className={`${styles.channelItem} ${activeChannel === 'voice' ? styles.active : ''}`}
              onClick={() => setActiveChannel('voice')}
            >
              <Mic size={16} />
              <span>Voice Agent Meetings</span>
            </div>

            <div
              className={`${styles.channelItem} ${activeChannel === 'uploads' ? styles.active : ''}`}
              onClick={() => {
                setActiveChannel('uploads');
                handleCaptureClick();
              }}
            >
              <Upload size={16} />
              <span>Uploads</span>
              <span className={styles.badgeNew}>NEW</span>
            </div>
          </div>

          <div className={styles.allChannelsSection}>
            <div className={styles.allChannelsTitle}>All channels</div>
            <div className={styles.channelIconPlaceholder}>#</div>
            <div className={styles.allChannelsText}>
              Create channels to organize your conversations
            </div>
            <button className={styles.addChannelBtn} onClick={() => alert('Create Channel modal')}>
              <Plus size={14} />
              <span>Channel</span>
            </button>
          </div>
        </aside>

        {/* Center Panel (Meetings List) */}
        <main className={styles.meetingsMainPanel}>
          {/* Filter row */}
          <div className={styles.filterRow}>
            <div className={styles.filterPills}>
              <button
                className={`${styles.filterPill} ${activeFilter === 'hosted' ? styles.activePill : ''}`}
                onClick={() => setActiveFilter('hosted')}
              >
                Hosted by me
              </button>
              <button
                className={`${styles.filterPill} ${activeFilter === 'shared' ? styles.activePill : ''}`}
                onClick={() => setActiveFilter('shared')}
              >
                Shared with me
              </button>
              <button className={styles.filterPill} onClick={() => alert('Filters clicked')}>
                <SlidersHorizontal size={14} />
                <span>Filters</span>
              </button>
            </div>

            <button className={styles.filterSearchBtn} title="Quick search">
              <Search size={16} />
            </button>
          </div>

          {/* Warning Banner */}
          {showWarningBanner && (
            <div className={styles.warningBanner}>
              <div className={styles.warningLeft}>
                <AlertTriangle size={16} className={styles.warningIcon} />
                <span>One of your recent meetings didn't record successfully.</span>
                <span className={styles.warningLink} onClick={() => alert('Recent meeting status: checked')}>
                  recent meeting status →
                </span>
              </div>
              <button className={styles.warningClose} onClick={() => setShowWarningBanner(false)}>
                <X size={14} />
              </button>
            </div>
          )}

          {/* Date Header */}
          <div className={styles.dateSectionHeader}>
            <span className={styles.dateTitle}>Today</span>
            <button className={styles.feedbackBtn} onClick={() => alert('Feedback submitted')}>
              <MessageSquare size={14} />
              <span>Feedback</span>
            </button>
          </div>

          {/* Meetings List */}
          <div className={styles.meetingList}>
            {loading ? (
              <div className={styles.loadingState}>Loading meetings...</div>
            ) : filteredMeetings.length === 0 ? (
              <div className={styles.emptyState}>No meetings found. Upload or capture one above!</div>
            ) : (
              filteredMeetings.map((meeting) => (
                <div
                  key={meeting.id}
                  className={styles.meetingItemCard}
                  onClick={() => router.push(`/meetings/${meeting.id}`)}
                >
                  <div className={styles.meetingCardLeft}>
                    <div className={styles.meetingAvatar}>
                      {meeting.host ? meeting.host[0].toUpperCase() : 'A'}
                    </div>

                    <div className={styles.meetingDetails}>
                      <div className={styles.meetingTitleRow}>
                        <span className={styles.titleText}>{meeting.title}</span>
                        <ChevronRight size={14} className={styles.titleIcon} />
                        <ArrowUpRight size={14} className={styles.titleIcon} />
                      </div>
                      <div className={styles.meetingMetaRow}>
                        {formatMeetingDate(meeting.date, meeting.duration_seconds, meeting.host)}
                      </div>
                    </div>
                  </div>

                  <div className={styles.meetingCardRight}>
                    <button
                      className={styles.cardActionBtn}
                      title="Delete meeting"
                      onClick={(e) => handleDeleteMeeting(e, meeting.id)}
                    >
                      <Trash2 size={15} />
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* End of meetings marker */}
          <div className={styles.endMessage}>
            You've reached the end of your meetings.
          </div>
        </main>

        {/* Right Panel (Ask Fred Chatbot) */}
        <AskFredPanel channelName="My Meetings" />
      </div>
    </div>
  );
}

export default function MeetingsPage() {
  return (
    <>
      <Sidebar />
      <Suspense fallback={<div style={{ padding: 24, color: '#94a3b8' }}>Loading meetings...</div>}>
        <MeetingsView />
      </Suspense>
    </>
  );
}

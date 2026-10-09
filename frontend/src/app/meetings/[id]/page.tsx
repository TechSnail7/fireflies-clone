'use client';

import { useEffect, useState, Suspense } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { format } from 'date-fns';
import {
  ArrowLeft, Share, Download, MoreHorizontal,
  Clock, Calendar, Users
} from 'lucide-react';
import Sidebar from '@/components/Sidebar';
import TranscriptPanel from '@/components/TranscriptPanel';
import SummaryPanel from '@/components/SummaryPanel';
import { api, MeetingDetail } from '@/lib/api';
import styles from './page.module.css';

function MeetingContent() {
  const params = useParams();
  const router = useRouter();
  const [meeting, setMeeting] = useState<MeetingDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function loadMeeting() {
      if (!params.id) return;
      try {
        const data = await api.getMeeting(Number(params.id));
        setMeeting(data);
      } catch (err) {
        console.error(err);
        setError('Failed to load meeting details.');
      } finally {
        setLoading(false);
      }
    }
    loadMeeting();
  }, [params.id]);

  if (loading) {
    return (
      <>
        <Sidebar />
        <div className={styles.loadingContainer}>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <div className={styles.spinner} />
            <span>Loading meeting…</span>
          </div>
        </div>
      </>
    );
  }

  if (error || !meeting) {
    return (
      <>
        <Sidebar />
        <div className={styles.errorContainer}>
          <h3>{error || 'Meeting not found'}</h3>
          <button className="btn btn-primary" onClick={() => router.push('/')}>Back to Dashboard</button>
        </div>
      </>
    );
  }

  const durationMinutes = Math.round(meeting.duration_seconds / 60);
  const formattedDate = format(new Date(meeting.date), 'EEEE, MMMM d, yyyy');

  return (
    <>
      <Sidebar />
      <div className="main-content">
        <header className={styles.header}>
          <div className={styles.headerTop}>
            <div className={styles.left}>
              <button className={styles.backBtn} onClick={() => router.push('/')} title="Back">
                <ArrowLeft size={18} />
              </button>
              <h1 className={styles.title}>{meeting.title}</h1>
            </div>

            <div className={styles.right}>
              <button className={styles.actionBtn}>
                <Share size={14} /> Share
              </button>
              <button className={styles.actionBtn}>
                <Download size={14} /> Export
              </button>
              <button className={styles.iconBtn}>
                <MoreHorizontal size={18} />
              </button>
            </div>
          </div>

          <div className={styles.meta}>
            <div className={styles.metaItem}>
              <Calendar size={13} />
              <span>{formattedDate}</span>
            </div>
            <div className={styles.metaDot} />
            <div className={styles.metaItem}>
              <Clock size={13} />
              <span>{durationMinutes} min</span>
            </div>
            <div className={styles.metaDot} />
            <div className={styles.metaItem}>
              <Users size={13} />
              <span>{meeting.participants.join(', ')}</span>
            </div>
          </div>
        </header>

        <main className={styles.workspace}>
          <div className={styles.leftPane}>
            <TranscriptPanel
              segments={meeting.segments || []}
              videoUrl={meeting.video_url}
            />
          </div>
          <div className={styles.rightPane}>
            <SummaryPanel
              summary={meeting.summary}
              actionItems={meeting.action_items || []}
            />
          </div>
        </main>
      </div>
    </>
  );
}

export default function MeetingView() {
  return (
    <Suspense fallback={
      <div className={styles.loadingContainer}>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
          <div className={styles.spinner} />
          <span>Loading meeting…</span>
        </div>
      </div>
    }>
      <MeetingContent />
    </Suspense>
  );
}

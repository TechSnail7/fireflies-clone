import Link from 'next/link';
import { format } from 'date-fns';
import { Settings, X } from 'lucide-react';
import { Meeting } from '@/lib/api';
import styles from './MeetingCard.module.css';

interface MeetingCardProps {
  meeting: Meeting;
  onDelete?: (id: number) => void;
}

export default function MeetingCard({ meeting, onDelete }: MeetingCardProps) {
  const formattedDate = format(new Date(meeting.date), 'EEE, MMM d yyyy, h:mm a');

  return (
    <Link href={`/meetings/${meeting.id}`} className={styles.listItem}>
      <div className={styles.iconContainer}>
        <div className={styles.appIcon}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" />
          </svg>
        </div>
      </div>
      
      <div className={styles.details}>
        <h4 className={styles.title}>{meeting.title}</h4>
        <span className={styles.date}>{formattedDate}</span>
      </div>

      <div className={styles.actions}>
        {onDelete && (
          <button 
            className={styles.actionBtn} 
            onClick={(e) => { e.preventDefault(); onDelete(meeting.id); }}
            title="Delete meeting"
            style={{ color: '#F87171' }}
          >
            <X size={16} />
          </button>
        )}
        <button className={styles.actionBtn} onClick={(e) => e.preventDefault()}>
          <Settings size={16} />
        </button>
      </div>
    </Link>
  );
}

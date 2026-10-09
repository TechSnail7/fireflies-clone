import { useState } from 'react';
import { Summary, ActionItem } from '@/lib/api';
import { CheckCircle2, Circle, ListTodo, FileText, LayoutList } from 'lucide-react';
import styles from './SummaryPanel.module.css';

interface SummaryPanelProps {
  summary: Summary | null;
  actionItems: ActionItem[];
}

export default function SummaryPanel({ summary, actionItems }: SummaryPanelProps) {
  const [activeTab, setActiveTab] = useState<'summary' | 'action_items' | 'chapters'>('summary');

  if (!summary && actionItems.length === 0) {
    return (
      <div className={styles.emptyPanel}>
        <div className={styles.emptyIcon}><FileText size={32} /></div>
        <h3>No AI Summary Available</h3>
        <p>This meeting does not have an AI-generated summary yet.</p>
        <button className="btn btn-primary mt-4">Generate AI Summary</button>
      </div>
    );
  }

  return (
    <div className={styles.panel}>
      <div className={styles.tabs}>
        <button 
          className={`${styles.tab} ${activeTab === 'summary' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('summary')}
        >
          <FileText size={16} /> AI Summary
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'action_items' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('action_items')}
        >
          <ListTodo size={16} /> Action Items
          {actionItems.length > 0 && (
            <span className={styles.badge}>{actionItems.length}</span>
          )}
        </button>
        <button 
          className={`${styles.tab} ${activeTab === 'chapters' ? styles.activeTab : ''}`}
          onClick={() => setActiveTab('chapters')}
        >
          <LayoutList size={16} /> Chapters
        </button>
      </div>

      <div className={styles.content}>
        {activeTab === 'summary' && summary && (
          <div className={styles.summarySection}>
            <div className={styles.overviewBlock}>
              <h3 className={styles.sectionTitle}>Overview</h3>
              <p className={styles.overviewText}>{summary.overview}</p>
            </div>

            {summary.key_topics && summary.key_topics.length > 0 && (
              <div className={styles.topicsBlock}>
                <h3 className={styles.sectionTitle}>Key Topics</h3>
                <div className={styles.topicsList}>
                  {summary.key_topics.map((topic, i) => (
                    <div key={i} className={styles.topicCard}>
                      <h4 className={styles.topicTitle}>{topic.title}</h4>
                      <p className={styles.topicDesc}>{topic.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {summary.outline && summary.outline.length > 0 && (
              <div className={styles.outlineBlock}>
                <h3 className={styles.sectionTitle}>Outline</h3>
                {summary.outline.map((section, i) => (
                  <div key={i} className={styles.outlineSection}>
                    <h4 className={styles.outlineHeading}>{section.heading}</h4>
                    <ul className={styles.outlineList}>
                      {section.points.map((point, j) => (
                        <li key={j}>{point}</li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'action_items' && (
          <div className={styles.actionItemsSection}>
            <div className={styles.actionItemsHeader}>
              <h3 className={styles.sectionTitle}>Tasks ({actionItems.length})</h3>
              <button className={styles.addBtn}>+ Add Task</button>
            </div>
            
            <div className={styles.taskList}>
              {actionItems.map(item => (
                <div key={item.id} className={`${styles.taskItem} ${item.is_completed ? styles.taskCompleted : ''}`}>
                  <button className={styles.checkBtn}>
                    {item.is_completed ? <CheckCircle2 size={20} className={styles.checked} /> : <Circle size={20} className={styles.unchecked} />}
                  </button>
                  <div className={styles.taskContent}>
                    <span className={styles.taskText}>{item.text}</span>
                    {item.assignee && (
                      <span className={styles.taskAssignee}>
                        <span className={styles.assigneeAvatar}>{item.assignee.charAt(0)}</span>
                        {item.assignee}
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'chapters' && summary && summary.chapters && (
          <div className={styles.chaptersSection}>
            <h3 className={styles.sectionTitle}>Timeline</h3>
            <div className={styles.timeline}>
              {summary.chapters.map((chapter, i) => (
                <div key={i} className={styles.timelineItem}>
                  <div className={styles.timelineDot}></div>
                  <div className={styles.timelineContent}>
                    <div className={styles.timelineHeader}>
                      <h4 className={styles.chapterTitle}>{chapter.title}</h4>
                      <span className={styles.chapterTime}>
                        {Math.floor(chapter.start_time / 60).toString().padStart(2, '0')}:
                        {Math.floor(chapter.start_time % 60).toString().padStart(2, '0')}
                      </span>
                    </div>
                    <p className={styles.chapterSummary}>{chapter.summary}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

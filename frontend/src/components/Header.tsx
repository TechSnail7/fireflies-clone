'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { Search, Bell, Video, ArrowRight, X, MessageSquare, Mic, Shield, Mail } from 'lucide-react';
import styles from './Header.module.css';

interface HeaderProps {
  title?: string;
  showSearch?: boolean;
}

export default function Header({ title = 'Home', showSearch = true }: HeaderProps) {
  const [search, setSearch] = useState('');
  const [showBanner, setShowBanner] = useState(true);
  const [isNotifOpen, setIsNotifOpen] = useState(false);
  const router = useRouter();

  const handleSearch = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter') {
      if (search.trim()) {
        router.push(`/?search=${encodeURIComponent(search.trim())}`);
      } else {
        router.push(`/`);
      }
    }
  };

  return (
    <div className={styles.headerWrapper}>
      {showBanner && (
        <div className={styles.topBanner}>
          <div className={styles.bannerContent}>
            You are eligible for 7 days business plan free trial. 
            <a href="#" className={styles.bannerLink}>
              Start free trial <ArrowRight size={14} className={styles.arrowIcon} />
            </a>
          </div>
          <button className={styles.closeBannerBtn} onClick={() => setShowBanner(false)}>
            <X size={16} />
          </button>
        </div>
      )}

      <header className={styles.header}>
        <div className={styles.left}>
          <h1 className={styles.title}>{title}</h1>
        </div>

        {showSearch && (
          <div className={styles.center}>
            <div className={styles.searchContainer}>
              <Search size={16} className={styles.searchIcon} />
              <input 
                type="text" 
                placeholder="Search by title or keyword" 
                className={styles.searchInput}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                onKeyDown={handleSearch}
              />
              <span className={styles.shortcut}>Enter</span>
            </div>
          </div>
        )}

        <div className={styles.right}>
          <div className={styles.freeMeetingsBadge}>
            <span className={styles.countBadge}>3</span>
            <span>Free meetings</span>
          </div>
          
          <button className={styles.upgradeBtn}>
            Upgrade
          </button>

          <div className={styles.notifWrapper}>
            <button className={styles.iconBtn} onClick={() => setIsNotifOpen(!isNotifOpen)}>
              <div className={styles.notificationDot}></div>
              <Bell size={18} />
            </button>

            {isNotifOpen && (
              <>
                <div className={styles.modalOverlay} onClick={() => setIsNotifOpen(false)}></div>
                <div className={styles.notifDropdown}>
                  <div className={styles.notifTabs}>
                    <button className={`${styles.notifTab} ${styles.activeTab}`}>All &middot; 12</button>
                    <button className={styles.notifTab}>Updates &middot; 12</button>
                    <button className={styles.notifTab}>Auto-Fill</button>
                    <button className={styles.notifTab}>Status <span className={styles.newBadge}>New</span></button>
                    <label className={styles.unreadToggle}>
                      <input type="checkbox" /> Unread
                    </label>
                  </div>
                  
                  <div className={styles.notifList}>
                    <div className={styles.notifHeader}>New</div>
                    
                    <div className={styles.notifItem}>
                      <div className={`${styles.notifIcon} ${styles.iconPurple}`}>
                        <MessageSquare size={16} />
                      </div>
                      <div className={styles.notifContent}>
                        <div className={styles.notifTitleRow}>
                          <h4>Your Slack recaps, your way</h4>
                          <span className={styles.notifTime}><span className={styles.redDot}></span> 03:45 AM</span>
                        </div>
                        <p>Pick what Fireflies sends to Slack after every call.</p>
                        <button className={styles.actionBtnSolid}>See How It Works</button>
                      </div>
                    </div>

                    <div className={styles.notifItem}>
                      <div className={`${styles.notifIcon} ${styles.iconPurple}`}>
                        <Mic size={16} />
                      </div>
                      <div className={styles.notifContent}>
                        <div className={styles.notifTitleRow}>
                          <h4>Stop taking the same call twice</h4>
                          <span className={styles.notifTime}><span className={styles.redDot}></span> 03:45 AM</span>
                        </div>
                        <p>Fireflies Voice Agents can run it for you instead, automatically. Get 100 free credits to try it.</p>
                        <button className={styles.actionBtnSolid}>Try now</button>
                      </div>
                    </div>

                    <div className={styles.notifItem}>
                      <div className={`${styles.notifIcon} ${styles.iconPurple}`}>
                        <Shield size={16} />
                      </div>
                      <div className={styles.notifContent}>
                        <div className={styles.notifTitleRow}>
                          <h4>Trust and privacy webinar</h4>
                          <span className={styles.notifTime}><span className={styles.redDot}></span> 03:45 AM</span>
                        </div>
                        <p>Tomorrow, Aug 25, 2 PM UTC. Privacy, proven live.</p>
                        <button className={styles.actionBtnSolid}>Save Your Spot</button>
                      </div>
                    </div>

                  </div>
                </div>
              </>
            )}
          </div>

          <button className={styles.captureBtn}>
            <Video size={16} />
            Capture
          </button>
        </div>
      </header>
    </div>
  );
}

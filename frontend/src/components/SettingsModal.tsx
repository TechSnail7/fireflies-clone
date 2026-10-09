'use client';

import { X, Sparkles, Calendar, Mail, Lock, Globe } from 'lucide-react';
import styles from './SettingsModal.module.css';
import { useState } from 'react';

interface SettingsModalProps {
  onClose: () => void;
}

export default function SettingsModal({ onClose }: SettingsModalProps) {
  const [unlimited, setUnlimited] = useState(false);
  const [autoJoin, setAutoJoin] = useState(true);

  return (
    <>
      <div className={styles.overlay} onClick={onClose}></div>
      <div className={styles.modal}>
        <div className={styles.header}>
          <h2>Meeting Settings</h2>
          <button className={styles.closeBtn} onClick={onClose}><X size={20} /></button>
        </div>

        <div className={styles.content}>
          <div className={styles.premiumBox}>
            <div className={styles.flexRow}>
              <Sparkles size={18} className={styles.sparkleIcon} />
              <span className={styles.premiumText}>Get unlimited transcripts</span>
              <span className={styles.freeBadge}>FREE</span>
            </div>
            <label className={styles.switch}>
              <input type="checkbox" checked={unlimited} onChange={(e) => setUnlimited(e.target.checked)} />
              <span className={styles.slider}></span>
            </label>
          </div>

          <div className={styles.settingGroup}>
            <div className={styles.settingHeader}>
              <div className={styles.flexRow}>
                <Calendar size={18} className={styles.blueIcon} />
                <span>Auto-join calendar meetings</span>
              </div>
              <label className={styles.switch}>
                <input type="checkbox" checked={autoJoin} onChange={(e) => setAutoJoin(e.target.checked)} />
                <span className={styles.slider}></span>
              </label>
            </div>
            <div className={styles.selectWrapper}>
              <select className={styles.select}>
                <option>All meetings with web-conf link</option>
                <option>Only meetings I host</option>
              </select>
            </div>
          </div>

          <div className={styles.settingGroup}>
            <div className={styles.settingHeader}>
              <div className={styles.flexRow}>
                <Mail size={18} className={styles.purpleIcon} />
                <span>Send email recap to</span>
              </div>
            </div>
            <div className={styles.selectWrapper}>
              <select className={styles.select}>
                <option>Everyone on the invite</option>
                <option>Only me</option>
              </select>
            </div>
          </div>

          <div className={styles.settingGroup}>
            <div className={styles.settingHeader}>
              <div className={styles.flexRow}>
                <Lock size={18} className={styles.purpleIcon} />
                <span>Meeting privacy</span>
              </div>
            </div>
            <div className={styles.selectWrapper}>
              <select className={styles.select}>
                <option>Teammates & Anyone with Link</option>
                <option>Only me</option>
              </select>
            </div>
          </div>

          <div className={styles.settingGroup}>
            <div className={styles.settingHeader}>
              <div className={styles.flexRow}>
                <Globe size={18} className={styles.purpleIcon} />
                <span>Meeting language</span>
              </div>
            </div>
            <div className={styles.selectWrapper}>
              <select className={styles.select}>
                <option>English (Global)</option>
                <option>Spanish</option>
                <option>French</option>
              </select>
            </div>
          </div>
        </div>

        <div className={styles.footer}>
          <button className={styles.cancelBtn} onClick={onClose}>Cancel</button>
          <button className={styles.saveBtn} onClick={onClose}>Save</button>
        </div>
      </div>
    </>
  );
}

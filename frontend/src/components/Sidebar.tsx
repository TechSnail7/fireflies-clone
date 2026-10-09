'use client';

import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { 
  Home, 
  Bot, 
  Video, 
  CheckSquare, 
  Sparkles, 
  BarChart2, 
  Mic, 
  Zap, 
  Mail, 
  Plug, 
  Settings,
  ChevronDown,
  ChevronRight,
  PanelLeftClose,
  PanelLeftOpen,
  LogOut,
  Smartphone,
  Monitor
} from 'lucide-react';
import styles from './Sidebar.module.css';

export default function Sidebar() {
  const pathname = usePathname();
  const [showInvite, setShowInvite] = useState(true);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [isProfileOpen, setIsProfileOpen] = useState(false);

  return (
    <>
      <aside className={`${styles.sidebar} ${isCollapsed ? styles.collapsed : ''}`}>
        <div className={styles.header}>
          <div className={styles.workspaceSelector} onClick={() => setIsProfileOpen(!isProfileOpen)}>
            <div className={styles.avatar}>A</div>
            {!isCollapsed && <span className={styles.workspaceName}>ANKIT</span>}
            {!isCollapsed && <ChevronDown size={14} className={styles.chevron} />}
          </div>
          
          <button className={styles.collapseBtn} onClick={() => setIsCollapsed(!isCollapsed)}>
            {isCollapsed ? <PanelLeftOpen size={16} /> : <PanelLeftClose size={16} />}
          </button>
        </div>

        <div className={styles.navContainer}>
          <div className={styles.navSection}>
            <Link href="/" className={`${styles.navItem} ${pathname === '/' ? styles.active : ''}`} title="Home">
              <Home size={18} />
              {!isCollapsed && <span>Home</span>}
            </Link>
            <Link href="/meetings?open=chat" className={`${styles.navItem} ${pathname.startsWith('/meetings') ? '' : ''}`} title="AskFred">
              <Bot size={18} />
              {!isCollapsed && <span>AskFred</span>}
            </Link>
            <Link href="/meetings" className={`${styles.navItem} ${pathname.startsWith('/meetings') ? styles.active : ''}`} title="Meetings">
              <Video size={18} />
              {!isCollapsed && <span>Meetings</span>}
            </Link>
            <Link href="#" className={styles.navItem} title="Tasks">
              <CheckSquare size={18} />
              {!isCollapsed && <span>Tasks</span>}
            </Link>
            <Link href="#" className={styles.navItem} title="AI Skills">
              <Sparkles size={18} />
              {!isCollapsed && <span>AI Skills</span>}
            </Link>
          </div>

          <div className={styles.navSection}>
            <Link href="#" className={styles.navItem} title="Analytics">
              <BarChart2 size={18} />
              {!isCollapsed && <span>Analytics</span>}
            </Link>
            <Link href="#" className={styles.navItem} title="Voice Agents">
              <Mic size={18} />
              {!isCollapsed && <span>Voice Agents</span>}
            </Link>
          </div>

          <div className={styles.navSection}>
            <Link href="#" className={styles.navItem} title="Upgrade">
              <Zap size={18} />
              {!isCollapsed && <span>Upgrade</span>}
              {!isCollapsed && <span className={styles.badgeGreen}>40% OFF</span>}
            </Link>
            <Link href="#" className={`${styles.navItem} ${styles.emailAssistant}`} title="Try Email Assistant">
              <Mail size={18} className={styles.iconColorful} />
              {!isCollapsed && <span>Try Email Assistant</span>}
            </Link>
          </div>

          <div className={styles.navSection}>
            <Link href="#" className={styles.navItem} title="Integrations">
              <Plug size={18} />
              {!isCollapsed && <span>Integrations</span>}
            </Link>
            <Link href="#" className={styles.navItem} title="Settings">
              <Settings size={18} />
              {!isCollapsed && <span>Settings</span>}
            </Link>
          </div>
        </div>

        {!isCollapsed && (
          <div className={styles.footer}>
            {showInvite && (
              <div className={styles.inviteCard}>
                <button className={styles.closeBtn} onClick={() => setShowInvite(false)}>&times;</button>
                <p className={styles.inviteText}>Invite coworkers to your Fireflies team</p>
                <button className={styles.createTeamBtn}>Create Team</button>
              </div>
            )}
          </div>
        )}
      </aside>

      {/* User Profile Dropdown Modal */}
      {isProfileOpen && (
        <>
          <div className={styles.modalOverlay} onClick={() => setIsProfileOpen(false)}></div>
          <div className={styles.profileDropdown}>
            <div className={styles.profileLeft}>
              <div className={styles.profileInfo}>
                <h4 className={styles.profileName}>Hi ANKIT</h4>
                <p className={styles.profileEmail}>akumar@example.com</p>
              </div>
              
              <div className={styles.profileSection}>
                <h5 className={styles.sectionTitle}>Free</h5>
                <div className={styles.usageBar}>
                  <div className={styles.usageFill} style={{ width: '100%' }}></div>
                </div>
                <p className={styles.usageText}>3 left / 3 free meetings</p>
                <button className={styles.upgradeBtnSolid}><Zap size={14} /> Upgrade</button>
              </div>

              <div className={styles.profileSection}>
                <h5 className={styles.sectionTitle}>Storage</h5>
                <p className={styles.usageText}>0 / 400 mins</p>
              </div>

              <div className={styles.profileSection}>
                <h5 className={styles.sectionTitle}>Refer and Earn $5</h5>
              </div>

              <div className={styles.profileMenu}>
                <Link href="#">Playlist</Link>
                <Link href="#">Settings</Link>
                <Link href="#">My Team</Link>
                <Link href="#">Manage Web Logins</Link>
                <Link href="#">Platform Rules</Link>
                <div className={styles.menuItemFlex}>
                  <span>Theme <span className={styles.betaBadge}>BETA</span></span>
                  <span className={styles.themeValue}>Dark</span>
                </div>
                <Link href="#">Logout</Link>
              </div>
            </div>

            <div className={styles.profileRight}>
              <div className={styles.appCard}>
                <Smartphone size={20} className={styles.appIconMobile} />
                <h5>Mobile App</h5>
                <p>Transcribe and summarize in-person conversations with mobile app.</p>
                <div className={styles.appStores}>
                  <div className={styles.storeBtn}>App Store</div>
                  <div className={styles.storeBtn}>Play Store</div>
                </div>
              </div>

              <div className={styles.appCard}>
                <div className={styles.chromeIcon}></div>
                <h5>Chrome Extension</h5>
                <p>Record and transcribe Google Meet calls without Fireflies notetaker bot.</p>
                <button className={styles.installBtn}>Install</button>
              </div>

              <div className={styles.desktopAppCard}>
                <div className={styles.ffIcon}></div>
                <span>Download Fireflies Desktop App</span>
                <ChevronRight size={16} />
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}

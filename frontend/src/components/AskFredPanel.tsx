'use client';

import React, { useState, useRef, useEffect } from 'react';
import { 
  Bot, 
  MessageSquare, 
  Plus, 
  X, 
  Sparkles, 
  Layers, 
  Mic, 
  ArrowUp,
  Hash,
  CheckCircle2,
  Target,
  Pin
} from 'lucide-react';
import { api } from '@/lib/api';
import styles from './AskFredPanel.module.css';

interface Message {
  id: string;
  sender: 'user' | 'bot';
  text: string;
  queryType?: string;
  items?: any[];
  timestamp: Date;
}

interface AskFredPanelProps {
  channelName?: string;
  onClose?: () => void;
}

export default function AskFredPanel({ channelName = 'My Meetings' }: AskFredPanelProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [showIntegrationCard, setShowIntegrationCard] = useState(true);
  const [isListening, setIsListening] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto scroll to bottom when messages update
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  const handleSendMessage = async (textToSend?: string) => {
    const query = (textToSend !== undefined ? textToSend : inputValue).trim();
    if (!query || isTyping) return;

    const userMsg: Message = {
      id: Date.now().toString(),
      sender: 'user',
      text: query,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMsg]);
    if (textToSend === undefined) setInputValue('');
    setIsTyping(true);

    try {
      const response = await api.askFred(query, channelName);
      const botMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: response.reply,
        queryType: response.query_type,
        items: response.items,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      console.error('Ask Fred failed:', err);
      const fallbackMsg: Message = {
        id: (Date.now() + 1).toString(),
        sender: 'bot',
        text: `I had trouble accessing that right now. Please ensure your backend is active or try asking about "action items" or "key decisions".`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, fallbackMsg]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleNewChat = () => {
    setMessages([]);
  };

  const handleToggleMic = () => {
    setIsListening(prev => !prev);
    if (!isListening) {
      // Mock voice input after a short delay
      setTimeout(() => {
        setInputValue("What are my key action items?");
        setIsListening(false);
      }, 1500);
    }
  };

  return (
    <div className={styles.askFredContainer}>
      {/* Header */}
      <div className={styles.header}>
        <div className={styles.headerTitle}>
          <div className={styles.botIcon}>
            <Bot size={20} />
          </div>
          <span>Ask Fred</span>
        </div>
        <div className={styles.headerActions}>
          <button className={styles.iconBtn} title="Conversation history">
            <MessageSquare size={16} />
          </button>
          <button className={styles.iconBtn} title="New Chat" onClick={handleNewChat}>
            <Plus size={17} />
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className={styles.scrollContent} ref={scrollRef}>
        {/* Integration Card */}
        {showIntegrationCard && (
          <div className={styles.integrationCard}>
            <button 
              className={styles.integrationCardClose} 
              onClick={() => setShowIntegrationCard(false)}
              aria-label="Close"
            >
              <X size={14} />
            </button>
            <div className={styles.integrationIcons}>
              {/* Slack & Gmail vector badges */}
              <svg className={styles.slackLogo} viewBox="0 0 128 128">
                <rect width="128" height="128" rx="28" fill="#4A154B" />
                <path d="M47 31a7 7 0 1 0-7 7h7V31zm0 14a7 7 0 1 0 0 14h14V45H47z" fill="#E01E5A" />
                <path d="M31 81a7 7 0 1 0 7 7v-7H31zm14 0a7 7 0 1 0 14 0V67H45v14z" fill="#36C5F0" />
                <path d="M81 97a7 7 0 1 0 7-7h-7v7zm0-14a7 7 0 1 0 0-14H67v14h14z" fill="#2EB67D" />
                <path d="M97 47a7 7 0 1 0-7-7v7h7zm-14 0a7 7 0 1 0-14 0v14h14V47z" fill="#ECB22E" />
              </svg>
              <svg className={styles.gmailLogo} viewBox="0 0 48 48">
                <rect width="48" height="48" rx="10" fill="#ffffff" />
                <path fill="#4caf50" d="M45,16.2l-5,2.75l-5,4.75L35,40h7c1.66,0,3-1.34,3-3V16.2z"/>
                <path fill="#f44336" d="M3,16.2l5,2.75l5,4.75L13,40H6c-1.66,0-3-1.34-3-3V16.2z"/>
                <path fill="#ffeb3b" d="M35,23.7L24,31.7L13,23.7V40h22V23.7z"/>
                <path fill="#2196f3" d="M42,8H6C4.34,8,3,9.34,3,11v5.2l21,15.5l21-15.5V11C45,9.34,43.66,8,42,8z"/>
              </svg>
            </div>
            <p className={styles.integrationText}>
              Connect Slack and Gmail — get answers with full context.
            </p>
            <button className={styles.integrationConnect} onClick={() => alert('Integrations modal: Connect Slack & Gmail')}>
              Connect
            </button>
          </div>
        )}

        {/* Empty / Welcome State */}
        {messages.length === 0 ? (
          <div className={styles.welcomeSection}>
            <Sparkles className={styles.sparklesIcon} />
            <div>
              <h2 className={styles.greetingTitle}>Hi ANKIT!</h2>
              <div className={styles.greetingSub}>Get ready for your meeting</div>
            </div>

            <div className={styles.quickPromptList}>
              <button 
                className={styles.promptPill}
                onClick={() => handleSendMessage("My action items")}
              >
                <CheckCircle2 size={16} color="#10b981" />
                <span>My action items</span>
              </button>

              <button 
                className={styles.promptPill}
                onClick={() => handleSendMessage("Key decisions")}
              >
                <Target size={16} color="#ec4899" />
                <span>Key decisions</span>
              </button>

              <button 
                className={styles.promptPill}
                onClick={() => handleSendMessage("Key initiatives")}
              >
                <Pin size={16} color="#f43f5e" />
                <span>Key initiatives</span>
              </button>
            </div>
          </div>
        ) : (
          <div className={styles.messageList}>
            {messages.map(msg => (
              <div 
                key={msg.id} 
                className={msg.sender === 'user' ? styles.messageUser : styles.messageBot}
              >
                {msg.sender === 'bot' && (
                  <div className={styles.botHeader}>
                    <Bot size={14} />
                    <span>Fred</span>
                  </div>
                )}
                
                <div className={styles.botText}>
                  {msg.text}
                </div>

                {msg.items && msg.items.length > 0 && msg.queryType === 'action_items' && (
                  <div className={styles.actionItemsList}>
                    {msg.items.map((item: any, idx: number) => (
                      <div key={item.id || idx} className={styles.actionItemRow}>
                        <input 
                          type="checkbox" 
                          defaultChecked={item.is_completed} 
                          className={styles.actionCheckbox}
                        />
                        <div className={styles.actionText}>
                          <div>{item.text}</div>
                          <div className={styles.actionMeta}>
                            {item.assignee && `👤 ${item.assignee} · `}
                            {item.meeting_title}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}

            {isTyping && (
              <div className={styles.typingIndicator}>
                <div className={styles.dotPulse} />
                <span>Fred is analyzing your meetings...</span>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input Section at bottom */}
      <div className={styles.inputContainer}>
        <div className={styles.inputCard}>
          <div className={styles.inputChannelTag}>
            <Hash size={12} />
            <span>{channelName}</span>
          </div>

          <textarea 
            className={styles.textArea}
            rows={2}
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask anything. Type / to run AI skills."
          />

          <div className={styles.inputControls}>
            <div className={styles.inputLeftActions}>
              <button 
                className={styles.toolBtn} 
                title="Add context"
                onClick={() => setInputValue(prev => prev + " /summarize ")}
              >
                <Plus size={15} />
              </button>
              <button 
                className={styles.toolBtn} 
                title="AI Skills"
                onClick={() => setInputValue(prev => prev + " /action-items ")}
              >
                <Layers size={15} />
              </button>
            </div>

            <div className={styles.inputRightActions}>
              <button 
                className={`${styles.micBtn} ${isListening ? styles.active : ''}`}
                title={isListening ? "Listening..." : "Voice input"}
                onClick={handleToggleMic}
              >
                <Mic size={15} />
              </button>
              <button 
                className={styles.sendBtn}
                title="Send message"
                disabled={!inputValue.trim() || isTyping}
                onClick={() => handleSendMessage()}
              >
                <ArrowUp size={16} />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

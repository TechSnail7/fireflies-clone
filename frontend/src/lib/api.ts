import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Types
export interface Tag {
  id: number;
  name: string;
  color: string;
}

export interface Meeting {
  id: number;
  title: string;
  date: string;
  duration_seconds: number;
  host: string;
  participants: string[];
  status: string;
  meeting_type: string;
  tags: Tag[];
  action_items_count: number;
  action_items_completed: number;
  created_at: string;
  updated_at: string;
}

export interface TranscriptSegment {
  id: number;
  meeting_id: number;
  speaker: string;
  text: string;
  start_time: number;
  end_time: number;
  order_index: number;
}

export interface Summary {
  id: number;
  meeting_id: number;
  overview: string;
  key_topics: { title: string; description: string }[];
  chapters: { title: string; start_time: number; end_time: number; summary: string }[];
  outline: { heading: string; points: string[] }[];
}

export interface ActionItem {
  id: number;
  meeting_id: number;
  text: string;
  assignee: string | null;
  is_completed: boolean;
  due_date: string | null;
  created_at: string;
}

export interface MeetingDetail extends Meeting {
  segments: TranscriptSegment[];
  summary: Summary | null;
  action_items: ActionItem[];
  video_url?: string;
}

export interface SearchResult {
  meeting_id: number;
  meeting_title: string;
  meeting_date: string;
  segment_id: number | null;
  speaker: string | null;
  text: string;
  start_time: number | null;
  match_type: 'title' | 'transcript' | 'summary' | 'action_item';
}

// API Methods
export const api = {
  getMeetings: async (params?: any) => {
    const { data } = await apiClient.get<Meeting[]>('/meetings', { params });
    return data;
  },
  getMeeting: async (id: number) => {
    const { data } = await apiClient.get<MeetingDetail>(`/meetings/${id}`);
    return data;
  },
  search: async (query: string) => {
    const { data } = await apiClient.get<SearchResult[]>('/search', { params: { q: query } });
    return data;
  },
  uploadTranscript: async (formData: FormData) => {
    const { data } = await apiClient.post('/meetings/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
  askFred: async (query: string, channel: string = 'My Meetings', meetingId?: number) => {
    const { data } = await apiClient.post('/ask-fred', {
      query,
      channel,
      meeting_id: meetingId,
    });
    return data;
  }
};

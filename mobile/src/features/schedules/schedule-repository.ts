import type { Schedule } from '@/shared/api/types';

const MOCK_SCHEDULES: Schedule[] = [
  {
    id: 12,
    space_id: '4e197ffb-b3a9-4345-9573-7e2491442eee',
    space_name: '우리 둘',
    title: '성수 데이트',
    description: '카페 투어',
    start_at: '2026-08-08T04:00:00Z',
    end_at: '2026-08-08T12:00:00Z',
    status: 'planned',
    created_by: { id: 1, nickname: '홍섭' },
    place_count: 3,
    has_diary: false,
  },
  {
    id: 11,
    space_id: 'b9da8630-6eb1-4b3f-af27-ef0bddaa0b9b',
    space_name: '나의 일정',
    title: '한강 산책',
    description: '저녁 노을 사진 남기기',
    start_at: '2026-08-02T09:30:00Z',
    end_at: '2026-08-02T11:00:00Z',
    status: 'completed',
    created_by: { id: 1, nickname: '홍섭' },
    place_count: 1,
    has_diary: true,
  },
];

export async function listMockSchedules(): Promise<Schedule[]> {
  return MOCK_SCHEDULES;
}

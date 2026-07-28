import { useQuery } from '@tanstack/react-query'
import { MOCK_SCHEDULES } from './mocks'

export function useSchedules() {
  return useQuery({
    queryKey: ['schedules'],
    queryFn: () => Promise.resolve(MOCK_SCHEDULES),
  })
}

export function useSchedule(id) {
  return useQuery({
    queryKey: ['schedules', id],
    queryFn: () => Promise.resolve(MOCK_SCHEDULES.find((s) => s.id === id) ?? null),
    enabled: !!id,
  })
}

import { useQuery } from '@tanstack/react-query';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { listMockSchedules } from '@/features/schedules/schedule-repository';
import { ScheduleCard } from '@/features/schedules/schedule-card';
import { colors, spacing } from '@/shared/theme';

export default function CalendarScreen() {
  const schedules = useQuery({ queryKey: ['mock-schedules'], queryFn: listMockSchedules });

  return (
    <SafeAreaView edges={['top']} style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.heading}>
          <Text style={styles.eyebrow}>2026년 8월</Text>
          <Text style={styles.title}>다가오는 일정</Text>
        </View>
        <View style={styles.calendarPlaceholder}>
          <Text style={styles.placeholderTitle}>캘린더 화면 골격</Text>
          <Text style={styles.placeholderText}>스페이스 API 연결 후 월별 일정과 날짜 선택을 연동합니다.</Text>
        </View>
        <View style={styles.list}>
          {schedules.data?.map((schedule) => <ScheduleCard key={schedule.id} schedule={schedule} />)}
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.background },
  content: { padding: spacing.lg, paddingBottom: 120 },
  heading: { gap: spacing.xs, marginBottom: spacing.lg },
  eyebrow: { color: colors.primary, fontSize: 14, fontWeight: '700' },
  title: { color: colors.text, fontSize: 28, fontWeight: '800' },
  calendarPlaceholder: { backgroundColor: colors.primarySoft, borderRadius: 20, padding: spacing.lg },
  placeholderTitle: { color: colors.text, fontSize: 17, fontWeight: '700' },
  placeholderText: { color: colors.muted, lineHeight: 21, marginTop: spacing.sm },
  list: { gap: spacing.md, marginTop: spacing.lg },
});

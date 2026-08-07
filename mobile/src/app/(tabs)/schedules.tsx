import { useQuery } from '@tanstack/react-query';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { ScheduleCard } from '@/features/schedules/schedule-card';
import { listMockSchedules } from '@/features/schedules/schedule-repository';
import { colors, spacing } from '@/shared/theme';

export default function SchedulesScreen() {
  const schedules = useQuery({ queryKey: ['mock-schedules'], queryFn: listMockSchedules });

  return (
    <SafeAreaView edges={['top']} style={styles.safeArea}>
      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.heading}>
          <Text style={styles.title}>일정</Text>
          <Text style={styles.description}>현재는 API 명세와 동일한 구조의 mock을 사용합니다.</Text>
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
  heading: { gap: spacing.sm, marginBottom: spacing.lg },
  title: { color: colors.text, fontSize: 28, fontWeight: '800' },
  description: { color: colors.muted, fontSize: 14 },
  list: { gap: spacing.md },
});

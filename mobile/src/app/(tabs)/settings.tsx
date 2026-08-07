import { Pressable, StyleSheet, Text, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';

import { useAuth } from '@/features/auth/auth-context';
import { colors, spacing } from '@/shared/theme';

export default function SettingsScreen() {
  const { logout, user } = useAuth();

  return (
    <SafeAreaView edges={['top']} style={styles.safeArea}>
      <View style={styles.content}>
        <Text style={styles.title}>설정</Text>
        <View style={styles.profile}>
          <View style={styles.avatar}><Text style={styles.avatarText}>{user?.nickname.slice(0, 1)}</Text></View>
          <View style={styles.profileText}>
            <Text style={styles.nickname}>{user?.nickname}</Text>
            <Text style={styles.email}>{user?.email}</Text>
          </View>
        </View>
        <Pressable onPress={logout} style={({ pressed }) => [styles.logoutButton, pressed && styles.pressed]}>
          <Text style={styles.logoutText}>로그아웃</Text>
        </Pressable>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: { flex: 1, backgroundColor: colors.background },
  content: { flex: 1, padding: spacing.lg },
  title: { color: colors.text, fontSize: 28, fontWeight: '800', marginBottom: spacing.xl },
  profile: { alignItems: 'center', backgroundColor: colors.surface, borderColor: colors.border, borderRadius: 18, borderWidth: 1, flexDirection: 'row', padding: spacing.lg },
  avatar: { alignItems: 'center', backgroundColor: colors.primarySoft, borderRadius: 24, height: 48, justifyContent: 'center', width: 48 },
  avatarText: { color: colors.primary, fontSize: 20, fontWeight: '800' },
  profileText: { gap: 3, marginLeft: spacing.md },
  nickname: { color: colors.text, fontSize: 17, fontWeight: '700' },
  email: { color: colors.muted, fontSize: 14 },
  logoutButton: { alignItems: 'center', borderColor: colors.border, borderRadius: 14, borderWidth: 1, marginTop: spacing.lg, paddingVertical: 15 },
  logoutText: { color: colors.danger, fontSize: 15, fontWeight: '700' },
  pressed: { opacity: 0.65 },
});

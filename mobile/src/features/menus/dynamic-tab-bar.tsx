import type { Href } from 'expo-router';
import { useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { colors, spacing } from '@/shared/theme';
import { useMenus } from './menu-api';

const iconGlyphs: Record<string, string> = {
  calendar: '▦',
  list: '☰',
  settings: '⚙',
};

type DynamicTabBarProps = {
  state: { index: number; routes: { name: string }[] };
};

export function DynamicTabBar({ state }: DynamicTabBarProps) {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { data: menus = [] } = useMenus();
  const activeRoute = state.routes[state.index]?.name;

  return (
    <View style={[styles.container, { paddingBottom: Math.max(insets.bottom, spacing.sm) }]}>
      {menus.map((menu) => {
        if (!menu.path) return null;
        const routeName = menu.path.replace(/^\//, '');
        const active = routeName === activeRoute;
        return (
          <Pressable key={menu.code} onPress={() => router.push(menu.path as Href)} style={styles.item}>
            <Text style={[styles.icon, active && styles.active]}>{iconGlyphs[menu.icon ?? ''] ?? '•'}</Text>
            <Text numberOfLines={1} style={[styles.label, active && styles.active]}>{menu.name}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { backgroundColor: colors.surface, borderTopColor: colors.border, borderTopWidth: 1, flexDirection: 'row', paddingHorizontal: spacing.sm, paddingTop: spacing.sm },
  item: { alignItems: 'center', flex: 1, gap: 3, minHeight: 52 },
  icon: { color: colors.muted, fontSize: 21, fontWeight: '700' },
  label: { color: colors.muted, fontSize: 11, fontWeight: '600' },
  active: { color: colors.primary },
});

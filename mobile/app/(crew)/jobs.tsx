import React from 'react';
import { View, Text, FlatList, Pressable, StyleSheet, RefreshControl } from 'react-native';
import { router } from 'expo-router';
import { useJobs } from '@/state/JobProvider';
import { StatusChip } from '@/components/Chip';
import { colors, radius, spacing, type } from '@/theme';

/** Job packet list — today's work orders (pre-job). */
export default function JobsScreen() {
  const { jobs, loading, offline, refresh } = useJobs();

  return (
    <View style={styles.wrap}>
      {offline ? (
        <View style={styles.offline}>
          <Text style={styles.offlineText}>Offline — showing last synced packet</Text>
        </View>
      ) : null}
      <FlatList
        data={jobs}
        keyExtractor={(j) => j.job_id}
        contentContainerStyle={{ padding: spacing.lg }}
        refreshControl={<RefreshControl refreshing={loading} onRefresh={refresh} />}
        ListEmptyComponent={<Text style={styles.empty}>No jobs assigned.</Text>}
        renderItem={({ item }) => (
          <Pressable
            style={styles.card}
            onPress={() => router.push(`/(crew)/job/${item.job_id}`)}
          >
            <View style={styles.cardHead}>
              <Text style={styles.title}>{item.zone.label}</Text>
              <StatusChip label={item.status} status={item.status} />
            </View>
            <Text style={styles.meta}>
              {item.zone.surface_type.replace(/_/g, ' ')} · attempt {item.attempt}
            </Text>
          </Pressable>
        )}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1 },
  offline: { backgroundColor: '#fff6e6', padding: spacing.sm, alignItems: 'center' },
  offlineText: { color: '#8a5a00', fontSize: type.small, fontWeight: '600' },
  card: { backgroundColor: colors.surface, borderRadius: radius.card, padding: spacing.lg, marginBottom: spacing.md },
  cardHead: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  title: { fontSize: type.h2, fontWeight: '700', color: colors.ink, flexShrink: 1 },
  meta: { color: colors.muted, fontSize: type.small, marginTop: 4 },
  empty: { textAlign: 'center', color: colors.muted, marginTop: spacing.xl },
});

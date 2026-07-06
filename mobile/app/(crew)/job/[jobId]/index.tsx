import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { useJobs } from '@/state/JobProvider';
import { useJobTelemetry } from '@/telemetry/useTelemetry';
import { StatusChip } from '@/components/Chip';
import { Button } from '@/components/Button';
import { colors, radius, spacing, type } from '@/theme';

/** Job overview — zone status + entry into the per-zone execution flow. */
export default function JobScreen() {
  const { jobId } = useLocalSearchParams<{ jobId: string }>();
  const { jobs } = useJobs();
  const job = jobs.find((j) => j.job_id === jobId);
  const { latest, connected } = useJobTelemetry(jobId);

  if (!job) {
    return (
      <View style={styles.wrap}>
        <Text style={styles.meta}>Job not found in current packet.</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.wrap}>
      <View style={styles.card}>
        <View style={styles.head}>
          <Text style={styles.title}>{job.zone.label}</Text>
          <StatusChip label={job.status} status={job.status} />
        </View>
        <Text style={styles.meta}>
          {job.zone.surface_type.replace(/_/g, ' ')} · pitch {job.zone.pitch_deg}° · grime{' '}
          {(job.zone.grime_confidence * 100).toFixed(0)}% (proxy)
        </Text>
        <Text style={[styles.meta, { color: connected ? colors.green : colors.muted }]}>
          telemetry {connected ? 'live' : 'offline'}
          {latest?.status ? ` · ${latest.status}` : ''}
        </Text>
      </View>

      <Button
        label="Start zone"
        variant="go"
        onPress={() => router.push(`/(crew)/job/${jobId}/zone/${job.zone.zone_id}`)}
      />
      <Button
        label="Job summary"
        variant="ghost"
        onPress={() => router.push(`/(crew)/job/${jobId}/summary`)}
      />
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { padding: spacing.lg, gap: spacing.sm },
  card: { backgroundColor: colors.surface, borderRadius: radius.card, padding: spacing.lg, marginBottom: spacing.sm },
  head: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  title: { fontSize: type.h1, fontWeight: '800', color: colors.ink, flexShrink: 1 },
  meta: { color: colors.muted, fontSize: type.small, marginTop: 4 },
});

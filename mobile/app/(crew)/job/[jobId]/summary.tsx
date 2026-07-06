import React, { useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useLocalSearchParams } from 'expo-router';
import { getVerifications } from '@/api/jobs';
import { VerdictCard } from '@/features/verify/VerdictCard';
import { colors, spacing, type } from '@/theme';
import type { VerificationResult } from '@/api/types';

/** End-of-job recap: verdicts per attempt, re-queued zones. */
export default function SummaryScreen() {
  const { jobId } = useLocalSearchParams<{ jobId: string }>();
  const [results, setResults] = useState<VerificationResult[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!jobId) return;
    getVerifications(jobId)
      .then(setResults)
      .catch(() => setError('Could not load verifications (offline?).'));
  }, [jobId]);

  return (
    <ScrollView contentContainerStyle={styles.wrap}>
      {error ? <Text style={styles.meta}>{error}</Text> : null}
      {results.length === 0 && !error ? (
        <Text style={styles.meta}>No verification results yet.</Text>
      ) : null}
      {results.map((r, i) => (
        <View key={`${r.zone_id}-${r.attempt}-${i}`} style={styles.item}>
          <Text style={styles.zoneLabel}>
            {r.zone_id} · attempt {r.attempt}
          </Text>
          <VerdictCard result={r} />
        </View>
      ))}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { padding: spacing.lg, gap: spacing.md },
  item: { gap: spacing.xs },
  zoneLabel: { color: colors.muted, fontSize: type.small, fontWeight: '700' },
  meta: { color: colors.muted, fontSize: type.small, textAlign: 'center', marginTop: spacing.xl },
});

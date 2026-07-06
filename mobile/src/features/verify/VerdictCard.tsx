import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, radius, type } from '@/theme';
import type { VerificationResult } from '@/api/types';

/** Post-Clean agent verdict: PASS ✓ or FAIL → retry-with-new-params. */
export function VerdictCard({ result }: { result: VerificationResult }) {
  const pass = result.verdict === 'PASS';
  const delta = result.delta_applied
    ? Object.entries(result.delta_applied)
        .map(([k, v]) => `${k} ${Number(v) > 0 ? '+' : ''}${v}`)
        .join(', ')
    : null;

  return (
    <View style={styles.card}>
      <Text style={[styles.icon, { color: pass ? colors.green : colors.red }]}>
        {pass ? '✓' : '↻'}
      </Text>
      <Text style={styles.title}>{pass ? 'PASS' : 'RE-QUEUE'}</Text>

      <View style={styles.metric}>
        <Text style={styles.k}>Residual (proxy)</Text>
        <Text style={styles.v}>{result.residual_confidence.toFixed(2)}</Text>
      </View>
      <View style={styles.metric}>
        <Text style={styles.k}>Threshold</Text>
        <Text style={styles.v}>{result.threshold.toFixed(2)}</Text>
      </View>
      {!pass && delta ? (
        <View style={styles.metric}>
          <Text style={styles.k}>Adjustment</Text>
          <Text style={styles.v}>{delta}</Text>
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: colors.surface, borderRadius: radius.card, padding: 18, alignItems: 'center' },
  icon: { fontSize: 46 },
  title: { fontSize: type.h1, fontWeight: '800', color: colors.ink, marginBottom: 8 },
  metric: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    width: '100%',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: colors.bg,
  },
  k: { fontSize: type.small, color: colors.muted },
  v: { fontSize: type.body, fontWeight: '700', color: colors.ink, fontVariant: ['tabular-nums'] },
});

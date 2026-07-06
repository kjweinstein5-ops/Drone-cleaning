import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, radius, type } from '@/theme';

/**
 * "Fit nozzle #N" hardware-confirmation step (CLAUDE.md §10). The operator
 * physically fits the nozzle and confirms — the app minimises skill, not authority.
 */
export function NozzlePrompt({
  nozzleId,
  angleDeg,
  orificeMm,
}: {
  nozzleId: number;
  angleDeg?: number | null;
  orificeMm?: number | null;
}) {
  const spec = [
    angleDeg ? `${angleDeg}° fan` : null,
    orificeMm ? `${orificeMm} mm orifice` : null,
  ]
    .filter(Boolean)
    .join(' · ');

  return (
    <View style={styles.card}>
      <Text style={styles.label}>FIT NOZZLE</Text>
      <Text style={styles.num}>#{nozzleId}</Text>
      {spec ? <Text style={styles.spec}>{spec}</Text> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surfaceAlt,
    borderRadius: radius.card,
    padding: 18,
    alignItems: 'center',
  },
  label: { color: colors.muted, fontSize: type.small, letterSpacing: 0.6, fontWeight: '700' },
  num: { color: colors.blue, fontSize: 40, fontWeight: '800' },
  spec: { color: colors.ink, fontSize: type.small },
});

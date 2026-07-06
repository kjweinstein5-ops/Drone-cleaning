import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, radius, type } from '@/theme';
import type { Prescription } from '@/api/types';

/** Read-only display of the Supervisor agent's prescription for a zone. */
export function PrescriptionCard({ rx }: { rx: Prescription }) {
  const rows: [string, string][] = [
    ['Pressure', `${rx.pressure_bar} bar`],
    ['Chemical', rx.chemical.replace(/_/g, ' ')],
    ['Mix (solution:DI)', `${Math.round(rx.chemical_mix_ratio * 100)}%`],
    ['Dwell', `${rx.dwell_seconds} s`],
    ['Nozzle', `#${rx.nozzle_id}${rx.nozzle_angle_deg ? ` · ${rx.nozzle_angle_deg}°` : ''}`],
    ['Standoff', `${rx.standoff_m} m`],
    ['Pattern', rx.coverage_pattern.replace(/_/g, ' ')],
  ];

  return (
    <View style={styles.card}>
      {rows.map(([k, v]) => (
        <View key={k} style={styles.row}>
          <Text style={styles.key}>{k}</Text>
          <Text style={styles.val}>{v}</Text>
        </View>
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: colors.surface, borderRadius: radius.card, padding: 16 },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderBottomColor: colors.bg,
  },
  key: { color: colors.muted, fontSize: type.small, textTransform: 'uppercase', letterSpacing: 0.4 },
  val: { fontSize: type.body, fontWeight: '600', color: colors.ink },
});

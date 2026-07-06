import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, radius, type } from '@/theme';
import type { WorkOrderStatus } from '@/api/types';

/** Maps a work-order status to the demo mockup's chip colours. */
function chipStyle(status: WorkOrderStatus): { bg: string; fg: string } {
  switch (status) {
    case 'done':
      return { bg: '#e3f5ea', fg: colors.green };
    case 'executing':
    case 'verifying':
    case 'assigned':
      return { bg: '#dbeafe', fg: colors.blue };
    case 'reflagged':
      return { bg: '#fdecea', fg: colors.red };
    default:
      return { bg: colors.bg, fg: colors.muted };
  }
}

export function StatusChip({ label, status }: { label: string; status: WorkOrderStatus }) {
  const { bg, fg } = chipStyle(status);
  return (
    <View style={[styles.chip, { backgroundColor: bg }]}>
      <Text style={[styles.text, { color: fg }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  chip: { paddingHorizontal: 9, paddingVertical: 4, borderRadius: radius.chip },
  text: { fontSize: type.tiny, fontWeight: '600' },
});

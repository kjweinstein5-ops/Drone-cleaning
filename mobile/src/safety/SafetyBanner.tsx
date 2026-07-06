import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors, radius, type } from '@/theme';
import { safetyNotesFor, type SafetyNote } from './ceilings';
import type { SurfaceType, Prescription } from '@/api/types';

const LEVEL_STYLE: Record<SafetyNote['level'], { bg: string; border: string; fg: string }> = {
  info: { bg: '#eef6ff', border: '#cfe3fb', fg: '#1a5fa0' },
  warn: { bg: '#fff6e6', border: '#ffe2a8', fg: '#8a5a00' },
  critical: { bg: '#fdecea', border: '#f1b9b3', fg: colors.red },
};

/** Advisory-only. Renders the safety notes from ceilings.ts — never gates hardware. */
export function SafetyBanner({
  surface,
  prescription,
}: {
  surface: SurfaceType;
  prescription: Prescription;
}) {
  const notes = safetyNotesFor(surface, prescription);
  if (notes.length === 0) return null;

  return (
    <View style={styles.wrap}>
      {notes.map((note, i) => {
        const s = LEVEL_STYLE[note.level];
        return (
          <View
            key={i}
            style={[styles.note, { backgroundColor: s.bg, borderColor: s.border }]}
          >
            <Text style={[styles.text, { color: s.fg }]}>{note.message}</Text>
          </View>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { gap: 8, marginVertical: 12 },
  note: { borderRadius: radius.button, borderWidth: 1, padding: 12 },
  text: { fontSize: type.small, fontWeight: '600' },
});

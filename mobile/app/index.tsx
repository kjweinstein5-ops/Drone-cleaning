import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { router } from 'expo-router';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Button } from '@/components/Button';
import { colors, spacing, type } from '@/theme';

/**
 * Entry / device-pair screen. In a real build this captures the operator's
 * identity and confirms a valid Part 107 pilot is on record before any job
 * (CLAUDE.md §10 — operator stays in command).
 *
 * TODO(PROPWASH): real auth + pilot-on-record check via expo-secure-store.
 */
export default function Landing() {
  return (
    <SafeAreaView style={styles.wrap}>
      <View style={styles.center}>
        <Text style={styles.brand}>PROPWASH</Text>
        <Text style={styles.sub}>Operator field app</Text>
      </View>
      <View style={styles.footer}>
        <Button label="Start shift" onPress={() => router.replace('/(crew)/jobs')} />
        <Text style={styles.note}>
          Operator in command · FAA Part 107. This app assists execution; it never flies or
          sprays autonomously.
        </Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, backgroundColor: colors.blue, padding: spacing.xl, justifyContent: 'space-between' },
  center: { flex: 1, alignItems: 'center', justifyContent: 'center' },
  brand: { color: '#fff', fontSize: 36, fontWeight: '800', letterSpacing: 2 },
  sub: { color: '#dbeafe', fontSize: type.body, marginTop: 4 },
  footer: { gap: spacing.md },
  note: { color: '#dbeafe', fontSize: type.tiny, textAlign: 'center' },
});

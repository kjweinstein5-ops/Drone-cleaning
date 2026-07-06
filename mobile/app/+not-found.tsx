import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { Link } from 'expo-router';
import { colors, spacing, type } from '@/theme';

export default function NotFound() {
  return (
    <View style={styles.wrap}>
      <Text style={styles.title}>Screen not found</Text>
      <Link href="/(crew)/jobs" style={styles.link}>
        Back to jobs
      </Link>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: spacing.xl },
  title: { fontSize: type.h1, fontWeight: '700', color: colors.ink },
  link: { marginTop: spacing.md, color: colors.blue, fontSize: type.body, fontWeight: '600' },
});

import React from 'react';
import { Stack } from 'expo-router';
import { colors } from '@/theme';

/** Authed crew stack. TODO(PROPWASH): guard on a valid pilot session. */
export default function CrewLayout() {
  return (
    <Stack
      screenOptions={{
        headerStyle: { backgroundColor: colors.blue },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: '800' },
        contentStyle: { backgroundColor: colors.surfaceAlt },
      }}
    >
      <Stack.Screen name="jobs" options={{ title: 'Today’s jobs' }} />
      <Stack.Screen name="job/[jobId]/index" options={{ title: 'Job' }} />
      <Stack.Screen name="job/[jobId]/zone/[zoneId]" options={{ title: 'Zone' }} />
      <Stack.Screen name="job/[jobId]/summary" options={{ title: 'Summary' }} />
    </Stack>
  );
}

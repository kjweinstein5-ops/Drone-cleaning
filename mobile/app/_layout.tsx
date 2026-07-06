import React from 'react';
import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { SafeAreaProvider } from 'react-native-safe-area-context';
import { JobProvider } from '@/state/JobProvider';
import { TelemetryProvider } from '@/telemetry/TelemetryProvider';
import { colors } from '@/theme';

/** Root layout — wires the global providers around the whole operator flow. */
export default function RootLayout() {
  return (
    <SafeAreaProvider>
      <TelemetryProvider>
        <JobProvider>
          <StatusBar style="light" />
          <Stack
            screenOptions={{
              headerStyle: { backgroundColor: colors.blue },
              headerTintColor: '#fff',
              headerTitleStyle: { fontWeight: '800' },
              contentStyle: { backgroundColor: colors.surfaceAlt },
            }}
          >
            <Stack.Screen name="index" options={{ headerShown: false }} />
            <Stack.Screen name="(crew)" options={{ headerShown: false }} />
          </Stack>
        </JobProvider>
      </TelemetryProvider>
    </SafeAreaProvider>
  );
}

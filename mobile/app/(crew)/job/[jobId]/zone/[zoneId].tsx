import React from 'react';
import { ScrollView, StyleSheet, View, Text } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import { useJobs } from '@/state/JobProvider';
import { useZoneExecution } from '@/hooks/useZoneExecution';
import { NozzlePrompt } from '@/features/zone/NozzlePrompt';
import { PrescriptionCard } from '@/features/zone/PrescriptionCard';
import { DwellTimer } from '@/features/zone/DwellTimer';
import { SafetyBanner } from '@/safety/SafetyBanner';
import { Button } from '@/components/Button';
import { colors, spacing, type } from '@/theme';

/**
 * PER-ZONE EXECUTION — the heart of the operator loop (CLAUDE.md §10).
 *   ready -> (fit nozzle, confirm) -> spraying (dwell) -> verifying -> verdict
 * Abort is always available; the operator is never removed from command.
 */
export default function ZoneScreen() {
  const { jobId, zoneId } = useLocalSearchParams<{ jobId: string; zoneId: string }>();
  const { jobs } = useJobs();
  const job = jobs.find((j) => j.job_id === jobId && j.zone.zone_id === zoneId);
  const exec = useZoneExecution(jobId!);

  if (!job) {
    return (
      <View style={styles.wrap}>
        <Text style={styles.meta}>Zone not found.</Text>
      </View>
    );
  }

  const { zone, prescription } = job;

  return (
    <ScrollView contentContainerStyle={styles.wrap}>
      <Text style={styles.h1}>{zone.label}</Text>

      <SafetyBanner surface={zone.surface_type} prescription={prescription} />

      {exec.phase === 'ready' && (
        <>
          <NozzlePrompt
            nozzleId={prescription.nozzle_id}
            angleDeg={prescription.nozzle_angle_deg}
            orificeMm={prescription.nozzle_orifice_mm}
          />
          <PrescriptionCard rx={prescription} />
          <Button label="Nozzle fitted — begin spray" variant="go" onPress={exec.beginSpray} />
        </>
      )}

      {exec.phase === 'spraying' && (
        <>
          <DwellTimer
            seconds={prescription.dwell_seconds}
            running
            onComplete={exec.beginVerify}
          />
          <Text style={styles.meta}>Monitor video + thermal overlay. Hold standoff {prescription.standoff_m} m.</Text>
          <Button label="Abort" variant="abort" onPress={exec.abort} />
        </>
      )}

      {exec.phase === 'verifying' && (
        <>
          <Text style={styles.meta}>Post-clean re-scan in progress…</Text>
          <Button
            label="View verdict"
            onPress={() => router.push(`/(crew)/job/${jobId}/summary`)}
          />
        </>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  wrap: { padding: spacing.lg, gap: spacing.sm },
  h1: { fontSize: type.h1, fontWeight: '800', color: colors.ink },
  meta: { color: colors.muted, fontSize: type.small, textAlign: 'center', marginVertical: spacing.sm },
});

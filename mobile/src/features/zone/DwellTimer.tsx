import React, { useEffect, useRef, useState } from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { colors } from '@/theme';

/**
 * Big per-zone dwell countdown (mirrors the demo mockup). Purely a timing aid
 * for the operator — it does not command the pump. Operator starts/stops.
 */
export function DwellTimer({
  seconds,
  running,
  onComplete,
}: {
  seconds: number;
  running: boolean;
  onComplete?: () => void;
}) {
  const [remaining, setRemaining] = useState(seconds);
  const done = useRef(false);

  useEffect(() => {
    setRemaining(seconds);
    done.current = false;
  }, [seconds]);

  useEffect(() => {
    if (!running) return;
    const id = setInterval(() => {
      setRemaining((r) => {
        if (r <= 1) {
          clearInterval(id);
          if (!done.current) {
            done.current = true;
            onComplete?.();
          }
          return 0;
        }
        return r - 1;
      });
    }, 1000);
    return () => clearInterval(id);
  }, [running, onComplete]);

  return (
    <View style={styles.wrap}>
      <Text style={styles.big}>{remaining}</Text>
      <Text style={styles.unit}>seconds dwell</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { alignItems: 'center', paddingVertical: 24 },
  big: { fontSize: 54, fontWeight: '800', color: colors.blue, fontVariant: ['tabular-nums'] },
  unit: { color: colors.muted, fontSize: 13 },
});

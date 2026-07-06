import React from 'react';
import { Pressable, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { colors, radius, type } from '@/theme';

type Variant = 'primary' | 'go' | 'ghost' | 'abort';

const VARIANT_BG: Record<Variant, string> = {
  primary: colors.blue,
  go: colors.green,
  ghost: colors.surface,
  abort: colors.surface,
};

const VARIANT_FG: Record<Variant, string> = {
  primary: '#fff',
  go: '#fff',
  ghost: colors.ink,
  abort: colors.red,
};

export function Button({
  label,
  onPress,
  variant = 'primary',
  loading = false,
  disabled = false,
}: {
  label: string;
  onPress: () => void;
  variant?: Variant;
  loading?: boolean;
  disabled?: boolean;
}) {
  const bordered = variant === 'ghost' || variant === 'abort';
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      disabled={disabled || loading}
      style={({ pressed }) => [
        styles.btn,
        { backgroundColor: VARIANT_BG[variant] },
        bordered && {
          borderWidth: 1.5,
          borderColor: variant === 'abort' ? '#f1b9b3' : colors.border,
        },
        (disabled || loading) && styles.disabled,
        pressed && styles.pressed,
      ]}
    >
      {loading ? (
        <ActivityIndicator color={VARIANT_FG[variant]} />
      ) : (
        <Text style={[styles.label, { color: VARIANT_FG[variant] }]}>{label}</Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    width: '100%',
    borderRadius: radius.button,
    paddingVertical: 16,
    alignItems: 'center',
    marginTop: 10,
  },
  label: { fontSize: type.body, fontWeight: '700' },
  disabled: { opacity: 0.5 },
  pressed: { transform: [{ scale: 0.99 }] },
});

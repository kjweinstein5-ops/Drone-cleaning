/** Design tokens lifted from samples/operator_app_demo.html so the native app
 *  matches the approved operator mockup. */

export const colors = {
  blue: '#0b6cc4',
  green: '#1a9e54',
  red: '#c0392b',
  amber: '#e08e0b',
  ink: '#1c2733',
  muted: '#7a8794',
  bg: '#eef1f4',
  surface: '#ffffff',
  surfaceAlt: '#f7f9fb',
  border: '#d4dbe2',
} as const;

export const spacing = {
  xs: 4,
  sm: 8,
  md: 12,
  lg: 16,
  xl: 24,
} as const;

export const radius = {
  chip: 20,
  card: 16,
  button: 12,
} as const;

export const type = {
  h1: 20,
  h2: 17,
  body: 16,
  small: 13,
  tiny: 11,
} as const;

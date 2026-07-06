/**
 * Durable key-value storage backed by MMKV (fast, synchronous, survives restarts).
 * Holds the cached job packet and the pending-action outbox so a dropped LTE
 * link never loses the operator's confirmations.
 */
import { MMKV } from 'react-native-mmkv';

const store = new MMKV({ id: 'propwash-operator' });

export const storage = {
  getJSON<T>(key: string): T | null {
    const raw = store.getString(key);
    return raw ? (JSON.parse(raw) as T) : null;
  },
  setJSON(key: string, value: unknown): void {
    store.set(key, JSON.stringify(value));
  },
  delete(key: string): void {
    store.delete(key);
  },
};

export const KEYS = {
  jobPacket: 'jobPacket',
  outbox: 'outbox',
} as const;

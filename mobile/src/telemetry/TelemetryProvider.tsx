/** Provides the live telemetry stream to the tree. One socket per app session. */
import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { connectTelemetry } from './socket';
import type { TelemetryEvent } from '@/api/types';

interface TelemetryContextValue {
  connected: boolean;
  lastEvent: TelemetryEvent | null;
  subscribe: (listener: (e: TelemetryEvent) => void) => () => void;
}

const TelemetryContext = createContext<TelemetryContextValue | null>(null);

export function TelemetryProvider({ children }: { children: React.ReactNode }) {
  const [connected, setConnected] = useState(false);
  const [lastEvent, setLastEvent] = useState<TelemetryEvent | null>(null);
  const listeners = useRef(new Set<(e: TelemetryEvent) => void>());

  useEffect(() => {
    const socket = connectTelemetry((event) => {
      setConnected(true);
      setLastEvent(event);
      listeners.current.forEach((l) => l(event));
    });
    return () => socket.close();
  }, []);

  const subscribe = (listener: (e: TelemetryEvent) => void) => {
    listeners.current.add(listener);
    return () => listeners.current.delete(listener);
  };

  return (
    <TelemetryContext.Provider value={{ connected, lastEvent, subscribe }}>
      {children}
    </TelemetryContext.Provider>
  );
}

export function useTelemetryContext(): TelemetryContextValue {
  const ctx = useContext(TelemetryContext);
  if (!ctx) throw new Error('useTelemetryContext must be used within <TelemetryProvider>');
  return ctx;
}

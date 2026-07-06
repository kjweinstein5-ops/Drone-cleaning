/// <reference types="expo/types" />

// Ambient types for EXPO_PUBLIC_* env vars used in the app.
declare namespace NodeJS {
  interface ProcessEnv {
    EXPO_PUBLIC_API_URL?: string;
    EXPO_PUBLIC_WS_URL?: string;
  }
}

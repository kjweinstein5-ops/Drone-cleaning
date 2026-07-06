/**
 * Thin fetch wrapper for the PROPWASH backend.
 * Mirrors frontend/src/api.js but typed and with field-grade retry/backoff.
 */

const API_URL = process.env.EXPO_PUBLIC_API_URL ?? 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface RequestOptions extends RequestInit {
  /** Network-error retries (NOT applied to 4xx/5xx responses). */
  retries?: number;
}

async function request<T>(path: string, opts: RequestOptions = {}): Promise<T> {
  const { retries = 3, ...init } = opts;
  const url = `${API_URL}${path}`;

  let lastErr: unknown;
  for (let attempt = 0; attempt <= retries; attempt++) {
    try {
      const res = await fetch(url, {
        ...init,
        headers: { 'Content-Type': 'application/json', ...init.headers },
      });
      if (!res.ok) {
        // A real HTTP response — do not retry, surface it.
        throw new ApiError(`${init.method ?? 'GET'} ${path} -> ${res.status}`, res.status);
      }
      return (await res.json()) as T;
    } catch (err) {
      if (err instanceof ApiError) throw err;
      // Network/transport failure — retry with exponential backoff.
      lastErr = err;
      if (attempt < retries) {
        await new Promise((r) => setTimeout(r, 2 ** attempt * 500));
      }
    }
  }
  throw lastErr;
}

export const api = {
  get: <T>(path: string, opts?: RequestOptions) => request<T>(path, { ...opts, method: 'GET' }),
  post: <T>(path: string, body: unknown, opts?: RequestOptions) =>
    request<T>(path, { ...opts, method: 'POST', body: JSON.stringify(body) }),
};

export const apiBaseUrl = API_URL;

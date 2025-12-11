import { useState, useEffect, useCallback, useRef } from 'react';

export interface UseFetchOptions {
  /** Whether to fetch immediately on mount */
  immediate?: boolean;
  /** Cache key for deduplication */
  cacheKey?: string;
  /** Refetch interval in milliseconds */
  refetchInterval?: number;
  /** Whether to refetch on window focus */
  refetchOnFocus?: boolean;
}

export interface UseFetchReturn<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
  mutate: (data: T | null) => void;
}

// Simple in-memory cache
const cache = new Map<string, { data: unknown; timestamp: number }>();
const CACHE_TTL = 30000; // 30 seconds

function getCachedData<T>(key: string): T | null {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data as T;
  }
  cache.delete(key);
  return null;
}

function setCachedData<T>(key: string, data: T): void {
  cache.set(key, { data, timestamp: Date.now() });
}

/**
 * Hook for fetching data with automatic loading/error states and caching
 * @param fetchFn Function that returns a promise with the data
 * @param options Configuration options
 */
export function useFetch<T>(
  fetchFn: () => Promise<T>,
  options: UseFetchOptions = {}
): UseFetchReturn<T> {
  const {
    immediate = true,
    cacheKey,
    refetchInterval,
    refetchOnFocus = false,
  } = options;

  const [data, setData] = useState<T | null>(() =>
    cacheKey ? getCachedData<T>(cacheKey) : null
  );
  const [loading, setLoading] = useState(immediate && !data);
  const [error, setError] = useState<Error | null>(null);

  const mountedRef = useRef(true);
  const fetchIdRef = useRef(0);

  const fetch = useCallback(async () => {
    const fetchId = ++fetchIdRef.current;

    setLoading(true);
    setError(null);

    try {
      const result = await fetchFn();

      if (mountedRef.current && fetchId === fetchIdRef.current) {
        setData(result);
        if (cacheKey) {
          setCachedData(cacheKey, result);
        }
      }
    } catch (err) {
      if (mountedRef.current && fetchId === fetchIdRef.current) {
        setError(err instanceof Error ? err : new Error(String(err)));
      }
    } finally {
      if (mountedRef.current && fetchId === fetchIdRef.current) {
        setLoading(false);
      }
    }
  }, [fetchFn, cacheKey]);

  const refetch = useCallback(async () => {
    await fetch();
  }, [fetch]);

  const mutate = useCallback((newData: T | null) => {
    setData(newData);
    if (cacheKey && newData !== null) {
      setCachedData(cacheKey, newData);
    }
  }, [cacheKey]);

  // Initial fetch
  useEffect(() => {
    mountedRef.current = true;

    if (immediate) {
      fetch();
    }

    return () => {
      mountedRef.current = false;
    };
  }, [immediate, fetch]);

  // Refetch on interval
  useEffect(() => {
    if (!refetchInterval) return;

    const intervalId = setInterval(fetch, refetchInterval);
    return () => clearInterval(intervalId);
  }, [refetchInterval, fetch]);

  // Refetch on window focus
  useEffect(() => {
    if (!refetchOnFocus) return;

    const handleFocus = () => {
      fetch();
    };

    window.addEventListener('focus', handleFocus);
    return () => window.removeEventListener('focus', handleFocus);
  }, [refetchOnFocus, fetch]);

  return {
    data,
    loading,
    error,
    refetch,
    mutate,
  };
}

export default useFetch;

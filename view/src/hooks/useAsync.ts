import { useState, useCallback, useRef, useEffect } from 'react';

export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: Error | null;
}

export interface UseAsyncReturn<T, Args extends unknown[]> extends AsyncState<T> {
  execute: (...args: Args) => Promise<T | undefined>;
  reset: () => void;
  setData: (data: T | null) => void;
}

/**
 * Hook for managing async operations with loading, error, and data states
 * @param asyncFunction The async function to execute
 * @param immediate Whether to execute immediately on mount
 */
export function useAsync<T, Args extends unknown[] = []>(
  asyncFunction: (...args: Args) => Promise<T>,
  immediate = false
): UseAsyncReturn<T, Args> {
  const [state, setState] = useState<AsyncState<T>>({
    data: null,
    loading: immediate,
    error: null,
  });

  // Track if component is mounted to prevent state updates after unmount
  const mountedRef = useRef(true);
  const lastCallIdRef = useRef(0);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const execute = useCallback(
    async (...args: Args): Promise<T | undefined> => {
      const callId = ++lastCallIdRef.current;

      setState((prev) => ({ ...prev, loading: true, error: null }));

      try {
        const result = await asyncFunction(...args);

        // Only update state if this is the most recent call and component is mounted
        if (mountedRef.current && callId === lastCallIdRef.current) {
          setState({ data: result, loading: false, error: null });
        }

        return result;
      } catch (error) {
        // Only update state if this is the most recent call and component is mounted
        if (mountedRef.current && callId === lastCallIdRef.current) {
          const err = error instanceof Error ? error : new Error(String(error));
          setState({ data: null, loading: false, error: err });
        }

        return undefined;
      }
    },
    [asyncFunction]
  );

  const reset = useCallback(() => {
    lastCallIdRef.current++;
    setState({ data: null, loading: false, error: null });
  }, []);

  const setData = useCallback((data: T | null) => {
    setState((prev) => ({ ...prev, data }));
  }, []);

  // Execute immediately if requested
  useEffect(() => {
    if (immediate) {
      execute(...([] as unknown as Args));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [immediate]);

  return {
    ...state,
    execute,
    reset,
    setData,
  };
}

export default useAsync;

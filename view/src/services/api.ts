/**
 * Base API client for making HTTP requests to the FastAPI backend
 */

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: unknown
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

interface RequestOptions extends RequestInit {
  params?: Record<string, string | number | boolean | undefined>;
}

/**
 * Build URL with query parameters
 */
function buildUrl(path: string, params?: Record<string, string | number | boolean | undefined>): string {
  const url = new URL(path, API_URL);

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      if (value !== undefined) {
        url.searchParams.append(key, String(value));
      }
    });
  }

  return url.toString();
}

/**
 * Base fetch function with error handling
 */
async function request<T>(
  path: string,
  options: RequestOptions = {}
): Promise<T> {
  const { params, ...fetchOptions } = options;
  const url = buildUrl(path, params);

  const defaultHeaders: HeadersInit = {
    'Content-Type': 'application/json',
  };

  const response = await fetch(url, {
    ...fetchOptions,
    headers: {
      ...defaultHeaders,
      ...fetchOptions.headers,
    },
  });

  if (!response.ok) {
    let errorData: unknown;
    try {
      errorData = await response.json();
    } catch {
      errorData = await response.text();
    }
    throw new ApiError(
      `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData
    );
  }

  // Handle empty responses
  const contentType = response.headers.get('content-type');
  if (contentType?.includes('application/json')) {
    return response.json();
  }

  return {} as T;
}

/**
 * GET request
 */
export async function get<T>(
  path: string,
  params?: Record<string, string | number | boolean | undefined>
): Promise<T> {
  return request<T>(path, { method: 'GET', params });
}

/**
 * POST request
 */
export async function post<T>(
  path: string,
  data?: unknown,
  options?: RequestOptions
): Promise<T> {
  return request<T>(path, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
    ...options,
  });
}

/**
 * PUT request
 */
export async function put<T>(
  path: string,
  data?: unknown,
  options?: RequestOptions
): Promise<T> {
  return request<T>(path, {
    method: 'PUT',
    body: data ? JSON.stringify(data) : undefined,
    ...options,
  });
}

/**
 * DELETE request
 */
export async function del<T>(
  path: string,
  options?: RequestOptions
): Promise<T> {
  return request<T>(path, {
    method: 'DELETE',
    ...options,
  });
}

/**
 * POST request with FormData (for file uploads)
 */
export async function postFormData<T>(
  path: string,
  formData: FormData,
  options?: Omit<RequestOptions, 'body'>
): Promise<T> {
  const url = buildUrl(path, options?.params);

  const response = await fetch(url, {
    method: 'POST',
    body: formData,
    ...options,
    // Don't set Content-Type header - browser will set it with boundary
    headers: options?.headers,
  });

  if (!response.ok) {
    let errorData: unknown;
    try {
      errorData = await response.json();
    } catch {
      errorData = await response.text();
    }
    throw new ApiError(
      `HTTP ${response.status}: ${response.statusText}`,
      response.status,
      errorData
    );
  }

  return response.json();
}

export const api = {
  get,
  post,
  put,
  delete: del,
  postFormData,
  API_URL,
};

export default api;

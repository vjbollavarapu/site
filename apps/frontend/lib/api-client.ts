// API client for Next.js API routes to proxy to Django backend
// This is used in Next.js API route handlers (server-side)

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface ApiRequestOptions extends RequestInit {
  authToken?: string;
}

/**
 * Make a request to the Django backend API
 * Used in Next.js API route handlers
 */
export async function apiRequest<T>(
  endpoint: string,
  options: ApiRequestOptions = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };

  // Add authentication if provided
  if (options.authToken) {
    headers['Authorization'] = `Basic ${options.authToken}`;
  }

  const config: RequestInit = {
    ...options,
    headers,
  };

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ 
        message: `HTTP error! status: ${response.status}` 
      }));
      throw new Error(error.message || error.detail || `HTTP error! status: ${response.status}`);
    }

    // Handle empty responses
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    
    return {} as T;
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

/**
 * Get authentication token from request headers or cookies
 * For Next.js API routes, we can get it from:
 * 1. Authorization header (Basic Auth)
 * 2. Cookie (Session-based auth)
 * 3. Client-side localStorage (passed via custom header)
 */
export function getAuthToken(request: Request): string | null {
  // Try Authorization header first
  const authHeader = request.headers.get('authorization');
  if (authHeader && authHeader.startsWith('Basic ')) {
    return authHeader.substring(6);
  }
  
  // Try X-Auth-Token header (for client-side token passing)
  const tokenHeader = request.headers.get('x-auth-token');
  if (tokenHeader) {
    return tokenHeader;
  }
  
  return null;
}

export { API_BASE_URL };


// Authentication utilities for frontend
// Simple auth system using localStorage and Basic Auth

const AUTH_TOKEN_KEY = 'auth_token';
const AUTH_USER_KEY = 'auth_user';

export interface AuthUser {
  username: string;
  email?: string;
  isAdmin?: boolean;
}

/**
 * Get authentication token from localStorage
 */
export function getAuthToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(AUTH_TOKEN_KEY);
}

/**
 * Set authentication token
 */
export function setAuthToken(token: string): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(AUTH_TOKEN_KEY, token);
}

/**
 * Get current user from localStorage
 */
export function getAuthUser(): AuthUser | null {
  if (typeof window === 'undefined') return null;
  const userStr = localStorage.getItem(AUTH_USER_KEY);
  if (!userStr) return null;
  try {
    return JSON.parse(userStr);
  } catch {
    return null;
  }
}

/**
 * Set current user
 */
export function setAuthUser(user: AuthUser): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return getAuthToken() !== null;
}

/**
 * Logout - clear all auth data
 */
export function logout(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(AUTH_TOKEN_KEY);
  localStorage.removeItem(AUTH_USER_KEY);
}

/**
 * Create Basic Auth token from username and password
 */
export function createBasicAuthToken(username: string, password: string): string {
  return btoa(`${username}:${password}`);
}

/**
 * Login with username and password
 * Returns true if successful, false otherwise
 */
export async function login(username: string, password: string): Promise<{ success: boolean; error?: string }> {
  try {
    const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const token = createBasicAuthToken(username, password);
    
    // Test authentication by calling a protected API endpoint
    // This validates the credentials with Django backend
    const apiResponse = await fetch(`${API_BASE_URL}/api/contacts/`, {
      method: 'GET',
      headers: {
        'Authorization': `Basic ${token}`,
        'Content-Type': 'application/json',
      },
      credentials: 'include', // Include cookies for session auth
    });

    if (apiResponse.ok || apiResponse.status === 200) {
      // Authentication successful
      setAuthToken(token);
      setAuthUser({
        username,
        isAdmin: true,
      });
      return { success: true };
    } else if (apiResponse.status === 401 || apiResponse.status === 403) {
      return { success: false, error: 'Invalid username or password. Please check your credentials.' };
    } else if (apiResponse.status === 503 || apiResponse.status === 0) {
      // Backend not running - allow login for development but warn user
      console.warn('Backend not accessible. Storing credentials for when backend is available.');
      setAuthToken(token);
      setAuthUser({
        username,
        isAdmin: true,
      });
      return { success: true };
    } else {
      // Other errors
      const errorData = await apiResponse.json().catch(() => ({}));
      const errorMessage = errorData.error || errorData.detail || `Login failed (${apiResponse.status})`;
      return { success: false, error: errorMessage };
    }
  } catch (error) {
    // Network error - backend might not be running
    // For development, allow login but store token
    const isNetworkError = error instanceof TypeError && error.message.includes('fetch');
    
    if (isNetworkError) {
      console.warn('Cannot reach backend. Storing credentials for when backend is available.');
      const token = createBasicAuthToken(username, password);
      setAuthToken(token);
      setAuthUser({
        username,
        isAdmin: true,
      });
      return { success: true };
    }
    
    console.error('Login error:', error);
    return { 
      success: false, 
      error: error instanceof Error ? error.message : 'Login failed. Please try again.' 
    };
  }
}


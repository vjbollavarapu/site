// API client for connecting to Django backend
// Base URL from environment variable or default to localhost:8000

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Helper function for API requests
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const config: RequestInit = {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  };

  // Add authentication if available
  // TODO: Implement authentication token retrieval
  // const token = getAuthToken();
  // if (token) {
  //   config.headers = {
  //     ...config.headers,
  //     'Authorization': `Basic ${token}`,
  //   };
  // }

  try {
    const response = await fetch(url, config);
    
    if (!response.ok) {
      const error = await response.json().catch(() => ({ message: 'An error occurred' }));
      throw new Error(error.message || `HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API request failed: ${endpoint}`, error);
    throw error;
  }
}

// Dashboard Stats
export async function fetchDashboardStats() {
  try {
    // Get auth token from localStorage
    const { getAuthToken } = await import('@/lib/auth');
    const authToken = getAuthToken();
    
    // Fetch from Next.js API route which proxies to Django backend
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };
    
    // Add auth token if available
    if (authToken) {
      headers['X-Auth-Token'] = authToken;
    }
    
    const response = await fetch('/api/dashboard/stats', {
      headers,
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return await response.json();
  } catch (error) {
    console.error('Failed to fetch dashboard stats:', error);
    // Return default stats on error
    return {
      contacts: {
        total: 0,
        new: 0,
        pending: 0,
        trend: 0,
      },
      waitlist: {
        total: 0,
        pending: 0,
        avgScore: 0,
        trend: 0,
      },
      leads: {
        total: 0,
        qualified: 0,
        conversionRate: 0,
        trend: 0,
      },
      newsletter: {
        total: 0,
        active: 0,
        unsubscribes: 0,
        growthRate: 0,
      },
    };
  }
}

// Chart Data
export async function fetchChartData() {
  // TODO: Replace with actual API endpoint when available
  try {
    // This would be the actual endpoint when backend provides it
    // return await apiRequest('/api/dashboard/charts/');
    
    // Fallback to mock data
    await new Promise((resolve) => setTimeout(resolve, 1000));
    
    const timeline = Array.from({ length: 30 }, (_, i) => {
      const date = new Date();
      date.setDate(date.getDate() - (29 - i));
      return {
        date: date.toLocaleDateString("en-US", { month: "short", day: "numeric" }),
        contacts: Math.floor(Math.random() * 100 + 400),
        waitlist: Math.floor(Math.random() * 50 + 100),
        leads: Math.floor(Math.random() * 80 + 150),
      };
    });

    return {
      timeline,
      statusDistribution: [
        { name: "Active", value: 6523 },
        { name: "Pending", value: 2845 },
        { name: "Inactive", value: 1876 },
        { name: "Archived", value: 1603 },
      ],
      leadSources: [
        { source: "Website", count: 2345 },
        { source: "Social", count: 1876 },
        { source: "Email", count: 987 },
        { source: "Referral", count: 424 },
      ],
      newsletterGrowth: [
        { month: "Jan", subscribers: 18234 },
        { month: "Feb", subscribers: 20145 },
        { month: "Mar", subscribers: 22567 },
        { month: "Apr", subscribers: 24123 },
        { month: "May", subscribers: 26234 },
        { month: "Jun", subscribers: 28456 },
      ],
    };
  } catch (error) {
    console.error('Failed to fetch chart data:', error);
    throw error;
  }
}

// Export API base URL for use in other files
export { API_BASE_URL };
export { apiRequest };

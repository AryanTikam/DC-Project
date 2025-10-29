import axios from 'axios';

/**
 * API service for communicating with the backend
 */
const API_BASE_URL = '/api';

// Create axios instance
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle token expiration
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

/**
 * Auth Service
 */
export const authService = {
  login: async (username, password) => {
    const response = await apiClient.post('/login', { username, password });
    return response.data;
  },

  register: async (userData) => {
    const response = await apiClient.post('/register', userData);
    return response.data;
  },

  getCurrentUser: () => {
    const userJson = localStorage.getItem('user');
    return userJson ? JSON.parse(userJson) : null;
  },

  logout: () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }
};

/**
 * Ride Service
 */
export const rideService = {
  bookCab: async (username, pickup, destination) => {
    const response = await apiClient.post('/book_cab', {
      username,
      pickup,
      destination
    });
    return response.data;
  },

  getRideStatus: async (rideId) => {
    const response = await apiClient.get(`/ride/${rideId}`);
    return response.data;
  },

  cancelRide: async (rideId) => {
    const response = await apiClient.post(`/ride/${rideId}/cancel`);
    return response.data;
  },

  updateRideStatus: async (rideId, status) => {
    const response = await apiClient.put(`/ride/${rideId}/status`, { status });
    return response.data;
  },

  getUserRides: async (username) => {
    const response = await apiClient.get(`/user/${username}/rides`);
    return response.data;
  },

  getActiveRides: async () => {
    const response = await apiClient.get('/rides/active');
    return response.data;
  }
};

/**
 * Driver Service
 */
export const driverService = {
  setAvailability: async (params) => {
    // Support both object parameter and individual parameters for backward compatibility
    let payload;
    if (typeof params === 'object' && params !== null && !Array.isArray(params)) {
      // If params is an object, use it directly (new style)
      payload = {
        is_available: params.available !== undefined ? params.available : params.is_available,
        location: params.current_location || params.location
      };
    } else {
      // Old style with separate parameters
      const [driverName, location, isAvailable] = arguments;
      payload = {
        driver_name: driverName,
        location,
        is_available: isAvailable
      };
    }
    
    const response = await apiClient.post('/driver/availability', payload);
    return response.data;
  },

  getAvailableCabs: async (location) => {
    const response = await apiClient.get(`/cabs?location=${location}`);
    return response.data;
  }
};

/**
 * System Service
 */
export const systemService = {
  getServerTime: async () => {
    const response = await apiClient.get('/time');
    return response.data;
  },

  syncTime: async () => {
    const clientTime = Date.now() / 1000; // seconds
    const response = await apiClient.post('/time/sync', { client_time: clientTime });
    return response.data;
  },

  getSystemStats: async () => {
    const response = await apiClient.get('/stats');
    return response.data;
  },

  getLoadBalancerStats: async () => {
    const response = await apiClient.get('/load_balancer/stats');
    return response.data;
  },

  getUserRides: async (username) => {
    const response = await apiClient.get(`/user/${username}/rides`);
    return response.data;
  },

  getAvailableRidesForDrivers: async () => {
    const response = await apiClient.get('/rides/available');
    return response.data;
  },

  acceptRide: async (rideId) => {
    const response = await apiClient.post(`/ride/${rideId}/accept`);
    return response.data;
  }
};

/**
 * Health Service
 */
export const healthService = {
  checkHealth: async () => {
    try {
      const response = await apiClient.get('/health');
      return response.data;
    } catch (error) {
      return { status: 'error', message: error.message };
    }
  }
};

export default {
  auth: authService,
  ride: rideService,
  driver: driverService,
  system: systemService,
  health: healthService
};
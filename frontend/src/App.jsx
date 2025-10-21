import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import BookRide from './pages/BookRide';
import { useAuth } from './context/AuthContext';
import { systemService } from './services/api';
import toast from 'react-hot-toast';

// Placeholder components for other pages
const Dashboard = () => (
  <div className="bg-white shadow rounded-lg p-6">
    <h1 className="text-2xl font-bold mb-4">Welcome to CabConnect</h1>
    <p className="text-gray-600 mb-4">A distributed cab booking system powered by RPC and advanced clock synchronization.</p>
    <div className="bg-blue-50 p-4 rounded-md">
      <p className="text-blue-700">Use the navigation to book rides, check ride status, or manage your driver availability.</p>
    </div>
  </div>
);

const MyRides = () => (
  <div className="bg-white shadow rounded-lg p-6">
    <h1 className="text-2xl font-bold mb-4">My Rides</h1>
    <p className="text-gray-600 mb-4">View your ride history and track current rides.</p>
    <div className="bg-yellow-50 p-4 rounded-md">
      <p className="text-yellow-700">This page is under construction. Please check back later.</p>
    </div>
  </div>
);

const AvailableRides = () => (
  <div className="bg-white shadow rounded-lg p-6">
    <h1 className="text-2xl font-bold mb-4">Available Rides</h1>
    <p className="text-gray-600 mb-4">View ride requests that need a driver.</p>
    <div className="bg-yellow-50 p-4 rounded-md">
      <p className="text-yellow-700">This page is under construction. Please check back later.</p>
    </div>
  </div>
);

const SetAvailability = () => (
  <div className="bg-white shadow rounded-lg p-6">
    <h1 className="text-2xl font-bold mb-4">Set Availability</h1>
    <p className="text-gray-600 mb-4">Update your location and availability status.</p>
    <div className="bg-yellow-50 p-4 rounded-md">
      <p className="text-yellow-700">This page is under construction. Please check back later.</p>
    </div>
  </div>
);

const SystemStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        const response = await systemService.getSystemStats();
        if (response.success) {
          setStats(response.stats);
        } else {
          setError('Failed to load system statistics');
        }
      } catch (err) {
        setError('An error occurred while fetching system statistics');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
    // Poll for stats every 30 seconds
    const interval = setInterval(fetchStats, 30000);
    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold mb-4">System Statistics</h1>
        <div className="flex justify-center py-8">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white shadow rounded-lg p-6">
        <h1 className="text-2xl font-bold mb-4">System Statistics</h1>
        <div className="bg-red-50 p-4 rounded-md">
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h1 className="text-2xl font-bold mb-4">System Statistics</h1>
      {stats ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-gray-50 p-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Server Information</h2>
            <p><span className="font-medium">Server ID:</span> {stats.server_id}</p>
            <p><span className="font-medium">Leader:</span> {stats.is_leader ? 'Yes' : 'No'}</p>
            <p><span className="font-medium">System Time:</span> {stats.system_time}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Clock Synchronization</h2>
            <p><span className="font-medium">Lamport Clock:</span> {stats.lamport_clock}</p>
            <p><span className="font-medium">Vector Clock:</span> {JSON.stringify(stats.vector_clock)}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Users</h2>
            <p><span className="font-medium">Total Users:</span> {stats.users.total}</p>
            <p><span className="font-medium">Riders:</span> {stats.users.riders}</p>
            <p><span className="font-medium">Drivers:</span> {stats.users.drivers}</p>
            <p><span className="font-medium">Available Drivers:</span> {stats.drivers.available}</p>
          </div>
          <div className="bg-gray-50 p-4 rounded-lg">
            <h2 className="text-lg font-semibold mb-2">Rides</h2>
            <p><span className="font-medium">Total Rides:</span> {stats.rides.total}</p>
            <p><span className="font-medium">Active:</span> {stats.rides.active}</p>
            <p><span className="font-medium">Completed:</span> {stats.rides.completed}</p>
            <p><span className="font-medium">Cancelled:</span> {stats.rides.cancelled}</p>
          </div>
        </div>
      ) : (
        <div className="bg-yellow-50 p-4 rounded-md">
          <p className="text-yellow-700">No statistics available.</p>
        </div>
      )}
    </div>
  );
};

// Protected Route Component
const ProtectedRoute = ({ element }) => {
  const { currentUser, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return currentUser ? element : <Navigate to="/login" />;
};

// Specific route that only drivers can access
const DriverRoute = ({ element }) => {
  const { currentUser, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!currentUser) {
    return <Navigate to="/login" />;
  }

  if (currentUser.userType !== 'DRIVER') {
    toast.error('This page is only accessible to drivers');
    return <Navigate to="/" />;
  }

  return element;
};

// Specific route that only riders can access
const RiderRoute = ({ element }) => {
  const { currentUser, loading } = useAuth();

  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!currentUser) {
    return <Navigate to="/login" />;
  }

  if (currentUser.userType !== 'RIDER') {
    toast.error('This page is only accessible to riders');
    return <Navigate to="/" />;
  }

  return element;
};

function App() {
  const { currentUser } = useAuth();

  // Sync time with server on load
  useEffect(() => {
    const syncTime = async () => {
      try {
        await systemService.syncTime();
        console.log('Time synchronized with server');
      } catch (error) {
        console.error('Failed to sync time with server:', error);
      }
    };

    syncTime();
    // Sync every 5 minutes
    const interval = setInterval(syncTime, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<ProtectedRoute element={<Dashboard />} />} />
        <Route path="book-ride" element={<RiderRoute element={<BookRide />} />} />
        <Route path="my-rides" element={<ProtectedRoute element={<MyRides />} />} />
        <Route path="available-rides" element={<DriverRoute element={<AvailableRides />} />} />
        <Route path="availability" element={<DriverRoute element={<SetAvailability />} />} />
        <Route path="stats" element={<ProtectedRoute element={<SystemStats />} />} />
        <Route path="login" element={currentUser ? <Navigate to="/" /> : <Login />} />
        <Route path="register" element={currentUser ? <Navigate to="/" /> : <Register />} />
        <Route path="*" element={<Navigate to="/" />} />
      </Route>
    </Routes>
  );
}

export default App;
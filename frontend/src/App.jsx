import { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Login from './pages/Login';
import Register from './pages/Register';
import BookRide from './pages/BookRide';
import { useAuth } from './context/AuthContext';
import { systemService, driverService, rideService } from './services/api';
import toast from 'react-hot-toast';

// Dashboard Component
const Dashboard = () => {
  const { currentUser } = useAuth();
  
  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl shadow-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">Welcome back, {currentUser?.name}! 👋</h1>
            <p className="text-blue-100 text-lg">Ready to embark on your next journey?</p>
          </div>
          <div className="hidden md:block">
            <svg className="w-32 h-32 opacity-20" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"/>
              <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1v-5a1 1 0 00-.293-.707l-2-2A1 1 0 0015 7h-1z"/>
            </svg>
          </div>
        </div>
      </div>

      {/* Quick Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500 hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Account Type</p>
              <p className="text-2xl font-bold text-gray-800 mt-1">{currentUser?.userType}</p>
            </div>
            <div className="bg-blue-100 rounded-full p-3">
              <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500 hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Rating</p>
              <p className="text-2xl font-bold text-gray-800 mt-1">{currentUser?.rating?.toFixed(1) || '5.0'} ⭐</p>
            </div>
            <div className="bg-green-100 rounded-full p-3">
              <svg className="w-8 h-8 text-green-600" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500 hover:shadow-xl transition-shadow">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-gray-500 text-sm font-medium">Member Since</p>
              <p className="text-2xl font-bold text-gray-800 mt-1">2025</p>
            </div>
            <div className="bg-purple-100 rounded-full p-3">
              <svg className="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">🚀 What You Can Do</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {currentUser?.userType === 'RIDER' ? (
            <>
              <div className="flex items-start space-x-4 p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg">
                <div className="bg-blue-500 rounded-full p-2 mt-1">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">Book Rides</h3>
                  <p className="text-gray-600 text-sm">Find and book cabs near you instantly</p>
                </div>
              </div>
              <div className="flex items-start space-x-4 p-4 bg-gradient-to-r from-green-50 to-green-100 rounded-lg">
                <div className="bg-green-500 rounded-full p-2 mt-1">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">Track Rides</h3>
                  <p className="text-gray-600 text-sm">Monitor your current and past rides</p>
                </div>
              </div>
            </>
          ) : (
            <>
              <div className="flex items-start space-x-4 p-4 bg-gradient-to-r from-purple-50 to-purple-100 rounded-lg">
                <div className="bg-purple-500 rounded-full p-2 mt-1">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">Accept Rides</h3>
                  <p className="text-gray-600 text-sm">View and accept ride requests</p>
                </div>
              </div>
              <div className="flex items-start space-x-4 p-4 bg-gradient-to-r from-orange-50 to-orange-100 rounded-lg">
                <div className="bg-orange-500 rounded-full p-2 mt-1">
                  <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold text-gray-800">Set Availability</h3>
                  <p className="text-gray-600 text-sm">Update your location and status</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* System Info */}
      <div className="bg-gradient-to-r from-indigo-500 to-purple-600 rounded-xl shadow-lg p-6 text-white">
        <h2 className="text-xl font-bold mb-3">🔧 Powered by Distributed Systems</h2>
        <p className="text-indigo-100">
          This platform uses advanced technologies including RPC for communication, 
          Lamport & Vector clocks for synchronization, and distributed load balancing 
          for optimal performance.
        </p>
      </div>
    </div>
  );
};

const MyRides = () => {
  const { currentUser } = useAuth();
  const [rides, setRides] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [cancellingRide, setCancellingRide] = useState(null);
  const [showCancelModal, setShowCancelModal] = useState(false);
  const [selectedRide, setSelectedRide] = useState(null);

  useEffect(() => {
    fetchRides();
  }, [currentUser]);

  const fetchRides = async () => {
    try {
      setLoading(true);
      const response = await systemService.getUserRides(currentUser.username);
      if (response.success) {
        setRides(response.rides);
      } else {
        setError('Failed to load rides');
      }
    } catch (err) {
      setError('An error occurred while fetching rides');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCancelClick = (ride) => {
    setSelectedRide(ride);
    setShowCancelModal(true);
  };

  const handleCancelConfirm = async () => {
    if (!selectedRide) return;
    
    setCancellingRide(selectedRide.ride_id);
    try {
      const response = await rideService.cancelRide(selectedRide.ride_id);
      if (response.success) {
        toast.success(
          `Ride cancelled. Rating penalty: -${response.rating_penalty.toFixed(1)} ⭐`,
          { duration: 6000 }
        );
        fetchRides(); // Refresh the list
      } else {
        toast.error(response.message || 'Failed to cancel ride');
      }
    } catch (err) {
      toast.error('Failed to cancel ride');
      console.error(err);
    } finally {
      setCancellingRide(null);
      setShowCancelModal(false);
      setSelectedRide(null);
    }
  };

  const getRatingPenalty = (status) => {
    if (status === 'REQUESTED') return 0.1;
    if (status === 'ACCEPTED') return 0.3;
    if (status === 'IN_PROGRESS') return 0.5;
    return 0;
  };

  const canCancelRide = (ride) => {
    return ride.status !== 'COMPLETED' && ride.status !== 'CANCELLED';
  };

  const getStatusColor = (status) => {
    const colors = {
      'REQUESTED': 'bg-yellow-100 text-yellow-800 border-yellow-300',
      'ACCEPTED': 'bg-blue-100 text-blue-800 border-blue-300',
      'IN_PROGRESS': 'bg-purple-100 text-purple-800 border-purple-300',
      'COMPLETED': 'bg-green-100 text-green-800 border-green-300',
      'CANCELLED': 'bg-red-100 text-red-800 border-red-300'
    };
    return colors[status] || 'bg-gray-100 text-gray-800 border-gray-300';
  };

  const getLocationIcon = (location) => {
    const icons = {
      'Downtown': '🏙️', 'Airport': '✈️', 'Mall': '🛍️',
      'University': '🎓', 'Tech Park': '💼', 'Hospital': '🏥',
      'Stadium': '🏟️', 'Railway Station': '🚉', 'Bus Terminal': '🚌', 'Beach': '🏖️'
    };
    return icons[location] || '📍';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">🚗 My Rides</h1>
        <div className="flex justify-center py-16">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-600"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="h-8 w-8 bg-blue-100 rounded-full"></div>
            </div>
          </div>
        </div>
        <p className="text-center text-gray-500 mt-4">Loading your rides...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">🚗 My Rides</h1>
        <div className="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 p-6 rounded-xl">
          <div className="flex items-start space-x-3">
            <svg className="w-6 h-6 text-red-600 mt-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
            </svg>
            <div>
              <h3 className="font-semibold text-red-800 mb-1">Error Loading Rides</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 rounded-2xl shadow-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">🚗 My Rides</h1>
            <p className="text-blue-100 text-lg">Track your ride history and status</p>
          </div>
          <div className="hidden md:block">
            <div className="bg-white bg-opacity-20 rounded-full p-4">
              <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9 2a1 1 0 000 2h2a1 1 0 100-2H9z"/>
                <path fillRule="evenodd" d="M4 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v11a2 2 0 01-2 2H6a2 2 0 01-2-2V5zm3 4a1 1 0 000 2h.01a1 1 0 100-2H7zm3 0a1 1 0 000 2h3a1 1 0 100-2h-3zm-3 4a1 1 0 100 2h.01a1 1 0 100-2H7zm3 0a1 1 0 100 2h3a1 1 0 100-2h-3z" clipRule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Rides List */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        {rides.length === 0 ? (
          <div className="text-center py-12">
            <div className="inline-block bg-gray-100 rounded-full p-6 mb-4">
              <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No Rides Yet</h3>
            <p className="text-gray-600">
              {currentUser?.userType === 'RIDER' 
                ? 'Book your first ride to get started!' 
                : 'Accept ride requests to see them here.'}
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-gray-800 mb-4">
              Total Rides: {rides.length}
            </h2>
            {rides.map((ride) => (
              <div key={ride.ride_id} className="bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl p-6 border-2 border-gray-200 hover:border-blue-400 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="bg-blue-500 rounded-full w-12 h-12 flex items-center justify-center text-white font-bold text-lg">
                      🚕
                    </div>
                    <div>
                      <p className="font-semibold text-gray-800">Ride #{ride.ride_id.slice(0, 8)}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(ride.booking_time * 1000).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <span className={`px-4 py-2 rounded-full text-sm font-semibold border-2 ${getStatusColor(ride.status)}`}>
                    {ride.status}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="bg-white rounded-lg p-4 border border-gray-200">
                    <div className="flex items-start space-x-3">
                      <div className="flex flex-col items-center">
                        <div className="bg-green-500 rounded-full w-3 h-3"></div>
                        <div className="w-0.5 h-8 bg-gray-300"></div>
                        <div className="bg-red-500 rounded-full w-3 h-3"></div>
                      </div>
                      <div className="flex-1">
                        <div className="mb-2">
                          <p className="text-xs text-gray-500 font-medium">PICKUP</p>
                          <p className="font-semibold text-gray-800">
                            {getLocationIcon(ride.pickup)} {ride.pickup}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 font-medium">DESTINATION</p>
                          <p className="font-semibold text-gray-800">
                            {getLocationIcon(ride.destination)} {ride.destination}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg p-4 border border-gray-200">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <p className="text-xs text-gray-500 font-medium">FARE</p>
                        <p className="text-lg font-bold text-green-600">₹{ride.fare}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 font-medium">DISTANCE</p>
                        <p className="text-lg font-bold text-blue-600">{ride.estimated_distance} km</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 font-medium">RIDER</p>
                        <p className="text-sm font-semibold text-gray-800">{ride.rider_name}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 font-medium">DRIVER</p>
                        <p className="text-sm font-semibold text-gray-800">{ride.driver_name || 'Pending'}</p>
                      </div>
                    </div>
                  </div>
                </div>

                {canCancelRide(ride) && (
                  <button
                    onClick={() => handleCancelClick(ride)}
                    disabled={cancellingRide === ride.ride_id}
                    className="w-full mt-4 py-3 bg-gradient-to-r from-red-500 to-pink-600 text-white font-bold rounded-xl shadow-lg hover:from-red-600 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {cancellingRide === ride.ride_id ? (
                      <span className="flex items-center justify-center">
                        <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Cancelling...
                      </span>
                    ) : (
                      <span className="flex items-center justify-center">
                        <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                        </svg>
                        Cancel Ride
                      </span>
                    )}
                  </button>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Cancel Confirmation Modal */}
      {showCancelModal && selectedRide && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 animate-fade-in">
            <div className="text-center mb-6">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100 mb-4">
                <svg className="h-10 w-10 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Cancel Ride?</h3>
              <p className="text-gray-600 mb-4">
                Are you sure you want to cancel this ride?
              </p>
            </div>

            <div className="bg-red-50 border-2 border-red-200 rounded-xl p-4 mb-6">
              <div className="flex items-start space-x-3">
                <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                </svg>
                <div className="flex-1">
                  <h4 className="font-bold text-red-800 mb-2">Warning: Rating Penalty</h4>
                  <p className="text-sm text-red-700 mb-2">
                    Cancelling this ride will reduce your rating by <strong>{getRatingPenalty(selectedRide.status).toFixed(1)} stars</strong>.
                  </p>
                  <ul className="text-xs text-red-600 space-y-1">
                    <li>• Before assignment: -0.1 ⭐</li>
                    <li>• After driver accepts: -0.3 ⭐</li>
                    <li>• During ride: -0.5 ⭐</li>
                  </ul>
                </div>
              </div>
            </div>

            <div className="bg-gray-50 rounded-xl p-4 mb-6">
              <p className="text-sm text-gray-600 mb-2"><strong>Ride Details:</strong></p>
              <p className="text-sm text-gray-800">From: {selectedRide.pickup}</p>
              <p className="text-sm text-gray-800">To: {selectedRide.destination}</p>
              <p className="text-sm text-gray-800">Status: <span className="font-semibold">{selectedRide.status}</span></p>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowCancelModal(false);
                  setSelectedRide(null);
                }}
                className="flex-1 px-4 py-3 bg-gray-200 text-gray-800 rounded-xl font-semibold hover:bg-gray-300 transition-colors"
              >
                Keep Ride
              </button>
              <button
                onClick={handleCancelConfirm}
                disabled={cancellingRide}
                className="flex-1 px-4 py-3 bg-gradient-to-r from-red-500 to-pink-600 text-white rounded-xl font-semibold hover:from-red-600 hover:to-pink-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {cancellingRide ? 'Cancelling...' : 'Yes, Cancel'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

const AvailableRides = () => {
  const [rides, setRides] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [accepting, setAccepting] = useState(null);

  useEffect(() => {
    fetchAvailableRides();
    // Refresh every 10 seconds
    const interval = setInterval(fetchAvailableRides, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchAvailableRides = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await systemService.getAvailableRidesForDrivers();
      if (response.success) {
        setRides(response.rides);
      } else {
        setError('Failed to load available rides');
      }
    } catch (err) {
      setError('An error occurred while fetching rides');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAcceptRide = async (rideId) => {
    setAccepting(rideId);
    try {
      const response = await systemService.acceptRide(rideId);
      if (response.success) {
        toast.success('🎉 Ride accepted successfully!');
        fetchAvailableRides(); // Refresh the list
      } else {
        toast.error(response.message || 'Failed to accept ride');
      }
    } catch (err) {
      toast.error('Failed to accept ride');
      console.error(err);
    } finally {
      setAccepting(null);
    }
  };

  const getLocationIcon = (location) => {
    const icons = {
      'Downtown': '🏙️', 'Airport': '✈️', 'Mall': '🛍️',
      'University': '🎓', 'Tech Park': '💼', 'Hospital': '🏥',
      'Stadium': '🏟️', 'Railway Station': '🚉', 'Bus Terminal': '🚌', 'Beach': '🏖️'
    };
    return icons[location] || '📍';
  };

  if (loading && rides.length === 0) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">🚖 Available Rides</h1>
        <div className="flex justify-center py-16">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-green-600"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="h-8 w-8 bg-green-100 rounded-full"></div>
            </div>
          </div>
        </div>
        <p className="text-center text-gray-500 mt-4">Loading available rides...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">🚖 Available Rides</h1>
        <div className="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 p-6 rounded-xl">
          <div className="flex items-start space-x-3">
            <svg className="w-6 h-6 text-red-600 mt-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
            </svg>
            <div>
              <h3 className="font-semibold text-red-800 mb-1">Error Loading Rides</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 via-emerald-600 to-teal-600 rounded-2xl shadow-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">🚖 Available Rides</h1>
            <p className="text-green-100 text-lg">Accept ride requests and start earning</p>
          </div>
          <div className="hidden md:block">
            <div className="bg-white bg-opacity-20 rounded-full p-4">
              <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z" clipRule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Bar */}
      <div className="bg-white rounded-xl shadow-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm text-gray-500 font-medium">AVAILABLE REQUESTS</p>
            <p className="text-3xl font-bold text-gray-800">{rides.length}</p>
          </div>
          <button
            onClick={fetchAvailableRides}
            className="px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* Rides List */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        {rides.length === 0 ? (
          <div className="text-center py-12">
            <div className="inline-block bg-gray-100 rounded-full p-6 mb-4">
              <svg className="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-gray-800 mb-2">No Available Rides</h3>
            <p className="text-gray-600">Check back in a moment for new ride requests!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {rides.map((ride) => (
              <div key={ride.ride_id} className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-xl p-6 border-2 border-green-200 hover:border-green-400 transition-all">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <div className="bg-green-500 rounded-full w-12 h-12 flex items-center justify-center text-white font-bold text-lg">
                      👤
                    </div>
                    <div>
                      <p className="font-semibold text-gray-800">{ride.rider_name}</p>
                      <p className="text-sm text-gray-500">
                        {new Date(ride.booking_time * 1000).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <span className="px-4 py-2 rounded-full text-sm font-semibold bg-yellow-100 text-yellow-800 border-2 border-yellow-300">
                    {ride.status}
                  </span>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="bg-white rounded-lg p-4 border border-gray-200">
                    <div className="flex items-start space-x-3">
                      <div className="flex flex-col items-center">
                        <div className="bg-green-500 rounded-full w-3 h-3"></div>
                        <div className="w-0.5 h-8 bg-gray-300"></div>
                        <div className="bg-red-500 rounded-full w-3 h-3"></div>
                      </div>
                      <div className="flex-1">
                        <div className="mb-2">
                          <p className="text-xs text-gray-500 font-medium">PICKUP</p>
                          <p className="font-semibold text-gray-800">
                            {getLocationIcon(ride.pickup)} {ride.pickup}
                          </p>
                        </div>
                        <div>
                          <p className="text-xs text-gray-500 font-medium">DESTINATION</p>
                          <p className="font-semibold text-gray-800">
                            {getLocationIcon(ride.destination)} {ride.destination}
                          </p>
                        </div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-white rounded-lg p-4 border border-gray-200">
                    <div className="grid grid-cols-2 gap-3">
                      <div>
                        <p className="text-xs text-gray-500 font-medium">FARE</p>
                        <p className="text-lg font-bold text-green-600">₹{ride.fare}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 font-medium">DISTANCE</p>
                        <p className="text-lg font-bold text-blue-600">{ride.estimated_distance} km</p>
                      </div>
                      <div className="col-span-2">
                        <p className="text-xs text-gray-500 font-medium">ESTIMATED TIME</p>
                        <p className="text-lg font-bold text-purple-600">{ride.estimated_time} min</p>
                      </div>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleAcceptRide(ride.ride_id)}
                  disabled={accepting === ride.ride_id}
                  className={`w-full py-3 bg-gradient-to-r from-green-600 to-emerald-600 text-white font-bold rounded-xl shadow-lg hover:from-green-700 hover:to-emerald-700 transition-all ${
                    accepting === ride.ride_id ? 'opacity-70 cursor-not-allowed' : ''
                  }`}
                >
                  {accepting === ride.ride_id ? (
                    <span className="flex items-center justify-center">
                      <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                      </svg>
                      Accepting...
                    </span>
                  ) : (
                    <span className="flex items-center justify-center">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      Accept This Ride
                    </span>
                  )}
                </button>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

const SetAvailability = () => {
  const { currentUser } = useAuth();
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState('available');
  const [location, setLocation] = useState('Downtown');
  const [message, setMessage] = useState(null);

  const locations = [
    '🏙️ Downtown', '✈️ Airport', '🛍️ Mall', '🎓 University',
    '💼 Tech Park', '🏥 Hospital', '🏟️ Stadium', '🚉 Railway Station',
    '🚌 Bus Terminal', '🏖️ Beach'
  ];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMessage(null);
    
    try {
      const cleanLocation = location.replace(/^[^\s]+\s/, ''); // Remove emoji
      const response = await driverService.setAvailability({
        driver_name: currentUser.username,
        available: status === 'available',
        current_location: cleanLocation
      });

      if (response.success) {
        setMessage({ type: 'success', text: '✅ Availability updated successfully!' });
        toast.success('Availability updated!');
      } else {
        setMessage({ type: 'error', text: response.message || 'Failed to update availability' });
        toast.error('Failed to update availability');
      }
    } catch (err) {
      setMessage({ type: 'error', text: 'An error occurred while updating availability' });
      toast.error('An error occurred');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 rounded-2xl shadow-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">⚙️ Set Availability</h1>
            <p className="text-purple-100 text-lg">Update your status and current location</p>
          </div>
          <div className="hidden md:block">
            <div className="bg-white bg-opacity-20 rounded-full p-4">
              <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      {/* Form Card */}
      <div className="bg-white rounded-xl shadow-lg p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Status Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              📍 AVAILABILITY STATUS
            </label>
            <div className="grid grid-cols-2 gap-4">
              <button
                type="button"
                onClick={() => setStatus('available')}
                className={`p-6 rounded-xl border-2 transition-all ${
                  status === 'available'
                    ? 'border-green-500 bg-gradient-to-br from-green-50 to-emerald-50 shadow-lg scale-105'
                    : 'border-gray-200 bg-gray-50 hover:border-green-300'
                }`}
              >
                <div className="flex flex-col items-center space-y-3">
                  <div className={`rounded-full p-3 ${
                    status === 'available' ? 'bg-green-500' : 'bg-gray-300'
                  }`}>
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div className="text-center">
                    <p className={`font-bold text-lg ${
                      status === 'available' ? 'text-green-700' : 'text-gray-600'
                    }`}>
                      Available
                    </p>
                    <p className="text-sm text-gray-500 mt-1">Ready to accept rides</p>
                  </div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setStatus('busy')}
                className={`p-6 rounded-xl border-2 transition-all ${
                  status === 'busy'
                    ? 'border-red-500 bg-gradient-to-br from-red-50 to-pink-50 shadow-lg scale-105'
                    : 'border-gray-200 bg-gray-50 hover:border-red-300'
                }`}
              >
                <div className="flex flex-col items-center space-y-3">
                  <div className={`rounded-full p-3 ${
                    status === 'busy' ? 'bg-red-500' : 'bg-gray-300'
                  }`}>
                    <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </div>
                  <div className="text-center">
                    <p className={`font-bold text-lg ${
                      status === 'busy' ? 'text-red-700' : 'text-gray-600'
                    }`}>
                      Busy / Offline
                    </p>
                    <p className="text-sm text-gray-500 mt-1">Not accepting rides</p>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* Location Selection */}
          <div>
            <label className="block text-sm font-semibold text-gray-700 mb-3">
              🗺️ CURRENT LOCATION
            </label>
            <select
              value={location}
              onChange={(e) => setLocation(e.target.value)}
              className="w-full p-4 border-2 border-gray-300 rounded-xl focus:border-purple-500 focus:outline-none bg-gradient-to-r from-white to-gray-50 text-gray-800 font-medium text-lg transition-colors"
            >
              {locations.map((loc) => (
                <option key={loc} value={loc}>
                  {loc}
                </option>
              ))}
            </select>
          </div>

          {/* Info Card */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border-2 border-blue-200 rounded-xl p-5">
            <div className="flex items-start space-x-3">
              <svg className="w-6 h-6 text-blue-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
              </svg>
              <div>
                <h4 className="font-semibold text-blue-800 mb-1">Quick Tip</h4>
                <p className="text-sm text-blue-700">
                  Keep your location updated to receive ride requests from nearby passengers. 
                  Set yourself as "Busy/Offline" when you're taking a break.
                </p>
              </div>
            </div>
          </div>

          {/* Message Display */}
          {message && (
            <div className={`rounded-xl p-5 border-2 ${
              message.type === 'success'
                ? 'bg-gradient-to-r from-green-50 to-emerald-50 border-green-200'
                : 'bg-gradient-to-r from-red-50 to-pink-50 border-red-200'
            }`}>
              <div className="flex items-start space-x-3">
                {message.type === 'success' ? (
                  <svg className="w-6 h-6 text-green-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
                  </svg>
                ) : (
                  <svg className="w-6 h-6 text-red-600 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
                  </svg>
                )}
                <p className={`font-medium ${
                  message.type === 'success' ? 'text-green-800' : 'text-red-800'
                }`}>
                  {message.text}
                </p>
              </div>
            </div>
          )}

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading}
            className={`w-full py-4 bg-gradient-to-r from-purple-600 via-violet-600 to-indigo-600 text-white font-bold rounded-xl shadow-lg hover:from-purple-700 hover:via-violet-700 hover:to-indigo-700 transition-all text-lg ${
              loading ? 'opacity-70 cursor-not-allowed' : 'transform hover:scale-[1.02]'
            }`}
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-white" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Updating...
              </span>
            ) : (
              <span className="flex items-center justify-center">
                <svg className="w-6 h-6 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                </svg>
                Update Availability
              </span>
            )}
          </button>
        </form>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-gradient-to-br from-green-500 to-emerald-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-green-100 text-sm font-medium mb-1">CURRENT STATUS</p>
              <p className="text-2xl font-bold">
                {status === 'available' ? '✅ Available' : '🚫 Offline'}
              </p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-full p-3">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-blue-100 text-sm font-medium mb-1">LOCATION</p>
              <p className="text-2xl font-bold">{location}</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-full p-3">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z" clipRule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>

        <div className="bg-gradient-to-br from-purple-500 to-pink-600 rounded-xl p-6 text-white shadow-lg">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-purple-100 text-sm font-medium mb-1">DRIVER</p>
              <p className="text-2xl font-bold">{currentUser?.username || 'Driver'}</p>
            </div>
            <div className="bg-white bg-opacity-20 rounded-full p-3">
              <svg className="w-8 h-8" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd"/>
              </svg>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const SystemStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        setError(null);
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
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">📊 System Statistics</h1>
        <div className="flex justify-center py-16">
          <div className="relative">
            <div className="animate-spin rounded-full h-16 w-16 border-t-4 border-b-4 border-blue-600"></div>
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="h-8 w-8 bg-blue-100 rounded-full"></div>
            </div>
          </div>
        </div>
        <p className="text-center text-gray-500 mt-4">Loading statistics...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-xl shadow-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-gray-800">📊 System Statistics</h1>
        <div className="bg-gradient-to-r from-red-50 to-red-100 border border-red-200 p-6 rounded-xl">
          <div className="flex items-start space-x-3">
            <svg className="w-6 h-6 text-red-600 mt-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd"/>
            </svg>
            <div>
              <h3 className="font-semibold text-red-800 mb-1">Error Loading Statistics</h3>
              <p className="text-red-700">{error}</p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-cyan-500 via-blue-500 to-indigo-600 rounded-2xl shadow-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">📊 System Statistics</h1>
            <p className="text-blue-100 text-lg">Real-time insights into the platform</p>
          </div>
          <div className="hidden md:block">
            <div className="bg-white bg-opacity-20 rounded-full p-4">
              <svg className="w-16 h-16" fill="currentColor" viewBox="0 0 20 20">
                <path d="M2 11a1 1 0 011-1h2a1 1 0 011 1v5a1 1 0 01-1 1H3a1 1 0 01-1-1v-5zM8 7a1 1 0 011-1h2a1 1 0 011 1v9a1 1 0 01-1 1H9a1 1 0 01-1-1V7zM14 4a1 1 0 011-1h2a1 1 0 011 1v12a1 1 0 01-1 1h-2a1 1 0 01-1-1V4z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      {stats ? (
        <>
          {/* Server Information */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <span className="bg-blue-100 rounded-full p-2 mr-3">
                <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                </svg>
              </span>
              Server Information
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200">
                <p className="text-sm text-blue-600 font-medium mb-1">Server ID</p>
                <p className="text-xl font-bold text-blue-900">{stats.server_id}</p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200">
                <p className="text-sm text-green-600 font-medium mb-1">Leader Status</p>
                <p className="text-xl font-bold text-green-900">{stats.is_leader ? '✅ Leader' : '⏸️ Follower'}</p>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200">
                <p className="text-sm text-purple-600 font-medium mb-1">System Time</p>
                <p className="text-xl font-bold text-purple-900">{stats.system_time}</p>
              </div>
            </div>
          </div>

          {/* Clock Synchronization */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <span className="bg-indigo-100 rounded-full p-2 mr-3">
                <svg className="w-6 h-6 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </span>
              Clock Synchronization
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 p-4 rounded-lg border border-indigo-200">
                <p className="text-sm text-indigo-600 font-medium mb-1">Lamport Clock</p>
                <p className="text-3xl font-bold text-indigo-900">{stats.lamport_clock}</p>
              </div>
              <div className="bg-gradient-to-br from-pink-50 to-pink-100 p-4 rounded-lg border border-pink-200">
                <p className="text-sm text-pink-600 font-medium mb-1">Vector Clock</p>
                <p className="text-lg font-mono text-pink-900">{JSON.stringify(stats.vector_clock)}</p>
              </div>
            </div>
          </div>

          {/* Users Statistics */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <span className="bg-green-100 rounded-full p-2 mr-3">
                <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
                </svg>
              </span>
              User Statistics
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200 text-center">
                <p className="text-4xl font-bold text-blue-900 mb-1">{stats.users.total}</p>
                <p className="text-sm text-blue-600 font-medium">Total Users</p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200 text-center">
                <p className="text-4xl font-bold text-green-900 mb-1">{stats.users.riders}</p>
                <p className="text-sm text-green-600 font-medium">Riders</p>
              </div>
              <div className="bg-gradient-to-br from-purple-50 to-purple-100 p-4 rounded-lg border border-purple-200 text-center">
                <p className="text-4xl font-bold text-purple-900 mb-1">{stats.users.drivers}</p>
                <p className="text-sm text-purple-600 font-medium">Drivers</p>
              </div>
              <div className="bg-gradient-to-br from-yellow-50 to-yellow-100 p-4 rounded-lg border border-yellow-200 text-center">
                <p className="text-4xl font-bold text-yellow-900 mb-1">{stats.drivers.available}</p>
                <p className="text-sm text-yellow-600 font-medium">Available Now</p>
              </div>
            </div>
          </div>

          {/* Rides Statistics */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-bold text-gray-800 mb-4 flex items-center">
              <span className="bg-orange-100 rounded-full p-2 mr-3">
                <svg className="w-6 h-6 text-orange-600" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"/>
                  <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1v-5a1 1 0 00-.293-.707l-2-2A1 1 0 0015 7h-1z"/>
                </svg>
              </span>
              Ride Statistics
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-gradient-to-br from-slate-50 to-slate-100 p-4 rounded-lg border border-slate-200 text-center">
                <p className="text-4xl font-bold text-slate-900 mb-1">{stats.rides.total}</p>
                <p className="text-sm text-slate-600 font-medium">Total Rides</p>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 p-4 rounded-lg border border-blue-200 text-center">
                <p className="text-4xl font-bold text-blue-900 mb-1">{stats.rides.active}</p>
                <p className="text-sm text-blue-600 font-medium">Active</p>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 p-4 rounded-lg border border-green-200 text-center">
                <p className="text-4xl font-bold text-green-900 mb-1">{stats.rides.completed}</p>
                <p className="text-sm text-green-600 font-medium">Completed</p>
              </div>
              <div className="bg-gradient-to-br from-red-50 to-red-100 p-4 rounded-lg border border-red-200 text-center">
                <p className="text-4xl font-bold text-red-900 mb-1">{stats.rides.cancelled}</p>
                <p className="text-sm text-red-600 font-medium">Cancelled</p>
              </div>
            </div>
          </div>

          {/* Last Updated */}
          <div className="bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl p-4 text-center border border-gray-200">
            <p className="text-gray-600 text-sm">
              Last updated: {new Date(stats.timestamp * 1000).toLocaleString()} • Auto-refreshing every 30 seconds
            </p>
          </div>
        </>
      ) : (
        <div className="bg-white rounded-xl shadow-lg p-8">
          <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border border-yellow-200 p-6 rounded-xl">
            <div className="flex items-start space-x-3">
              <svg className="w-6 h-6 text-yellow-600 mt-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
              </svg>
              <div>
                <h3 className="font-semibold text-yellow-800 mb-1">No Statistics Available</h3>
                <p className="text-yellow-700">Unable to retrieve system statistics at this time.</p>
              </div>
            </div>
          </div>
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
  const [shouldRedirect, setShouldRedirect] = useState(false);

  useEffect(() => {
    if (!loading && currentUser && currentUser.userType !== 'DRIVER') {
      toast.error('This page is only accessible to drivers');
      setShouldRedirect(true);
    }
  }, [currentUser, loading]);

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

  if (shouldRedirect || currentUser.userType !== 'DRIVER') {
    return <Navigate to="/" />;
  }

  return element;
};

// Specific route that only riders can access
const RiderRoute = ({ element }) => {
  const { currentUser, loading } = useAuth();
  const [shouldRedirect, setShouldRedirect] = useState(false);

  useEffect(() => {
    if (!loading && currentUser && currentUser.userType !== 'RIDER') {
      toast.error('This page is only accessible to riders');
      setShouldRedirect(true);
    }
  }, [currentUser, loading]);

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

  if (shouldRedirect || currentUser.userType !== 'RIDER') {
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
        console.log('✅ Time synchronized with server');
      } catch (error) {
        console.warn('⚠️ Failed to sync time with server:', error.message || error);
        // Don't show error to user as this is not critical
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
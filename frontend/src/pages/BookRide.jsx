import { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { rideService, driverService } from '../services/api';
import toast from 'react-hot-toast';
import { useNavigate } from 'react-router-dom';

export default function BookRide() {
  const { currentUser } = useAuth();
  const navigate = useNavigate();
  
  const [formData, setFormData] = useState({
    pickup: '',
    destination: '',
  });
  
  const [availableCabs, setAvailableCabs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isBooking, setIsBooking] = useState(false);
  const [showConfirmation, setShowConfirmation] = useState(false);
  const [estimatedFare, setEstimatedFare] = useState(null);
  const [estimatedDistance, setEstimatedDistance] = useState(null);
  const [estimatedTime, setEstimatedTime] = useState(null);
  
  // Common locations for demo with icons
  const locations = [
    { name: 'Downtown', icon: '🏙️' },
    { name: 'Airport', icon: '✈️' },
    { name: 'Mall', icon: '🛍️' },
    { name: 'University', icon: '🎓' },
    { name: 'Tech Park', icon: '💼' },
    { name: 'Hospital', icon: '🏥' },
    { name: 'Stadium', icon: '🏟️' },
    { name: 'Railway Station', icon: '🚉' },
    { name: 'Bus Terminal', icon: '🚌' },
    { name: 'Beach', icon: '🏖️' },
  ];

  useEffect(() => {
    // Redirect if not logged in
    if (!currentUser) {
      navigate('/login');
    }
    
    // Redirect drivers to their dashboard
    if (currentUser?.userType === 'DRIVER') {
      navigate('/');
      toast.error('Drivers cannot book rides. Please use a rider account.');
    }
  }, [currentUser, navigate]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.pickup || !formData.destination) {
      toast.error('Please provide both pickup and destination locations');
      return;
    }
    
    if (formData.pickup === formData.destination) {
      toast.error('Pickup and destination cannot be the same');
      return;
    }
    
    setIsLoading(true);
    
    try {
      // Get available cabs
      const result = await driverService.getAvailableCabs(formData.pickup);
      
      if (result.success && result.available_drivers && result.available_drivers.length > 0) {
        setAvailableCabs(result.available_drivers);
        
        // Calculate estimated fare (simulated here, actual calculation would be from backend)
        const distance = Math.floor(Math.random() * 20) + 1; // 1-20 km
        const time = Math.floor(distance * 3) + 5; // 3 min/km + 5 min base
        const fare = 50 + (distance * 12); // Base fare + per km charge
        
        setEstimatedDistance(distance);
        setEstimatedTime(time);
        setEstimatedFare(fare);
        setShowConfirmation(true);
      } else {
        toast.error('No cabs available near your location. Please try again later.');
      }
    } catch (error) {
      console.error('Error fetching available cabs:', error);
      toast.error('Failed to find available cabs. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const confirmBooking = async () => {
    setIsBooking(true);
    
    try {
      const result = await rideService.bookCab(
        currentUser.username,
        formData.pickup,
        formData.destination
      );
      
      if (result.success) {
        toast.success('🎉 Ride booked successfully!');
        // Reset form
        setFormData({ pickup: '', destination: '' });
        setShowConfirmation(false);
        setAvailableCabs([]);
      } else {
        toast.error(result.message || 'Failed to book ride');
      }
    } catch (error) {
      console.error('Error booking ride:', error);
      toast.error('An error occurred while booking your ride');
    } finally {
      setIsBooking(false);
    }
  };

  const cancelBooking = () => {
    setShowConfirmation(false);
    setAvailableCabs([]);
  };

  const getLocationIcon = (locationName) => {
    const location = locations.find(loc => loc.name === locationName);
    return location ? location.icon : '📍';
  };

  // Render confirmation modal
  const renderConfirmationModal = () => {
    if (!showConfirmation) return null;
    
    return (
      <div className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
        <div className="bg-white rounded-2xl shadow-2xl max-w-lg w-full transform transition-all">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-t-2xl p-6 text-white">
            <h3 className="text-2xl font-bold">🚕 Confirm Your Ride</h3>
            <p className="text-blue-100 mt-1">Review details before booking</p>
          </div>
          
          {/* Content */}
          <div className="p-6 space-y-4">
            {/* Route */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-4 border border-blue-200">
              <div className="flex items-start space-x-3">
                <div className="flex flex-col items-center">
                  <div className="bg-green-500 rounded-full w-3 h-3"></div>
                  <div className="w-0.5 h-8 bg-gray-300"></div>
                  <div className="bg-red-500 rounded-full w-3 h-3"></div>
                </div>
                <div className="flex-1 space-y-2">
                  <div>
                    <p className="text-xs text-gray-500 font-medium">PICKUP</p>
                    <p className="text-lg font-semibold text-gray-800 flex items-center">
                      <span className="mr-2">{getLocationIcon(formData.pickup)}</span>
                      {formData.pickup}
                    </p>
                  </div>
                  <div>
                    <p className="text-xs text-gray-500 font-medium">DESTINATION</p>
                    <p className="text-lg font-semibold text-gray-800 flex items-center">
                      <span className="mr-2">{getLocationIcon(formData.destination)}</span>
                      {formData.destination}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Trip Details */}
            <div className="grid grid-cols-3 gap-3">
              <div className="bg-blue-50 rounded-lg p-3 text-center border border-blue-200">
                <p className="text-xs text-blue-600 font-medium mb-1">DISTANCE</p>
                <p className="text-xl font-bold text-blue-900">{estimatedDistance} km</p>
              </div>
              <div className="bg-purple-50 rounded-lg p-3 text-center border border-purple-200">
                <p className="text-xs text-purple-600 font-medium mb-1">EST. TIME</p>
                <p className="text-xl font-bold text-purple-900">{estimatedTime} min</p>
              </div>
              <div className="bg-green-50 rounded-lg p-3 text-center border border-green-200">
                <p className="text-xs text-green-600 font-medium mb-1">FARE</p>
                <p className="text-xl font-bold text-green-900">₹{estimatedFare}</p>
              </div>
            </div>

            {/* Available Drivers */}
            {availableCabs.length > 0 && (
              <div className="mt-4">
                <p className="text-sm font-medium text-gray-700 mb-2">
                  {availableCabs.length} driver{availableCabs.length > 1 ? 's' : ''} available
                </p>
                <div className="max-h-40 overflow-y-auto space-y-2">
                  {availableCabs.slice(0, 3).map((cab) => (
                    <div key={cab.username} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="bg-blue-500 rounded-full w-10 h-10 flex items-center justify-center text-white font-bold">
                            {cab.name?.[0] || cab.username?.[0] || 'D'}
                          </div>
                          <div>
                            <p className="font-medium text-gray-800">{cab.name || cab.username}</p>
                            <p className="text-xs text-gray-500">
                              {cab.vehicle_info?.type} • {cab.vehicle_info?.model || 'Standard Car'}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-semibold text-yellow-600">⭐ {cab.rating || '5.0'}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          {/* Actions */}
          <div className="p-6 bg-gray-50 rounded-b-2xl flex space-x-3">
            <button
              onClick={cancelBooking}
              className="flex-1 px-4 py-3 border-2 border-gray-300 bg-white rounded-xl text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={confirmBooking}
              disabled={isBooking}
              className={`flex-1 px-4 py-3 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl text-white font-semibold hover:from-blue-700 hover:to-purple-700 transition-all shadow-lg ${
                isBooking ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {isBooking ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-2 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Booking...
                </span>
              ) : (
                '✅ Confirm Booking'
              )}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-pink-600 rounded-2xl shadow-2xl p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">🚕 Book Your Ride</h1>
            <p className="text-blue-100 text-lg">Find the perfect cab for your journey</p>
          </div>
          <div className="hidden md:block">
            <svg className="w-32 h-32 opacity-20" fill="currentColor" viewBox="0 0 20 20">
              <path d="M8 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0zM15 16.5a1.5 1.5 0 11-3 0 1.5 1.5 0 013 0z"/>
              <path d="M3 4a1 1 0 00-1 1v10a1 1 0 001 1h1.05a2.5 2.5 0 014.9 0H10a1 1 0 001-1V5a1 1 0 00-1-1H3zM14 7a1 1 0 00-1 1v6.05A2.5 2.5 0 0115.95 16H17a1 1 0 001-1v-5a1 1 0 00-.293-.707l-2-2A1 1 0 0015 7h-1z"/>
            </svg>
          </div>
        </div>
      </div>

      {/* Booking Form */}
      <div className="bg-white rounded-2xl shadow-xl">
        <div className="p-8">
          <div className="flex items-center space-x-3 mb-6">
            <div className="bg-blue-100 rounded-full p-3">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-800">Where are you going?</h2>
              <p className="text-gray-600">Select your pickup and destination</p>
            </div>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Pickup Location */}
              <div>
                <label htmlFor="pickup" className="block text-sm font-semibold text-gray-700 mb-2">
                  📍 Pickup Location
                </label>
                <select
                  id="pickup"
                  name="pickup"
                  value={formData.pickup}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-base bg-white"
                >
                  <option value="">Choose pickup location</option>
                  {locations.map(location => (
                    <option key={location.name} value={location.name}>
                      {location.icon} {location.name}
                    </option>
                  ))}
                </select>
              </div>
              
              {/* Destination */}
              <div>
                <label htmlFor="destination" className="block text-sm font-semibold text-gray-700 mb-2">
                  🎯 Destination
                </label>
                <select
                  id="destination"
                  name="destination"
                  value={formData.destination}
                  onChange={handleChange}
                  required
                  className="w-full px-4 py-3 rounded-xl border-2 border-gray-300 focus:border-purple-500 focus:ring-2 focus:ring-purple-200 transition-all text-base bg-white"
                >
                  <option value="">Choose destination</option>
                  {locations.map(location => (
                    <option key={location.name} value={location.name}>
                      {location.icon} {location.name}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            
            {/* Submit Button */}
            <button
              type="submit"
              disabled={isLoading}
              className={`w-full py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-bold rounded-xl shadow-lg hover:from-blue-700 hover:to-purple-700 transition-all transform hover:scale-[1.02] ${
                isLoading ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {isLoading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Finding Available Cabs...
                </span>
              ) : (
                <span className="flex items-center justify-center">
                  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                  Find Available Cabs
                </span>
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Features */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-blue-500">
          <div className="flex items-start space-x-4">
            <div className="bg-blue-100 rounded-full p-3">
              <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-gray-800">Instant Booking</h3>
              <p className="text-sm text-gray-600 mt-1">Get matched with drivers in seconds</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-green-500">
          <div className="flex items-start space-x-4">
            <div className="bg-green-100 rounded-full p-3">
              <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-gray-800">Verified Drivers</h3>
              <p className="text-sm text-gray-600 mt-1">All drivers are verified and rated</p>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl shadow-lg p-6 border-l-4 border-purple-500">
          <div className="flex items-start space-x-4">
            <div className="bg-purple-100 rounded-full p-3">
              <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <div>
              <h3 className="font-bold text-gray-800">Fair Pricing</h3>
              <p className="text-sm text-gray-600 mt-1">Transparent pricing with no hidden fees</p>
            </div>
          </div>
        </div>
      </div>
      
      {renderConfirmationModal()}
    </div>
  );
}
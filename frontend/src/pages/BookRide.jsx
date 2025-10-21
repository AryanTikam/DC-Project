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
  
  // Common locations for demo
  const locations = [
    'Downtown', 'Airport', 'Mall', 'University', 'Tech Park',
    'Hospital', 'Stadium', 'Railway Station', 'Bus Terminal', 'Beach',
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
        toast.success('Ride booked successfully!');
        navigate('/my-rides');
      } else {
        toast.error(result.message || 'Failed to book ride');
      }
    } catch (error) {
      console.error('Error booking ride:', error);
      toast.error('An error occurred while booking your ride');
    } finally {
      setIsBooking(false);
      setShowConfirmation(false);
    }
  };

  const cancelBooking = () => {
    setShowConfirmation(false);
    setAvailableCabs([]);
  };

  // Render confirmation modal
  const renderConfirmationModal = () => {
    if (!showConfirmation) return null;
    
    return (
      <div className="fixed inset-0 bg-gray-600 bg-opacity-75 flex items-center justify-center z-10">
        <div className="bg-white rounded-lg p-6 max-w-md w-full">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Confirm your booking</h3>
          
          <div className="space-y-3 mb-6">
            <p><span className="font-medium">Pickup:</span> {formData.pickup}</p>
            <p><span className="font-medium">Destination:</span> {formData.destination}</p>
            <p><span className="font-medium">Distance:</span> {estimatedDistance} km</p>
            <p><span className="font-medium">Est. Time:</span> {estimatedTime} minutes</p>
            <p className="text-lg font-bold">Estimated Fare: ₹{estimatedFare}</p>
          </div>
          
          <div className="mt-4 flex justify-end space-x-3">
            <button
              onClick={cancelBooking}
              className="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              onClick={confirmBooking}
              disabled={isBooking}
              className={`inline-flex justify-center rounded-md border border-transparent bg-primary-600 px-4 py-2 text-sm font-medium text-white shadow-sm hover:bg-primary-700 ${
                isBooking ? 'opacity-70 cursor-not-allowed' : ''
              }`}
            >
              {isBooking ? 'Booking...' : 'Confirm Booking'}
            </button>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="bg-white shadow sm:rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-semibold text-gray-900">Book a Ride</h1>
          <p className="mt-1 text-sm text-gray-600">
            Enter your pickup and destination to find available cabs.
          </p>
          
          <form onSubmit={handleSubmit} className="mt-6">
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="pickup" className="block text-sm font-medium text-gray-700">
                  Pickup Location
                </label>
                <select
                  id="pickup"
                  name="pickup"
                  value={formData.pickup}
                  onChange={handleChange}
                  required
                  className="mt-1 block w-full rounded-md border border-gray-300 py-2 pl-3 pr-10 text-base focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm"
                >
                  <option value="">Select Pickup Location</option>
                  {locations.map(location => (
                    <option key={location} value={location}>{location}</option>
                  ))}
                </select>
              </div>
              
              <div>
                <label htmlFor="destination" className="block text-sm font-medium text-gray-700">
                  Destination
                </label>
                <select
                  id="destination"
                  name="destination"
                  value={formData.destination}
                  onChange={handleChange}
                  required
                  className="mt-1 block w-full rounded-md border border-gray-300 py-2 pl-3 pr-10 text-base focus:border-primary-500 focus:outline-none focus:ring-primary-500 sm:text-sm"
                >
                  <option value="">Select Destination</option>
                  {locations.map(location => (
                    <option key={location} value={location}>{location}</option>
                  ))}
                </select>
              </div>
            </div>
            
            <div className="mt-6">
              <button
                type="submit"
                disabled={isLoading}
                className={`w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 ${
                  isLoading ? 'opacity-70 cursor-not-allowed' : ''
                }`}
              >
                {isLoading ? 'Finding Cabs...' : 'Find Cabs'}
              </button>
            </div>
          </form>
          
          {availableCabs.length > 0 && !showConfirmation && (
            <div className="mt-8">
              <h2 className="text-lg font-medium text-gray-900">Available Drivers</h2>
              
              <ul className="mt-3 divide-y divide-gray-200">
                {availableCabs.map((cab) => (
                  <li key={cab.username} className="py-4 flex">
                    <div className="ml-3 flex-1">
                      <p className="text-sm font-medium text-gray-900">{cab.name || cab.username}</p>
                      <p className="text-sm text-gray-500">Location: {cab.location}</p>
                      <p className="text-sm text-gray-500">
                        {cab.vehicle_info?.type} {cab.vehicle_info?.model} • {cab.vehicle_info?.license_plate || 'No plate info'}
                      </p>
                      <div className="mt-1">
                        <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                          Rating: {cab.rating} ★
                        </span>
                      </div>
                    </div>
                  </li>
                ))}
              </ul>
              
              <div className="mt-4">
                <button
                  onClick={() => setShowConfirmation(true)}
                  className="w-full inline-flex items-center justify-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  Proceed to Booking
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {renderConfirmationModal()}
    </div>
  );
}
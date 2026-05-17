import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import { Palmtree, MapPin, Calendar, IndianRupee, Sparkles, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';

const CITIES = [
  { id: 'Goa', name: 'Goa', desc: 'Beaches, nightlife, and heritage' },
  { id: 'Jaipur', name: 'Jaipur', desc: 'Palaces, forts, and rich culture' },
  { id: 'Manali', name: 'Manali', desc: 'Mountains, adventure, and nature' }
];

const GenerateItineraryPage: React.FC = () => {
  const [city, setCity] = useState('');
  const [days, setDays] = useState<number>(3);
  const [budget, setBudget] = useState<number>(10000);
  const [stayBudget, setStayBudget] = useState<number>(1000);
  const [foodBudget, setFoodBudget] = useState<number>(1000);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleGenerate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!city) {
      setError('Please select a destination city.');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await apiClient.post('/itineraries/generate', {
        city: city,
        num_days: days,
        budget_total: budget,
        stay_budget_per_night: stayBudget,
        food_budget_per_day: foodBudget
      });
      
      // Redirect to the newly generated itinerary details page
      navigate(`/itinerary/${response.data.id}`);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate itinerary. Ensure you have completed your profile quiz.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-dark-bg py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="text-center mb-12">
          <h1 className="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4 flex items-center justify-center">
            <Sparkles className="w-8 h-8 text-primary-500 mr-3" />
            Plan Your Perfect Getaway
          </h1>
          <p className="text-lg text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">
            We'll take your preferences and build a chill, stress-free plan just for you.
          </p>
        </div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-white dark:bg-dark-surface rounded-3xl shadow-xl border border-slate-100 dark:border-dark-border overflow-hidden"
        >
          <div className="grid md:grid-cols-5 h-full">
            
            {/* Left Side: Information */}
            <div className="md:col-span-2 bg-gradient-to-br from-amber-500 to-orange-600 p-10 text-white flex flex-col justify-between">
              <div>
                <h3 className="text-2xl font-bold mb-6">How it works</h3>
                <ul className="space-y-6">
                  <li className="flex">
                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center mr-4 shrink-0">1</div>
                    <div>
                      <h4 className="font-semibold text-lg">Select Destination</h4>
                      <p className="text-primary-100 text-sm mt-1">Choose where you want to go.</p>
                    </div>
                  </li>
                  <li className="flex">
                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center mr-4 shrink-0">2</div>
                    <div>
                      <h4 className="font-semibold text-lg">Set Constraints</h4>
                      <p className="text-primary-100 text-sm mt-1">Tell us your available time and max budget.</p>
                    </div>
                  </li>
                  <li className="flex">
                    <div className="w-8 h-8 rounded-full bg-white/20 flex items-center justify-center mr-4 shrink-0">3</div>
                    <div>
                      <h4 className="font-semibold text-lg">Smart Planning</h4>
                      <p className="text-primary-100 text-sm mt-1">We create a smooth, easy-going route that perfectly matches your vibe.</p>
                    </div>
                  </li>
                </ul>
              </div>
              <div className="mt-12 p-4 bg-white/10 rounded-xl backdrop-blur-sm border border-white/20">
                <p className="text-sm flex items-start">
                  <AlertCircle className="w-5 h-5 mr-2 shrink-0 text-amber-300" />
                  Your generated plan will automatically avoid places that clash with your crowd tolerance and physical pace.
                </p>
              </div>
            </div>

            {/* Right Side: Form */}
            <div className="md:col-span-3 p-10">
              <form onSubmit={handleGenerate} className="space-y-8">
                {error && (
                  <div className="bg-red-50 dark:bg-red-900/30 text-red-600 dark:text-red-400 p-4 rounded-xl text-sm border border-red-200 dark:border-red-800">
                    {error}
                  </div>
                )}

                {/* Destination */}
                <div>
                  <label className="block text-lg font-medium text-slate-900 dark:text-white mb-4 flex items-center">
                    <MapPin className="w-5 h-5 mr-2 text-primary-500" /> Where do you want to go?
                  </label>
                  <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                    {CITIES.map(c => (
                      <div 
                        key={c.id}
                        onClick={() => setCity(c.id)}
                        className={`cursor-pointer rounded-xl p-4 border-2 transition-all duration-200 text-center
                          ${city === c.id 
                            ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' 
                            : 'border-slate-200 dark:border-slate-700 hover:border-primary-300 dark:hover:border-slate-500'}`}
                      >
                        <h4 className={`font-bold ${city === c.id ? 'text-primary-700 dark:text-primary-400' : 'text-slate-700 dark:text-slate-300'}`}>
                          {c.name}
                        </h4>
                        <p className="text-xs text-slate-500 dark:text-slate-400 mt-1">{c.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Duration */}
                <div>
                  <label className="block text-lg font-medium text-slate-900 dark:text-white mb-4 flex items-center">
                    <Calendar className="w-5 h-5 mr-2 text-primary-500" /> How many days?
                  </label>
                  <div className="flex items-center space-x-4">
                    <input 
                      type="range" 
                      min="1" 
                      max="7" 
                      value={days}
                      onChange={(e) => setDays(parseInt(e.target.value))}
                      className="w-full h-2 bg-slate-200 dark:bg-slate-700 rounded-lg appearance-none cursor-pointer accent-primary-600"
                    />
                    <div className="w-16 h-12 bg-slate-100 dark:bg-slate-800 rounded-xl flex items-center justify-center font-bold text-xl text-primary-600 dark:text-primary-400 border border-slate-200 dark:border-slate-700 shadow-inner">
                      {days}
                    </div>
                  </div>
                  <div className="flex justify-between text-xs text-slate-400 mt-2 px-1">
                    <span>1 Day</span>
                    <span>7 Days</span>
                  </div>
                </div>

                {/* Budget */}
                <div>
                  <label className="block text-lg font-medium text-slate-900 dark:text-white mb-4 flex items-center">
                    <IndianRupee className="w-5 h-5 mr-2 text-primary-500" /> Max Budget (INR)
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <span className="text-slate-500 font-medium">₹</span>
                    </div>
                    <input 
                      type="number" 
                      min="1000"
                      step="500"
                      value={budget}
                      onChange={(e) => setBudget(parseInt(e.target.value))}
                      className="input-field pl-10 text-lg font-medium"
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-2">This budget covers activities and internal travel (excluding flights/hotels).</p>
                </div>

                {/* Stay Budget */}
                <div>
                  <label className="block text-lg font-medium text-slate-900 dark:text-white mb-4 flex items-center">
                    <IndianRupee className="w-5 h-5 mr-2 text-primary-500" /> Stay Budget Per Night (INR)
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <span className="text-slate-500 font-medium">₹</span>
                    </div>
                    <input 
                      type="number" 
                      min="500"
                      max="2000"
                      step="100"
                      value={stayBudget}
                      onChange={(e) => setStayBudget(parseInt(e.target.value))}
                      className="input-field pl-10 text-lg font-medium"
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-2">Suggested stay options per night based on your budget (500 - 2000).</p>
                </div>

                {/* Food Budget */}
                <div>
                  <label className="block text-lg font-medium text-slate-900 dark:text-white mb-4 flex items-center">
                    <IndianRupee className="w-5 h-5 mr-2 text-primary-500" /> Food Budget Per Day (INR)
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                      <span className="text-slate-500 font-medium">₹</span>
                    </div>
                    <input 
                      type="number" 
                      min="500"
                      max="2000"
                      step="100"
                      value={foodBudget}
                      onChange={(e) => setFoodBudget(parseInt(e.target.value))}
                      className="input-field pl-10 text-lg font-medium"
                    />
                  </div>
                  <p className="text-xs text-slate-500 mt-2">Personalized restaurant suggestions per day (500 - 2000).</p>
                </div>

                <div className="pt-4 border-t border-slate-100 dark:border-slate-800">
                  <button 
                    type="submit"
                    disabled={loading}
                    className="w-full btn-primary py-4 text-lg flex items-center justify-center shadow-xl shadow-primary-500/20"
                  >
                    {loading ? (
                      <span className="flex items-center">
                        <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin mr-3"></div>
                        Putting together your trip...
                      </span>
                    ) : (
                      <span className="flex items-center">
                        Plan My Trip <Palmtree className="w-5 h-5 ml-2" />
                      </span>
                    )}
                  </button>
                </div>

              </form>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default GenerateItineraryPage;

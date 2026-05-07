import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { MapPin, Search, Compass, IndianRupee, Heart, Filter, Star, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

interface Attraction {
  id: number;
  name: string;
  city: string;
  category: string;
  description: string;
  cost_estimate_inr: number;
  avg_visit_duration_hours: number;
  best_visiting_time: string;
  is_favorite: boolean;
  match_score: number | null;
  match_reason: string | null;
}

const ExplorePage: React.FC = () => {
  const [attractions, setAttractions] = useState<Attraction[]>([]);
  const [loading, setLoading] = useState(true);
  const [cityFilter, setCityFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    const fetchAttractions = async () => {
      setLoading(true);
      try {
        const url = cityFilter ? `/attractions?city=${cityFilter}` : '/attractions';
        const response = await apiClient.get(url);
        setAttractions(response.data);
      } catch (error) {
        console.error("Failed to load attractions", error);
      } finally {
        setLoading(false);
      }
    };

    fetchAttractions();
  }, [cityFilter]);

  const toggleFavorite = async (id: number) => {
    try {
      await apiClient.post(`/attractions/${id}/favorite`);
      setAttractions(attractions.map(attr => 
        attr.id === id ? { ...attr, is_favorite: !attr.is_favorite } : attr
      ));
    } catch (error) {
      console.error("Failed to toggle favorite", error);
    }
  };

  const filteredAttractions = attractions.filter(a => 
    a.name.toLowerCase().includes(searchQuery.toLowerCase()) || 
    a.category.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-dark-bg py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        
        {/* Header & Search */}
        <div className="mb-10">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-2 flex items-center">
            <Compass className="w-8 h-8 mr-3 text-primary-500" /> Explore Destinations
          </h1>
          <p className="text-slate-600 dark:text-slate-400 max-w-2xl">
            {user?.has_profile 
              ? "Discover places scored specifically for your travel archetype by our ML engine."
              : "Browse top attractions across India. Take the personality quiz to get personalized match scores!"}
          </p>

          <div className="mt-8 flex flex-col sm:flex-row gap-4">
            <div className="relative flex-grow">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-slate-400" />
              </div>
              <input
                type="text"
                className="input-field pl-10 h-12 shadow-sm"
                placeholder="Search by name or category (e.g., Beach, Temple)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
              />
            </div>
            
            <div className="flex gap-2 overflow-x-auto pb-2 sm:pb-0 scrollbar-hide shrink-0">
              {['', 'Goa', 'Jaipur', 'Manali'].map((city) => (
                <button
                  key={city}
                  onClick={() => setCityFilter(city)}
                  className={`
                    px-6 py-2 h-12 rounded-lg font-medium whitespace-nowrap transition-all duration-200 border shadow-sm
                    ${cityFilter === city 
                      ? 'bg-slate-900 text-white border-slate-900 dark:bg-white dark:text-slate-900 dark:border-white' 
                      : 'bg-white text-slate-700 border-slate-200 hover:bg-slate-50 dark:bg-dark-surface dark:text-slate-300 dark:border-slate-700 dark:hover:bg-slate-800'}
                  `}
                >
                  {city || 'All Cities'}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Results Grid */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-10 h-10 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <AnimatePresence>
              {filteredAttractions.map((attr, index) => (
                <motion.div
                  key={attr.id}
                  initial={{ opacity: 0, scale: 0.95 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.9 }}
                  transition={{ duration: 0.2, delay: index * 0.05 }}
                  className="bg-white dark:bg-dark-surface rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-100 dark:border-dark-border overflow-hidden flex flex-col group"
                >
                  {/* Image Placeholder (Gradient based on category) */}
                  <div className={`h-48 relative bg-gradient-to-br 
                    ${attr.category === 'Beach' ? 'from-blue-400 to-cyan-300' : 
                      attr.category === 'Heritage' ? 'from-amber-600 to-orange-400' :
                      attr.category === 'Nature' ? 'from-green-500 to-emerald-400' :
                      attr.category === 'Adventure' ? 'from-red-500 to-orange-500' :
                      'from-indigo-500 to-purple-500'}`}
                  >
                    <div className="absolute inset-0 bg-black/10 group-hover:bg-transparent transition-colors"></div>
                    <button 
                      onClick={() => toggleFavorite(attr.id)}
                      className="absolute top-4 right-4 w-10 h-10 bg-white/20 hover:bg-white/40 backdrop-blur-md rounded-full flex items-center justify-center transition-colors"
                    >
                      <Heart className={`w-5 h-5 ${attr.is_favorite ? 'fill-red-500 text-red-500' : 'text-white'}`} />
                    </button>
                    
                    <div className="absolute bottom-4 left-4">
                      <span className="px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-xs font-semibold text-white shadow-sm border border-white/30 uppercase tracking-wider">
                        {attr.category}
                      </span>
                    </div>
                  </div>

                  {/* Content */}
                  <div className="p-5 flex-grow flex flex-col">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="text-xl font-bold text-slate-900 dark:text-white line-clamp-1" title={attr.name}>{attr.name}</h3>
                      {attr.match_score && (
                        <div className={`flex items-center text-sm font-bold px-2 py-1 rounded-md shrink-0 ml-2
                          ${attr.match_score >= 80 ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 
                            attr.match_score >= 50 ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' : 
                            'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'}`}
                        >
                          <Sparkles className="w-3 h-3 mr-1" />
                          {attr.match_score}%
                        </div>
                      )}
                    </div>
                    
                    <p className="text-sm text-slate-500 dark:text-slate-400 flex items-center mb-3">
                      <MapPin className="w-4 h-4 mr-1" /> {attr.city}
                    </p>

                    <p className="text-sm text-slate-600 dark:text-slate-300 line-clamp-2 mb-4 flex-grow">
                      {attr.description}
                    </p>

                    {attr.match_reason && (
                      <p className="text-xs text-indigo-600 dark:text-indigo-400 mb-4 font-medium italic line-clamp-1">
                        "{attr.match_reason}"
                      </p>
                    )}

                    <div className="flex items-center justify-between pt-4 border-t border-slate-100 dark:border-slate-800">
                      <div className="flex items-center text-sm text-slate-700 dark:text-slate-300 font-medium">
                        <IndianRupee className="w-4 h-4 mr-1" />
                        {attr.cost_estimate_inr > 0 ? attr.cost_estimate_inr : 'Free'}
                      </div>
                      <div className="text-sm text-slate-500 dark:text-slate-400">
                        {attr.avg_visit_duration_hours}h • {attr.best_visiting_time}
                      </div>
                    </div>
                  </div>
                </motion.div>
              ))}
            </AnimatePresence>
          </div>
        )}
        
        {!loading && filteredAttractions.length === 0 && (
          <div className="text-center py-20 text-slate-500">
            <Filter className="w-12 h-12 mx-auto mb-4 opacity-20" />
            <p>No attractions found matching your criteria.</p>
          </div>
        )}

      </div>
    </div>
  );
};

export default ExplorePage;

import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { MapPin, Search, Compass, IndianRupee, Heart, Filter, Star, Sparkles, X, ChevronLeft, ChevronRight, User as UserIcon } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { useAuth } from '../context/AuthContext';

interface Review {
  user: string;
  rating: number;
  text: string;
  date: string;
}

interface Attraction {
  id: number;
  name: string;
  city: string;
  category: string;
  description: string;
  image_url: string;
  image_urls: string[];
  reviews: Review[];
  cost_breakdown: Record<string, any>;
  cost_estimate_inr: number;
  avg_visit_duration_hours: number;
  best_visiting_time: string;
  is_favorite: boolean;
  match_score: number | null;
  match_reason: string | null;
}

const PLACEHOLDER_GRADIENT: Record<string, string> = {
  Beach: 'from-blue-400 to-cyan-300',
  Heritage: 'from-amber-600 to-orange-400',
  Nature: 'from-green-500 to-emerald-400',
  Adventure: 'from-red-500 to-orange-500',
  Shopping: 'from-pink-500 to-rose-400',
  Nightlife: 'from-purple-600 to-indigo-500',
  Culture: 'from-teal-500 to-cyan-400',
};

function primaryImage(attr: Attraction): string | null {
  if (attr.image_urls?.length) return attr.image_urls[0];
  return attr.image_url || null;
}

const ExplorePage: React.FC = () => {
  const [attractions, setAttractions] = useState<Attraction[]>([]);
  const [loading, setLoading] = useState(true);
  const [cityFilter, setCityFilter] = useState<string>('');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedAttraction, setSelectedAttraction] = useState<Attraction | null>(null);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
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
              ? "Discover spots hand-picked for your unique vibe."
              : "Browse top spots across India. Take the quick vibe check to see what matches your style!"}
          </p>

          <div className="mt-8 flex flex-col sm:flex-row gap-4">
            <div className="relative flex-grow">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-5 w-5 text-slate-400" />
              </div>
              <input
                type="text"
                className="input-field pl-10 h-12 shadow-sm"
                placeholder="Find your next favorite spot (e.g., Beach, Cafe)..."
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
                  onClick={() => { setSelectedAttraction(attr); setActiveImageIndex(0); }}
                  className="bg-white dark:bg-dark-surface rounded-2xl shadow-sm hover:shadow-xl transition-all duration-300 border border-slate-100 dark:border-dark-border overflow-hidden flex flex-col group cursor-pointer"
                >
                  {/* Image */}
                  <div className={`h-48 relative bg-slate-200 dark:bg-slate-800 overflow-hidden`}>
                    {primaryImage(attr) ? (
                      <img
                        src={primaryImage(attr)!}
                        alt={attr.name}
                        loading="lazy"
                        referrerPolicy="no-referrer"
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                        onError={(e) => {
                          const fallbacks = attr.image_urls?.slice(1) ?? [];
                          const next = fallbacks.find((u) => u !== e.currentTarget.src);
                          if (next) {
                            e.currentTarget.src = next;
                          } else {
                            e.currentTarget.style.display = 'none';
                          }
                        }}
                      />
                    ) : (
                      <motion.div className={`absolute inset-0 bg-gradient-to-br ${PLACEHOLDER_GRADIENT[attr.category] || 'from-indigo-500 to-purple-500'}`} />
                    )}
                    <div className="absolute inset-0 bg-black/10 group-hover:bg-black/20 transition-colors"></div>
                    <button 
                      onClick={(e) => { e.stopPropagation(); toggleFavorite(attr.id); }}
                      className="absolute top-4 right-4 w-10 h-10 bg-white/20 hover:bg-white/40 backdrop-blur-md rounded-full flex items-center justify-center transition-colors z-10"
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

        {/* Attraction Details Modal */}
        <AnimatePresence>
          {selectedAttraction && (
            <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
              <motion.div 
                initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
                onClick={() => setSelectedAttraction(null)}
                className="absolute inset-0 bg-slate-900/60 backdrop-blur-sm"
              />
              <motion.div 
                initial={{ opacity: 0, scale: 0.95, y: 20 }} animate={{ opacity: 1, scale: 1, y: 0 }} exit={{ opacity: 0, scale: 0.95, y: 20 }}
                className="bg-white dark:bg-dark-surface w-full max-w-4xl max-h-[90vh] rounded-2xl shadow-2xl relative overflow-hidden flex flex-col z-10"
              >
                <button 
                  onClick={() => setSelectedAttraction(null)}
                  className="absolute top-4 right-4 z-20 w-10 h-10 bg-black/20 hover:bg-black/40 backdrop-blur-md rounded-full flex items-center justify-center text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>

                <div className="flex flex-col md:flex-row h-full overflow-y-auto md:overflow-hidden">
                  
                  {/* Left: Images */}
                  <div className="w-full md:w-1/2 relative bg-slate-900 min-h-[300px] md:min-h-full shrink-0 group">
                    {selectedAttraction.image_urls && selectedAttraction.image_urls.length > 0 ? (
                      <>
                        <img 
                          src={selectedAttraction.image_urls[activeImageIndex]} 
                          alt={selectedAttraction.name}
                          referrerPolicy="no-referrer"
                          className="w-full h-full object-cover"
                          onError={(e) => {
                            const fallbacks = selectedAttraction.image_urls.filter((u) => u !== e.currentTarget.src);
                            if (fallbacks.length) e.currentTarget.src = fallbacks[0];
                          }}
                        />
                        {selectedAttraction.image_urls.length > 1 && (
                          <>
                            <button 
                              onClick={(e) => { e.stopPropagation(); setActiveImageIndex((prev) => (prev === 0 ? selectedAttraction.image_urls.length - 1 : prev - 1)); }}
                              className="absolute left-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/30 hover:bg-black/50 backdrop-blur-md rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <ChevronLeft className="w-6 h-6" />
                            </button>
                            <button 
                              onClick={(e) => { e.stopPropagation(); setActiveImageIndex((prev) => (prev === selectedAttraction.image_urls.length - 1 ? 0 : prev + 1)); }}
                              className="absolute right-4 top-1/2 -translate-y-1/2 w-10 h-10 bg-black/30 hover:bg-black/50 backdrop-blur-md rounded-full flex items-center justify-center text-white opacity-0 group-hover:opacity-100 transition-opacity"
                            >
                              <ChevronRight className="w-6 h-6" />
                            </button>
                            <div className="absolute bottom-4 left-1/2 -translate-x-1/2 flex space-x-2">
                              {selectedAttraction.image_urls.map((_, i) => (
                                <div key={i} className={`w-2 h-2 rounded-full transition-all ${i === activeImageIndex ? 'bg-white scale-125' : 'bg-white/50'}`} />
                              ))}
                            </div>
                          </>
                        )}
                      </>
                    ) : (
                      <div className="w-full h-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center">
                        <Compass className="w-16 h-16 text-slate-400 opacity-50" />
                      </div>
                    )}
                    <div className="absolute top-4 left-4">
                      <span className="px-3 py-1 bg-black/40 backdrop-blur-md rounded-full text-xs font-semibold text-white uppercase tracking-wider">
                        {selectedAttraction.category}
                      </span>
                    </div>
                  </div>

                  {/* Right: Info, Costs, Reviews */}
                  <div className="w-full md:w-1/2 flex flex-col md:overflow-y-auto p-6 lg:p-8">
                    <div className="mb-6">
                      <div className="flex justify-between items-start mb-2">
                        <h2 className="text-2xl font-bold text-slate-900 dark:text-white">{selectedAttraction.name}</h2>
                        <button 
                          onClick={() => toggleFavorite(selectedAttraction.id)}
                          className={`p-2 rounded-full transition-colors ${selectedAttraction.is_favorite ? 'bg-red-50 text-red-500 dark:bg-red-500/10' : 'bg-slate-100 text-slate-400 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700'}`}
                        >
                          <Heart className={`w-5 h-5 ${selectedAttraction.is_favorite ? 'fill-current' : ''}`} />
                        </button>
                      </div>
                      <p className="text-sm text-slate-500 dark:text-slate-400 flex items-center mb-4 font-medium">
                        <MapPin className="w-4 h-4 mr-1" /> {selectedAttraction.city}
                      </p>
                      <p className="text-slate-700 dark:text-slate-300 leading-relaxed">
                        {selectedAttraction.description}
                      </p>
                    </div>

                    {/* Cost Breakdown */}
                    <div className="mb-8 bg-slate-50 dark:bg-slate-800/50 rounded-xl p-5 border border-slate-100 dark:border-slate-700">
                      <h3 className="text-sm font-bold text-slate-900 dark:text-white uppercase tracking-wider mb-4 flex items-center">
                        <IndianRupee className="w-4 h-4 mr-2 text-primary-500" /> Cost Per Person
                      </h3>
                      <div className="flex justify-between items-end mb-4 pb-4 border-b border-slate-200 dark:border-slate-700">
                        <span className="text-slate-600 dark:text-slate-400 font-medium">Total Estimate</span>
                        <span className="text-3xl font-bold text-primary-600 dark:text-primary-400">
                          {selectedAttraction.cost_estimate_inr === 0 ? 'Free' : `₹${selectedAttraction.cost_estimate_inr}`}
                        </span>
                      </div>
                      
                      {selectedAttraction.cost_breakdown && Object.keys(selectedAttraction.cost_breakdown).length > 0 ? (
                        <div className="space-y-3">
                          {Object.entries(selectedAttraction.cost_breakdown).map(([key, value]) => (
                            <div key={key} className="flex justify-between items-center text-sm">
                              <span className="text-slate-600 dark:text-slate-400">{key}</span>
                              <span className="font-semibold text-slate-900 dark:text-slate-200">
                                {typeof value === 'number' ? `₹${value}` : value}
                              </span>
                            </div>
                          ))}
                        </div>
                      ) : null}
                    </div>

                    {/* Reviews */}
                    <div className="flex-grow">
                      <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4 flex items-center">
                        <Star className="w-5 h-5 mr-2 text-amber-500 fill-amber-500" /> Real-time Reviews
                      </h3>
                      
                      {selectedAttraction.reviews && selectedAttraction.reviews.length > 0 ? (
                        <div className="space-y-4">
                          {selectedAttraction.reviews.map((review, i) => (
                            <div key={i} className="bg-white dark:bg-dark-bg p-4 rounded-xl shadow-sm border border-slate-100 dark:border-slate-800">
                              <div className="flex justify-between items-start mb-2">
                                <div className="flex items-center">
                                  <div className="w-8 h-8 rounded-full bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center text-primary-600 dark:text-primary-400 mr-3">
                                    <UserIcon className="w-4 h-4" />
                                  </div>
                                  <div>
                                    <p className="text-sm font-semibold text-slate-900 dark:text-white">{review.user}</p>
                                    <p className="text-xs text-slate-400">{review.date}</p>
                                  </div>
                                </div>
                                <div className="flex items-center bg-amber-50 dark:bg-amber-900/20 px-2 py-1 rounded">
                                  <span className="text-sm font-bold text-amber-600 dark:text-amber-400 mr-1">{review.rating}</span>
                                  <Star className="w-3 h-3 text-amber-500 fill-amber-500" />
                                </div>
                              </div>
                              <p className="text-sm text-slate-600 dark:text-slate-300 italic">"{review.text}"</p>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-center py-8 bg-slate-50 dark:bg-slate-800/50 rounded-xl">
                          <p className="text-slate-500 dark:text-slate-400 text-sm">No reviews available yet.</p>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          )}
        </AnimatePresence>

      </div>
    </div>
  );
};

export default ExplorePage;

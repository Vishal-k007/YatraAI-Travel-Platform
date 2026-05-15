import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import apiClient from '../api/client';
import { MapPin, Calendar, Clock, IndianRupee, Zap, ArrowLeft, Brain, CheckCircle2, Download, Share2 } from 'lucide-react';
import { motion } from 'framer-motion';

const ItineraryDetailsPage: React.FC = () => {
  const { id } = useParams();
  const [itinerary, setItinerary] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [activeDay, setActiveDay] = useState(1);

  useEffect(() => {
    const fetchItinerary = async () => {
      try {
        const response = await apiClient.get(`/itineraries/${id}`);
        setItinerary(response.data);
        if (response.data.days && response.data.days.length > 0) {
          setActiveDay(response.data.days[0].day_number);
        }
      } catch (error) {
        console.error("Failed to load itinerary", error);
      } finally {
        setLoading(false);
      }
    };

    fetchItinerary();
  }, [id]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-dark-bg">
        <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  if (!itinerary) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center bg-slate-50 dark:bg-dark-bg text-center px-4">
        <h2 className="text-2xl font-bold text-slate-900 dark:text-white mb-2">Itinerary Not Found</h2>
        <p className="text-slate-500 mb-6">The itinerary you're looking for doesn't exist or you don't have access.</p>
        <Link to="/dashboard" className="btn-primary">Back to Dashboard</Link>
      </div>
    );
  }

  const currentDayData = itinerary.days.find((d: any) => d.day_number === activeDay);

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-dark-bg pb-20">
      {/* Hero Header */}
      <div className="bg-slate-900 text-white pt-24 pb-16 relative overflow-hidden">
        <div className="absolute inset-0 opacity-20">
          {/* Abstract pattern or map background could go here */}
          <div className="absolute top-0 right-0 w-96 h-96 bg-primary-500 rounded-full blur-[100px] translate-x-1/2 -translate-y-1/2"></div>
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <Link to="/dashboard" className="inline-flex items-center text-slate-300 hover:text-white mb-6 transition-colors">
            <ArrowLeft className="w-4 h-4 mr-2" /> Back to Dashboard
          </Link>
          
          <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
            <div>
              <div className="flex flex-wrap gap-3 mb-4">
                <span className="px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-sm font-medium border border-white/20 flex items-center">
                  <MapPin className="w-4 h-4 mr-1.5" /> {itinerary.city}
                </span>
                <span className="px-3 py-1 bg-white/10 backdrop-blur-md rounded-full text-sm font-medium border border-white/20 flex items-center">
                  <Calendar className="w-4 h-4 mr-1.5" /> {itinerary.num_days} Days
                </span>
                <span className="px-3 py-1 bg-primary-500/20 backdrop-blur-md rounded-full text-sm font-medium text-primary-300 border border-primary-500/30 flex items-center">
                  <Brain className="w-4 h-4 mr-1.5" /> {itinerary.match_score}% Vibe Match
                </span>
              </div>
              <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-2">{itinerary.title}</h1>
              <p className="text-slate-300 text-lg">Your Stress-Free Travel Plan</p>
            </div>
            
            <div className="flex gap-3">
              <button className="px-4 py-2 bg-white/10 hover:bg-white/20 rounded-lg text-sm font-medium flex items-center backdrop-blur-sm border border-white/10 transition-colors">
                <Share2 className="w-4 h-4 mr-2" /> Share
              </button>
              <button className="px-4 py-2 bg-white text-slate-900 hover:bg-slate-100 rounded-lg text-sm font-bold flex items-center transition-colors">
                <Download className="w-4 h-4 mr-2" /> Export PDF
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 -mt-8 relative z-20">
        
        {/* Stats Row */}
        <div className="bg-white/80 dark:bg-dark-surface/80 backdrop-blur-xl rounded-3xl shadow-xl border border-white/40 dark:border-white/10 p-6 grid grid-cols-2 md:grid-cols-5 gap-6 mb-8 relative overflow-hidden">
          <div className="absolute top-0 right-0 w-32 h-32 bg-gradient-to-br from-primary-400/20 to-indigo-500/20 rounded-full blur-2xl -mr-10 -mt-10 pointer-events-none"></div>
          
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-1">Total Budget</p>
            <p className="text-2xl font-black text-slate-900 dark:text-white flex items-center">
              <IndianRupee className="w-5 h-5 mr-1 text-primary-500" />
              {itinerary.total_estimated_cost.toLocaleString()}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-1">Attractions</p>
            <p className="text-2xl font-black text-slate-900 dark:text-white flex items-center">
              <MapPin className="w-5 h-5 mr-2 text-indigo-500" />
              {itinerary.total_attractions}
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-1">Total Commute</p>
            <p className="text-2xl font-black text-slate-900 dark:text-white flex items-center">
              <Clock className="w-5 h-5 mr-2 text-emerald-500" />
              {Math.round((itinerary.days?.reduce((acc: number, day: any) => acc + (day.total_travel_time_mins || 0), 0) || 0) / 60)}h
            </p>
          </div>
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-1">Avg Energy</p>
            <div className="flex items-center">
              <Zap className="w-5 h-5 mr-2 text-amber-500" />
              <p className="text-2xl font-black text-slate-900 dark:text-white mr-2">
                {itinerary.avg_daily_energy.toFixed(1)}
              </p>
            </div>
          </div>
          <div>
            <p className="text-xs text-slate-500 dark:text-slate-400 font-bold uppercase tracking-wider mb-1">Pace</p>
            <div className="h-full flex items-center">
              <span className={`px-3 py-1 rounded-full text-sm font-bold ${
                itinerary.avg_daily_energy > 8 ? 'bg-rose-100 text-rose-700 dark:bg-rose-900/30 dark:text-rose-400' : 
                itinerary.avg_daily_energy < 5 ? 'bg-emerald-100 text-emerald-700 dark:bg-emerald-900/30 dark:text-emerald-400' : 
                'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
              }`}>
                {itinerary.avg_daily_energy > 8 ? 'Intense' : itinerary.avg_daily_energy < 5 ? 'Relaxed' : 'Balanced'}
              </span>
            </div>
          </div>
        </div>

        {itinerary.warnings && itinerary.warnings.length > 0 && (
          <div className="bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 p-4 rounded-xl mb-8 flex items-start">
            <CheckCircle2 className="w-5 h-5 text-amber-600 dark:text-amber-500 mr-3 mt-0.5" />
            <div>
              <h4 className="font-semibold text-amber-800 dark:text-amber-400">Heads Up</h4>
              <p className="text-amber-700 dark:text-amber-300/80 text-sm mt-1">{itinerary.warnings[0]}</p>
            </div>
          </div>
        )}

        <div className="grid lg:grid-cols-3 gap-8">
          
          {/* Main Timeline Column */}
          <div className="lg:col-span-2 space-y-6">
            
            {/* Day Selector */}
            <div className="flex space-x-2 overflow-x-auto pb-2 scrollbar-hide">
              {itinerary.days.map((day: any) => (
                <button
                  key={day.day_number}
                  onClick={() => setActiveDay(day.day_number)}
                  className={`
                    px-6 py-3 rounded-xl font-medium whitespace-nowrap transition-all duration-200
                    ${activeDay === day.day_number 
                      ? 'bg-primary-600 text-white shadow-md' 
                      : 'bg-white dark:bg-dark-surface text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-800'}
                  `}
                >
                  Day {day.day_number}
                </button>
              ))}
            </div>

            {/* Day Theme */}
            {currentDayData && (
              <motion.div 
                key={`theme-${activeDay}`}
                initial={{ opacity: 0 }} animate={{ opacity: 1 }}
                className="bg-white dark:bg-dark-surface p-5 rounded-2xl shadow-sm border border-slate-100 dark:border-dark-border"
              >
                <div className="flex justify-between items-center">
                  <h3 className="text-xl font-bold text-slate-900 dark:text-white">
                    {currentDayData.theme}
                  </h3>
                  <div className="flex gap-4 text-sm text-slate-500">
                    <span className="flex items-center"><IndianRupee className="w-4 h-4 mr-1"/>{currentDayData.total_cost}</span>
                    <span className="flex items-center"><Zap className="w-4 h-4 mr-1"/>{currentDayData.total_energy?.toFixed(1)} Energy</span>
                  </div>
                </div>
              </motion.div>
            )}

            {/* Timeline */}
            <div className="space-y-6 relative before:absolute before:inset-0 before:ml-5 before:-translate-x-px md:before:mx-auto md:before:translate-x-0 before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 dark:before:via-slate-700 before:to-transparent">
              {currentDayData?.slots.map((slot: any, index: number) => (
                <motion.div 
                  key={index}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="relative flex items-center justify-between md:justify-normal md:odd:flex-row-reverse group is-active"
                >
                  {/* Timeline Node */}
                  <div className="flex items-center justify-center w-12 h-12 rounded-full border-4 border-slate-50 dark:border-dark-bg bg-gradient-to-br from-primary-400 to-primary-600 dark:from-primary-500 dark:to-primary-700 text-white shadow-lg shrink-0 md:order-1 md:group-odd:-translate-x-1/2 md:group-even:translate-x-1/2 relative z-10">
                    {slot.slot_type === 'attraction' ? <MapPin className="w-5 h-5" /> : 
                     slot.slot_type === 'breakfast' ? <span className="text-lg">🥐</span> : 
                     slot.slot_type === 'lunch' || slot.slot_type === 'dinner' ? <span className="text-lg">🍽️</span> : 
                     <Clock className="w-5 h-5" />}
                  </div>

                  {/* Card */}
                  <div className="w-[calc(100%-4rem)] md:w-[calc(50%-2.5rem)] rounded-2xl bg-white/80 dark:bg-dark-surface/80 backdrop-blur-md shadow-lg hover:shadow-xl border border-white/40 dark:border-white/10 transition-all duration-300 overflow-hidden group-hover:-translate-y-1">
                    {slot.slot_type === 'attraction' && slot.image_url && (
                      <div className="w-full h-48 relative overflow-hidden">
                        <img 
                          src={slot.image_url} 
                          alt={slot.attraction_name} 
                          className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                        />
                        <div className="absolute inset-0 bg-gradient-to-t from-slate-900/80 via-slate-900/30 to-transparent"></div>
                        <div className="absolute bottom-3 left-4 right-4 flex justify-between items-end">
                          <span className="text-xs font-bold text-white bg-white/20 backdrop-blur-md px-2 py-1 rounded-md border border-white/20">
                            {slot.category}
                          </span>
                          <span className="text-xs font-medium text-white bg-slate-900/60 backdrop-blur-md px-2 py-1 rounded-md">
                            {slot.duration_hours}h
                          </span>
                        </div>
                      </div>
                    )}
                    
                    <div className="p-5">
                      <div className="flex justify-between items-start mb-2">
                        <span className="text-sm font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-600 to-indigo-600 dark:from-primary-400 dark:to-indigo-400 bg-primary-50 dark:bg-primary-900/20 px-2 py-1 rounded">
                          {slot.time_label}
                        </span>
                        {slot.travel_time_mins > 0 && (
                          <span className="text-xs font-medium text-slate-500 flex items-center">
                            🚗 {slot.travel_time_mins}m commute
                          </span>
                        )}
                      </div>
                      
                      <h4 className="text-xl font-bold text-slate-900 dark:text-white mb-2 leading-tight">
                        {slot.slot_type === 'attraction' ? slot.attraction_name : slot.slot_type.charAt(0).toUpperCase() + slot.slot_type.slice(1)}
                      </h4>
                      
                      <p className="text-sm text-slate-600 dark:text-slate-300 mb-4 line-clamp-3">
                        {slot.description}
                      </p>

                      {slot.slot_type === 'attraction' && slot.recommendation_reason && (
                        <div className="mt-4 p-3 bg-gradient-to-br from-indigo-50 to-primary-50 dark:from-indigo-900/20 dark:to-primary-900/20 rounded-xl border border-indigo-100/50 dark:border-indigo-800/30 flex items-start">
                          <Brain className="w-4 h-4 text-indigo-500 mr-2 shrink-0 mt-0.5" />
                          <p className="text-xs text-indigo-900 dark:text-indigo-300">
                            <span className="font-semibold block mb-0.5 text-indigo-800 dark:text-indigo-200">Why this matches you:</span>
                            {slot.recommendation_reason}
                          </p>
                        </div>
                      )}
                      
                      {(slot.estimated_cost > 0 || slot.energy_level > 0) && (
                        <div className="mt-4 pt-4 border-t border-slate-100 dark:border-slate-800 flex items-center justify-between text-xs font-medium text-slate-500 dark:text-slate-400">
                          {slot.estimated_cost > 0 ? (
                            <div className="flex items-center">
                              <IndianRupee className="w-3.5 h-3.5 mr-1" />
                              Est: {slot.estimated_cost}
                            </div>
                          ) : (
                            <div className="flex items-center text-emerald-600 dark:text-emerald-400">
                              Free Entry
                            </div>
                          )}
                          {slot.energy_level > 0 && (
                            <div className="flex items-center">
                              <Zap className="w-3.5 h-3.5 mr-1 text-amber-500" />
                              Energy: {slot.energy_level}/5
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
            
          </div>

          {/* Sidebar / AI Explanations */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl shadow-xl border border-slate-100 dark:border-dark-border sticky top-24">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900/30 flex items-center justify-center mr-3">
                  <Brain className="w-5 h-5 text-primary-600 dark:text-primary-400" />
                </div>
                <h3 className="text-lg font-bold text-slate-900 dark:text-white">Why We Picked This</h3>
              </div>
              
              <p className="text-sm text-slate-600 dark:text-slate-400 mb-6 pb-6 border-b border-slate-100 dark:border-slate-800">
                This plan was crafted just for you. Here's a quick look at why these spots made the cut.
              </p>

              <div className="space-y-4 max-h-[400px] overflow-y-auto pr-2 custom-scrollbar">
                {Object.entries(itinerary.recommendations_explanation || {})
                  .filter(([_, reason]) => (reason as string).includes('Excellent') || (reason as string).includes('Warning'))
                  .slice(0, 5)
                  .map(([name, reason]: [string, any], idx) => (
                  <div key={idx} className="bg-slate-50 dark:bg-slate-800/50 p-3 rounded-xl border border-slate-100 dark:border-slate-700">
                    <p className="text-sm font-semibold text-slate-900 dark:text-white mb-1">{name}</p>
                    <p className="text-xs text-slate-500 dark:text-slate-400 leading-relaxed">{reason}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
};

export default ItineraryDetailsPage;

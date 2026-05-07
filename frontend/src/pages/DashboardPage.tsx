import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Calendar, MapPin, TrendingUp, Plus, Compass } from 'lucide-react';
import { motion } from 'framer-motion';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip as RechartsTooltip } from 'recharts';

interface ItineraryItem {
  id: number;
  city: string;
  num_days: int;
  title: string;
  total_estimated_cost: number;
  total_attractions: number;
  match_score: number;
  created_at: string;
}

interface Analytics {
  total_itineraries: number;
  popular_cities: Record<string, number>;
  avg_trip_duration: number;
}

const DashboardPage: React.FC = () => {
  const { user } = useAuth();
  const [itineraries, setItineraries] = useState<ItineraryItem[]>([]);
  const [analytics, setAnalytics] = useState<Analytics | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboardData = async () => {
      try {
        const [itinRes, analyticsRes] = await Promise.all([
          apiClient.get('/itineraries'),
          apiClient.get('/analytics')
        ]);
        setItineraries(itinRes.data);
        setAnalytics(analyticsRes.data);
      } catch (error) {
        console.error("Failed to load dashboard data", error);
      } finally {
        setLoading(false);
      }
    };

    fetchDashboardData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-50 dark:bg-dark-bg">
        <div className="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin"></div>
      </div>
    );
  }

  const cityData = analytics ? Object.entries(analytics.popular_cities).map(([name, value]) => ({ name, value })) : [];
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#6366f1', '#ec4899'];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-dark-bg py-8 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white dark:bg-dark-surface p-6 rounded-2xl border border-slate-100 dark:border-dark-border shadow-sm">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">Welcome back, {user?.full_name || user?.username}!</h1>
            <p className="text-slate-500 dark:text-slate-400 mt-1 flex items-center">
              Your Traveler Archetype: <span className="ml-2 px-2 py-0.5 rounded text-xs font-semibold bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400">{user?.archetype || 'Pending'}</span>
            </p>
          </div>
          <div className="flex gap-3">
            <Link to="/explore" className="btn-secondary flex items-center">
              <Compass className="w-4 h-4 mr-2" /> Explore
            </Link>
            <Link to="/plan" className="btn-primary flex items-center shadow-lg shadow-primary-500/20">
              <Plus className="w-4 h-4 mr-2" /> New Trip
            </Link>
          </div>
        </div>

        {/* Top Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <motion.div initial={{opacity: 0, y: 20}} animate={{opacity: 1, y: 0}} transition={{delay: 0.1}} className="bg-white dark:bg-dark-surface p-6 rounded-2xl border border-slate-100 dark:border-dark-border shadow-sm flex items-center">
            <div className="w-12 h-12 rounded-full bg-blue-100 dark:bg-blue-900/30 flex items-center justify-center mr-4">
              <Calendar className="w-6 h-6 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">My Itineraries</p>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white">{itineraries.length}</h3>
            </div>
          </motion.div>
          
          <motion.div initial={{opacity: 0, y: 20}} animate={{opacity: 1, y: 0}} transition={{delay: 0.2}} className="bg-white dark:bg-dark-surface p-6 rounded-2xl border border-slate-100 dark:border-dark-border shadow-sm flex items-center">
            <div className="w-12 h-12 rounded-full bg-green-100 dark:bg-green-900/30 flex items-center justify-center mr-4">
              <TrendingUp className="w-6 h-6 text-green-600 dark:text-green-400" />
            </div>
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">Avg Trip Length</p>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white">{analytics?.avg_trip_duration.toFixed(1)} days</h3>
            </div>
          </motion.div>

          <motion.div initial={{opacity: 0, y: 20}} animate={{opacity: 1, y: 0}} transition={{delay: 0.3}} className="bg-white dark:bg-dark-surface p-6 rounded-2xl border border-slate-100 dark:border-dark-border shadow-sm flex items-center">
            <div className="w-12 h-12 rounded-full bg-amber-100 dark:bg-amber-900/30 flex items-center justify-center mr-4">
              <MapPin className="w-6 h-6 text-amber-600 dark:text-amber-400" />
            </div>
            <div>
              <p className="text-sm text-slate-500 dark:text-slate-400 font-medium">Top Global City</p>
              <h3 className="text-2xl font-bold text-slate-900 dark:text-white truncate max-w-[120px]">
                {cityData.length > 0 ? cityData.sort((a,b)=>b.value-a.value)[0].name : '-'}
              </h3>
            </div>
          </motion.div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content: Itinerary List */}
          <div className="lg:col-span-2 space-y-6">
            <div className="flex justify-between items-center">
              <h2 className="text-xl font-bold text-slate-900 dark:text-white">Your Saved Trips</h2>
            </div>

            {itineraries.length === 0 ? (
              <div className="bg-white dark:bg-dark-surface border border-dashed border-slate-300 dark:border-slate-700 rounded-2xl p-12 text-center">
                <MapPin className="mx-auto h-12 w-12 text-slate-300 dark:text-slate-600 mb-4" />
                <h3 className="text-lg font-medium text-slate-900 dark:text-white mb-2">No trips planned yet</h3>
                <p className="text-slate-500 dark:text-slate-400 mb-6">Create your first AI-optimized itinerary today.</p>
                <Link to="/plan" className="btn-primary">Start Planning</Link>
              </div>
            ) : (
              <div className="space-y-4">
                {itineraries.map((itin, idx) => (
                  <motion.div 
                    key={itin.id}
                    initial={{opacity: 0, y: 20}} 
                    animate={{opacity: 1, y: 0}} 
                    transition={{delay: idx * 0.1}}
                  >
                    <Link to={`/itinerary/${itin.id}`} className="block bg-white dark:bg-dark-surface p-5 rounded-2xl border border-slate-100 dark:border-dark-border shadow-sm hover:shadow-md transition-all group">
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="text-lg font-bold text-slate-900 dark:text-white group-hover:text-primary-600 transition-colors">{itin.title}</h3>
                          <div className="flex items-center text-sm text-slate-500 dark:text-slate-400 mt-2 space-x-4">
                            <span className="flex items-center"><MapPin className="w-4 h-4 mr-1"/> {itin.city}</span>
                            <span className="flex items-center"><Calendar className="w-4 h-4 mr-1"/> {itin.num_days} Days</span>
                            <span className="flex items-center text-primary-600 dark:text-primary-400"><TrendingUp className="w-4 h-4 mr-1"/> {itin.match_score}% Match</span>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-sm font-medium text-slate-900 dark:text-white">₹{itin.total_estimated_cost.toLocaleString()}</p>
                          <p className="text-xs text-slate-500 mt-1">{itin.total_attractions} places</p>
                        </div>
                      </div>
                    </Link>
                  </motion.div>
                ))}
              </div>
            )}
          </div>

          {/* Sidebar: Analytics */}
          <div className="space-y-6">
            <div className="bg-white dark:bg-dark-surface p-6 rounded-2xl border border-slate-100 dark:border-dark-border shadow-sm">
              <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-6">Platform Popularity</h3>
              {cityData.length > 0 ? (
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={cityData}
                        cx="50%"
                        cy="50%"
                        innerRadius={60}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="value"
                      >
                        {cityData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip 
                        contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                      />
                    </PieChart>
                  </ResponsiveContainer>
                  <div className="flex flex-wrap justify-center gap-3 mt-4">
                    {cityData.map((entry, index) => (
                      <div key={entry.name} className="flex items-center text-sm">
                        <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: COLORS[index % COLORS.length] }}></div>
                        <span className="text-slate-600 dark:text-slate-400">{entry.name}</span>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-slate-500 text-center py-10">No data available yet</p>
              )}
            </div>
            
            {/* Quick Action Card */}
            <div className="bg-gradient-to-br from-primary-600 to-indigo-700 p-6 rounded-2xl shadow-lg text-white">
              <h3 className="text-lg font-bold mb-2">Want to refine your profile?</h3>
              <p className="text-primary-100 text-sm mb-4">You can retake the personality quiz anytime to update your travel archetype.</p>
              <Link to="/quiz" className="inline-block px-4 py-2 bg-white text-primary-700 text-sm font-semibold rounded-lg shadow hover:bg-slate-50 transition-colors">
                Retake Quiz
              </Link>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default DashboardPage;

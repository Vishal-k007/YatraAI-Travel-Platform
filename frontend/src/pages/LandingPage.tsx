import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { MapPin, Brain, Zap, Compass, ChevronRight } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const LandingPage: React.FC = () => {
  const { isAuthenticated } = useAuth();

  const fadeIn = {
    initial: { opacity: 0, y: 20 },
    animate: { opacity: 1, y: 0 },
    transition: { duration: 0.6 }
  };

  return (
    <div className="flex flex-col min-h-screen bg-slate-50 dark:bg-dark-bg">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 lg:pt-48 lg:pb-32 overflow-hidden">
        {/* Background gradient blob */}
        <div className="absolute top-0 right-0 -translate-y-12 translate-x-1/3">
          <div className="w-[600px] h-[600px] bg-amber-400/20 rounded-full blur-3xl"></div>
        </div>
        <div className="absolute bottom-0 left-0 translate-y-1/3 -translate-x-1/3">
          <div className="w-[500px] h-[500px] bg-rose-400/20 rounded-full blur-3xl"></div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center max-w-4xl mx-auto">
            <motion.div {...fadeIn}>
              <span className="inline-block py-1 px-3 rounded-full bg-amber-100 dark:bg-amber-900/30 text-amber-700 dark:text-amber-400 text-sm font-semibold tracking-wider mb-6">
                STRESS-FREE TRAVEL PLANNING
              </span>
              <h1 className="text-5xl lg:text-7xl font-bold tracking-tight text-slate-900 dark:text-white mb-8 leading-tight">
                Plan less. <br/> Experience more.
              </h1>
              <p className="text-xl text-slate-600 dark:text-slate-300 mb-10 max-w-2xl mx-auto leading-relaxed">
                We get to know your vibe and magically put together trips that feel just right for you. No stress, just good times.
              </p>
              
              <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
                <Link to={isAuthenticated ? "/plan" : "/register"} className="btn-primary text-lg px-8 py-4 w-full sm:w-auto flex items-center justify-center shadow-lg shadow-primary-500/30">
                  Let's Go <ChevronRight className="ml-2 w-5 h-5" />
                </Link>
                <Link to="/explore" className="btn-secondary text-lg px-8 py-4 w-full sm:w-auto flex items-center justify-center">
                  Look Around
                </Link>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white dark:bg-dark-surface border-t border-slate-100 dark:border-dark-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">How we keep it chill</h2>
            <p className="text-slate-600 dark:text-slate-400 max-w-2xl mx-auto">We do all the heavy lifting behind the scenes so you don't have to. Here's how we make your trip perfect.</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {[
              {
                icon: <Brain className="w-8 h-8 text-indigo-500" />,
                title: "Getting to Know You",
                desc: "We learn what makes you tick so we can suggest things you'll actually enjoy."
              },
              {
                icon: <MapPin className="w-8 h-8 text-amber-500" />,
                title: "Curated Spots",
                desc: "We know all the best spots, from quiet hidden gems to the main attractions."
              },
              {
                icon: <Zap className="w-8 h-8 text-orange-500" />,
                title: "Vibe Matching",
                desc: "Our smart matching ensures you only see places that fit your exact mood."
              },
              {
                icon: <Compass className="w-8 h-8 text-rose-500" />,
                title: "Easy Routing",
                desc: "We map it all out so you can just enjoy the ride, without burning out."
              }
            ].map((feature, idx) => (
              <motion.div 
                key={idx}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: idx * 0.1 }}
                className="p-6 rounded-2xl bg-slate-50 dark:bg-slate-800/50 border border-slate-100 dark:border-slate-700 hover:shadow-xl transition-all duration-300"
              >
                <div className="w-14 h-14 rounded-xl bg-white dark:bg-slate-800 shadow-sm flex items-center justify-center mb-6">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-slate-900 dark:text-white mb-3">{feature.title}</h3>
                <p className="text-slate-600 dark:text-slate-400 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Destinations Preview */}
      <section className="py-24 relative overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-end mb-12">
            <div>
              <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Where to next?</h2>
              <p className="text-slate-600 dark:text-slate-400">Check out our favorite spots to escape to right now.</p>
            </div>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                name: "Goa",
                image: "https://images.unsplash.com/photo-1512343879784-a960bf40e7f2?auto=format&fit=crop&q=80&w=1000",
                tags: ["Beaches", "Nightlife", "Heritage"]
              },
              {
                name: "Jaipur",
                image: "https://images.unsplash.com/photo-1477587458883-47145ed94245?auto=format&fit=crop&q=80&w=1000",
                tags: ["Culture", "Architecture", "Shopping"]
              },
              {
                name: "Manali",
                image: "https://images.unsplash.com/photo-1605640840605-14ac1855827b?auto=format&fit=crop&q=80&w=1000",
                tags: ["Mountains", "Adventure", "Nature"]
              }
            ].map((dest, idx) => (
              <motion.div 
                key={idx}
                whileHover={{ y: -10 }}
                className="group cursor-pointer rounded-2xl overflow-hidden shadow-lg relative aspect-[4/5]"
              >
                <img src={dest.image} alt={dest.name} className="absolute inset-0 w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" />
                <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent"></div>
                <div className="absolute bottom-0 left-0 p-8">
                  <h3 className="text-3xl font-bold text-white mb-3">{dest.name}</h3>
                  <div className="flex gap-2">
                    {dest.tags.map(tag => (
                      <span key={tag} className="px-3 py-1 bg-white/20 backdrop-blur-md rounded-full text-xs font-medium text-white">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>
    </div>
  );
};

export default LandingPage;

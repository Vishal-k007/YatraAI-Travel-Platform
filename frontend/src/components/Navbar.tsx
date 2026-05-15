import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Palmtree, User as UserIcon, LogOut, Compass } from 'lucide-react';

const Navbar: React.FC = () => {
  const { isAuthenticated, user, logout } = useAuth();

  return (
    <nav className="sticky top-0 z-50 bg-white/80 dark:bg-dark-bg/80 backdrop-blur-md border-b border-slate-200 dark:border-dark-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-8 h-8 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg flex items-center justify-center shadow-md shadow-orange-500/20">
                <Palmtree className="h-5 w-5 text-white" />
              </div>
              <span className="font-display font-bold text-xl tracking-tight text-slate-900 dark:text-white">
                YatraAI
              </span>
            </Link>
          </div>

          <div className="flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                <Link to="/explore" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-500 font-medium text-sm flex items-center">
                  <Compass className="w-4 h-4 mr-1" /> Explore
                </Link>
                <Link to="/plan" className="btn-primary py-1.5 text-sm">
                  Plan Trip
                </Link>
                <div className="relative group ml-2">
                  <button className="flex items-center space-x-2 text-slate-700 dark:text-slate-200 hover:text-primary-600">
                    <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-700 flex items-center justify-center">
                      <UserIcon className="w-4 h-4" />
                    </div>
                  </button>
                  <div className="absolute right-0 w-48 mt-2 py-2 bg-white dark:bg-dark-surface rounded-xl shadow-xl border border-slate-100 dark:border-dark-border opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200">
                    <div className="px-4 py-2 border-b border-slate-100 dark:border-slate-700">
                      <p className="text-sm font-medium text-slate-900 dark:text-white truncate">{user?.username}</p>
                      <p className="text-xs text-slate-500 truncate">{user?.email}</p>
                    </div>
                    <Link to="/dashboard" className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800">
                      Dashboard
                    </Link>
                    <Link to="/quiz" className="block px-4 py-2 text-sm text-slate-700 dark:text-slate-300 hover:bg-slate-50 dark:hover:bg-slate-800">
                      Personality Profile
                    </Link>
                    <button 
                      onClick={logout}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 flex items-center"
                    >
                      <LogOut className="w-4 h-4 mr-2" /> Sign out
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <>
                <Link to="/login" className="text-slate-600 dark:text-slate-300 hover:text-primary-600 dark:hover:text-primary-500 font-medium text-sm">
                  Log in
                </Link>
                <Link to="/register" className="btn-primary py-1.5 text-sm">
                  Sign up
                </Link>
              </>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;

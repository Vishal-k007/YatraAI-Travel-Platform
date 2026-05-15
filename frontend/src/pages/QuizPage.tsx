import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowRight, ArrowLeft, Brain, CheckCircle2 } from 'lucide-react';
import apiClient from '../api/client';
import { useAuth } from '../context/AuthContext';

const QUESTIONS = [
  { id: 'travel_pace', text: 'How do you prefer to pace your travel?', left: 'Slow & relaxed', right: 'Fast & packed' },
  { id: 'budget_per_day', text: 'What is your typical budget style?', left: 'Strict budget', right: 'Luxury all the way' },
  { id: 'crowd_tolerance', text: 'How do you feel about crowded tourist spots?', left: 'Avoid at all costs', right: 'Love the energy' },
  { id: 'food_adventurousness', text: 'When it comes to local food...', left: 'Familiar & safe', right: 'Try anything once' },
  { id: 'cultural_curiosity', text: 'How interested are you in history and culture?', left: 'Just the highlights', right: 'Deep immersion' },
  { id: 'adventure_appetite', text: 'What is your appetite for adventure/thrill?', left: 'Zero thrill', right: 'Extreme adrenaline' },
  { id: 'climate_tolerance', text: 'How sensitive are you to extreme weather?', left: 'Very sensitive', right: 'Weather doesn\'t matter' },
  { id: 'photography_interest', text: 'How important is photography to you?', left: 'Live in the moment', right: 'Must capture everything' },
  { id: 'nightlife_interest', text: 'How do you spend your evenings?', left: 'Early to bed', right: 'Partying till dawn' },
  { id: 'relaxation_preference', text: 'Do you travel to rest or to stay active?', left: 'Constant activity', right: 'Pure relaxation' },
  { id: 'luxury_preference', text: 'Comfort level preference?', left: 'Basic is fine', right: '5-star comfort' },
  { id: 'social_preference', text: 'How do you interact with others?', left: 'Keep to myself', right: 'Make new friends' },
  { id: 'planning_spontaneity', text: 'How do you plan your days?', left: 'Strict itinerary', right: 'Go with the flow' },
  { id: 'walking_tolerance', text: 'How much walking can you handle?', left: 'Prefer cabs', right: 'Walk everywhere' },
  { id: 'local_experience', text: 'What type of spots do you prefer?', left: 'Famous landmarks', right: 'Hidden local gems' },
];

const QuizPage: React.FC = () => {
  const [currentStep, setCurrentStep] = useState(0);
  const [answers, setAnswers] = useState<Record<string, number>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState<any>(null);
  const navigate = useNavigate();
  const { updateUser, user } = useAuth();

  const handleSelect = (value: number) => {
    setAnswers({ ...answers, [QUESTIONS[currentStep].id]: value });
    
    // Auto advance after small delay
    if (currentStep < QUESTIONS.length - 1) {
      setTimeout(() => setCurrentStep(prev => prev + 1), 300);
    }
  };

  const handleSubmit = async () => {
    // Fill missing answers with default 3 (neutral)
    const finalAnswers = { ...answers };
    QUESTIONS.forEach(q => {
      if (finalAnswers[q.id] === undefined) {
        finalAnswers[q.id] = 3;
      }
    });

    setIsSubmitting(true);
    try {
      const response = await apiClient.post('/profile/quiz', finalAnswers);
      setResult(response.data);
      
      // Update global user state
      if (user) {
        updateUser({
          ...user,
          has_profile: true,
          archetype: response.data.archetype
        });
      }
    } catch (error) {
      console.error('Failed to submit quiz:', error);
      alert('Error analyzing profile. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const currentQ = QUESTIONS[currentStep];

  if (result) {
    return (
      <div className="min-h-screen bg-slate-50 dark:bg-dark-bg py-12 px-4 sm:px-6 lg:px-8 flex items-center justify-center">
        <motion.div 
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          className="max-w-2xl w-full glass-panel p-10 text-center"
        >
          <div className="mx-auto w-20 h-20 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center mb-6">
            <Brain className="h-10 w-10 text-primary-600 dark:text-primary-400" />
          </div>
          <h2 className="text-3xl font-bold text-slate-900 dark:text-white mb-2">Vibe Check Complete!</h2>
          <p className="text-lg text-slate-600 dark:text-slate-400 mb-8">We've got a good feel for your travel style.</p>
          
          <div className="bg-white dark:bg-slate-800 rounded-2xl p-8 shadow-inner mb-8 border border-slate-100 dark:border-slate-700">
            <h3 className="text-sm font-semibold tracking-wider text-primary-600 uppercase mb-2">Your Travel Vibe</h3>
            <div className="text-4xl font-display font-bold text-slate-900 dark:text-white mb-4">
              {result.archetype}
            </div>
            <p className="text-slate-600 dark:text-slate-300 leading-relaxed text-lg">
              {result.archetype_explanation}
            </p>
          </div>

          <button 
            onClick={() => navigate('/dashboard')}
            className="btn-primary py-4 px-8 text-lg w-full sm:w-auto flex items-center justify-center mx-auto"
          >
            Go to Dashboard <ArrowRight className="ml-2 w-5 h-5" />
          </button>
        </motion.div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-dark-bg py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-3xl font-bold text-slate-900 dark:text-white mb-4">Travel Vibe Check</h1>
          <p className="text-slate-600 dark:text-slate-400">Just {QUESTIONS.length} quick questions to help us match you with the perfect spots.</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8 relative pt-1">
          <div className="flex mb-2 items-center justify-between">
            <div>
              <span className="text-xs font-semibold inline-block py-1 px-2 uppercase rounded-full text-primary-600 bg-primary-100 dark:bg-primary-900/30">
                Question {currentStep + 1} of {QUESTIONS.length}
              </span>
            </div>
            <div className="text-right">
              <span className="text-xs font-semibold inline-block text-primary-600">
                {Math.round(((currentStep + 1) / QUESTIONS.length) * 100)}%
              </span>
            </div>
          </div>
          <div className="overflow-hidden h-2 mb-4 text-xs flex rounded-full bg-slate-200 dark:bg-slate-700">
            <motion.div 
              initial={{ width: 0 }}
              animate={{ width: `${((currentStep + 1) / QUESTIONS.length) * 100}%` }}
              className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary-500"
            ></motion.div>
          </div>
        </div>

        {/* Question Card */}
        <div className="glass-panel p-8 md:p-12 min-h-[400px] flex flex-col justify-center relative overflow-hidden">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentStep}
              initial={{ x: 50, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -50, opacity: 0 }}
              transition={{ duration: 0.3 }}
            >
              <h2 className="text-2xl md:text-3xl font-display font-medium text-center text-slate-900 dark:text-white mb-12">
                {currentQ.text}
              </h2>

              {/* Slider / Buttons */}
              <div className="flex flex-col space-y-6">
                <div className="flex justify-between text-sm font-medium text-slate-500 dark:text-slate-400 px-2">
                  <span>{currentQ.left}</span>
                  <span>{currentQ.right}</span>
                </div>
                
                <div className="grid grid-cols-5 gap-2 md:gap-4">
                  {[1, 2, 3, 4, 5].map((val) => {
                    const isSelected = answers[currentQ.id] === val;
                    return (
                      <button
                        key={val}
                        onClick={() => handleSelect(val)}
                        className={`
                          h-16 rounded-xl transition-all duration-200 flex items-center justify-center text-lg font-semibold
                          ${isSelected 
                            ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30 scale-105' 
                            : 'bg-white dark:bg-slate-800 text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-700 hover:border-primary-400 hover:bg-slate-50 dark:hover:bg-slate-700'}
                        `}
                      >
                        {isSelected ? <CheckCircle2 className="w-6 h-6" /> : val}
                      </button>
                    )
                  })}
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>

        {/* Navigation */}
        <div className="mt-8 flex justify-between items-center">
          <button
            onClick={() => setCurrentStep(prev => Math.max(0, prev - 1))}
            disabled={currentStep === 0 || isSubmitting}
            className="flex items-center px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white disabled:opacity-50 transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-2" /> Back
          </button>

          {currentStep === QUESTIONS.length - 1 ? (
            <button
              onClick={handleSubmit}
              disabled={isSubmitting || Object.keys(answers).length < QUESTIONS.length}
              className="btn-primary flex items-center px-8"
            >
              {isSubmitting ? 'Analyzing...' : 'Find My Vibe'}
              {!isSubmitting && <Brain className="w-4 h-4 ml-2" />}
            </button>
          ) : (
            <button
              onClick={() => setCurrentStep(prev => Math.min(QUESTIONS.length - 1, prev + 1))}
              className="flex items-center px-4 py-2 text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white transition-colors"
            >
              Skip <ArrowRight className="w-4 h-4 ml-2" />
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default QuizPage;

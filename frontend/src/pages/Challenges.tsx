import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { SparklesIcon } from '@heroicons/react/24/outline';
import { challengeService } from '../services/api';
import { Challenge } from '../types';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import GenerateChallengeModal from '../components/GenerateChallengeModal';

const Challenges: React.FC = () => {
  const [challenges, setChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [selectedDifficulty, setSelectedDifficulty] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [showGenerateModal, setShowGenerateModal] = useState(false);

  useEffect(() => {
    fetchChallenges();
  }, [selectedCategory, selectedDifficulty]);

  const fetchChallenges = async () => {
    try {
      setLoading(true);
      const params: any = { limit: 100 };

      if (selectedDifficulty !== 'all') {
        params.difficulty = selectedDifficulty;
      }

      const data = await challengeService.getChallenges(params);
      setChallenges(data);
    } catch (error) {
      console.error('Error fetching challenges:', error);
    } finally {
      setLoading(false);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors = {
      beginner: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
      easy: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
      medium: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200',
      hard: 'bg-orange-100 text-orange-800 dark:bg-orange-900 dark:text-orange-200',
      expert: 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200',
    };
    return colors[difficulty as keyof typeof colors] || colors.medium;
  };

  const filteredChallenges = challenges.filter((challenge) => {
    const matchesSearch = challenge.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         challenge.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesSearch;
  });

  const groupedByCategory = filteredChallenges.reduce((acc, challenge) => {
    const categoryId = challenge.category_id || 0;
    if (!acc[categoryId]) {
      acc[categoryId] = [];
    }
    acc[categoryId].push(challenge);
    return acc;
  }, {} as Record<number, Challenge[]>);

  const categoryNames: Record<number, string> = {
    1: 'Cryptography',
    2: 'Web Security',
    3: 'Forensics',
    4: 'Network Security',
    5: 'Binary Exploitation',
    6: 'Reverse Engineering',
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <LoadingSpinner />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          Challenges
        </h1>
        <motion.button
          whileHover={{ scale: 1.03 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => setShowGenerateModal(true)}
          className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-semibold text-white
                     bg-gradient-to-r from-primary-600 to-purple-600
                     hover:from-primary-700 hover:to-purple-700 transition-all shadow-md"
        >
          <SparklesIcon className="h-4 w-4" />
          Generate with AI
        </motion.button>
      </div>

      <GenerateChallengeModal
        isOpen={showGenerateModal}
        onClose={() => setShowGenerateModal(false)}
        onGenerated={(challenge) => {
          // Prepend the new challenge so it appears at the top
          setChallenges((prev) => [challenge as any, ...prev]);
          setShowGenerateModal(false);
        }}
      />

      {/* Filters */}
      <div className="card">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {/* Search */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Search
            </label>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search challenges..."
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          {/* Difficulty Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Difficulty
            </label>
            <select
              value={selectedDifficulty}
              onChange={(e) => setSelectedDifficulty(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Difficulties</option>
              <option value="beginner">Beginner</option>
              <option value="easy">Easy</option>
              <option value="medium">Medium</option>
              <option value="hard">Hard</option>
              <option value="expert">Expert</option>
            </select>
          </div>

          {/* Category Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Category
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                       bg-white dark:bg-gray-800 text-gray-900 dark:text-white
                       focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="all">All Categories</option>
              <option value="1">Cryptography</option>
              <option value="2">Web Security</option>
              <option value="3">Forensics</option>
              <option value="4">Network Security</option>
              <option value="5">Binary Exploitation</option>
              <option value="6">Reverse Engineering</option>
            </select>
          </div>
        </div>
      </div>

      {/* Challenges by Category */}
      {Object.entries(groupedByCategory).map(([categoryId, categoryChalls]) => {
        if (selectedCategory !== 'all' && selectedCategory !== categoryId) {
          return null;
        }

        return (
          <div key={categoryId} className="space-y-4">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              {categoryNames[parseInt(categoryId)] || 'Other'}
            </h2>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {categoryChalls.map((challenge) => (
                <motion.div
                  key={challenge.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                >
                  <Link to={`/challenges/${challenge.id}`}>
                    <div className="card hover:shadow-lg transition-shadow duration-200 h-full">
                      {/* Header */}
                      <div className="flex items-start justify-between mb-3">
                        <h3 className="text-lg font-semibold text-gray-900 dark:text-white flex-1">
                          {challenge.title}
                        </h3>
                        <span
                          className={`px-2 py-1 text-xs font-medium rounded-full ${getDifficultyColor(
                            challenge.difficulty
                          )}`}
                        >
                          {challenge.difficulty}
                        </span>
                      </div>

                      {/* Description */}
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
                        {challenge.description}
                      </p>

                      {/* Stats */}
                      <div className="flex items-center justify-between text-sm">
                        <div className="flex items-center space-x-4">
                          <span className="text-primary-600 dark:text-primary-400 font-semibold">
                            {challenge.points} pts
                          </span>
                          <span className="text-gray-500 dark:text-gray-400">
                            {challenge.solve_count} solves
                          </span>
                        </div>
                      </div>

                      {/* Tags */}
                      {challenge.tags && challenge.tags.length > 0 && (
                        <div className="flex flex-wrap gap-2 mt-3">
                          {challenge.tags.slice(0, 3).map((tag, index) => (
                            <span
                              key={index}
                              className="px-2 py-1 text-xs bg-gray-100 dark:bg-gray-700
                                       text-gray-600 dark:text-gray-300 rounded"
                            >
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        );
      })}

      {/* No results */}
      {filteredChallenges.length === 0 && (
        <div className="card text-center py-12">
          <p className="text-gray-600 dark:text-gray-400">
            No challenges found matching your criteria.
          </p>
        </div>
      )}
    </div>
  );
};

export default Challenges;

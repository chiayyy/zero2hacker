import React, { useState } from 'react';

interface Props {
  onGenerate: (params: { category: string; difficulty: string; learning_goal: string }) => void;
  loading?: boolean;
}

const categories = [
  { value: 'crypto', label: 'Crypto' },
  { value: 'web', label: 'Web' },
  { value: 'forensics', label: 'Forensics' },
  { value: 'reverse engineering', label: 'Reverse Engineering' },
  { value: 'mixed', label: 'Mixed' },
];

const difficulties = [
  { value: 'beginner', label: 'Beginner' },
  { value: 'easy', label: 'Easy' },
  { value: 'medium', label: 'Medium' },
  { value: 'hard', label: 'Hard' },
];

const learningGoals = [
  'Learn Caesar cipher',
  'Learn base64 decoding',
  'Learn SQL injection basics',
  'Learn steganography',
];

const ChallengeGeneratorForm: React.FC<Props> = ({ onGenerate, loading }) => {
  const [category, setCategory] = useState<string>('mixed');
  const [difficulty, setDifficulty] = useState<string>('beginner');
  const [learningGoal, setLearningGoal] = useState<string>(learningGoals[0]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onGenerate({
      category,
      difficulty,
      learning_goal: learningGoal,
    });
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Category
          </label>
          <select
            value={category}
            onChange={(e) => setCategory(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-dark-800 py-2 px-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          >
            {categories.map((cat) => (
              <option key={cat.value} value={cat.value}>
                {cat.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Difficulty
          </label>
          <select
            value={difficulty}
            onChange={(e) => setDifficulty(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-dark-800 py-2 px-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          >
            {difficulties.map((diff) => (
              <option key={diff.value} value={diff.value}>
                {diff.label}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
            Learning Goal
          </label>
          <select
            value={learningGoal}
            onChange={(e) => setLearningGoal(e.target.value)}
            className="mt-1 block w-full rounded-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-dark-800 py-2 px-3 shadow-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 text-sm"
          >
            {learningGoals.map((goal) => (
              <option key={goal} value={goal}>
                {goal}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="flex items-center justify-between">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          Zero will look at your progress, find your weak spots, and craft a challenge that teaches this concept step by step.
        </p>
        <button
          type="submit"
          disabled={loading}
          className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50"
        >
          {loading ? 'Generating...' : 'Generate Challenge'}
        </button>
      </div>
    </form>
  );
};

export default ChallengeGeneratorForm;



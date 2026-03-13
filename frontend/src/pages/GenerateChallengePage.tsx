import React, { useEffect, useState } from 'react';
import toast from 'react-hot-toast';
import { aiService } from '../services/api';
import { Challenge } from '../types';
import ChallengeGeneratorForm from '../components/ChallengeGeneratorForm';
import GeneratedChallengeCard from '../components/GeneratedChallengeCard';
import LoadingSpinner from '../components/ui/LoadingSpinner';

const GenerateChallengePage: React.FC = () => {
  const [generatedChallenge, setGeneratedChallenge] = useState<Challenge | null>(null);
  const [myChallenges, setMyChallenges] = useState<Challenge[]>([]);
  const [loading, setLoading] = useState(false);
  const [loadingList, setLoadingList] = useState(false);

  const loadMyChallenges = async () => {
    try {
      setLoadingList(true);
      const challenges = await aiService.getGeneratedChallenges();
      setMyChallenges(challenges);
    } catch (error) {
      console.error('Failed to load generated challenges', error);
    } finally {
      setLoadingList(false);
    }
  };

  useEffect(() => {
    loadMyChallenges();
  }, []);

  const handleGenerate = async (params: {
    category: string;
    difficulty: string;
    learning_goal: string;
  }) => {
    try {
      setLoading(true);
      const challenge = await aiService.generatePersonalizedChallenge(params);
      setGeneratedChallenge(challenge);
      toast.success('New AI-generated challenge is ready. Let\'s hack!');
      // Refresh library list
      await loadMyChallenges();
    } catch (error: any) {
      console.error('Failed to generate challenge', error);
      const rawDetail = error?.response?.data?.detail;
      let detail: string;

      if (Array.isArray(rawDetail)) {
        detail = rawDetail
          .map((d: any) => d?.msg || d?.detail || JSON.stringify(d))
          .join(' | ');
      } else if (typeof rawDetail === 'object' && rawDetail !== null) {
        detail = rawDetail.msg || rawDetail.detail || JSON.stringify(rawDetail);
      } else if (typeof rawDetail === 'string') {
        detail = rawDetail;
      } else {
        detail = error?.message || 'Check your connection and try again.';
      }

      toast.error(`Couldn't generate a challenge: ${detail}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
            AI Challenge Generator
          </h1>
          <p className="mt-2 text-gray-600 dark:text-gray-400 max-w-2xl">
            Let Zero craft a new cybersecurity challenge just for you, based on your skill level and learning goals. 🔐
          </p>
        </div>
      </div>

      <div className="card">
        <ChallengeGeneratorForm onGenerate={handleGenerate} loading={loading} />
        {loading && (
          <div className="mt-6 flex items-center space-x-3 text-sm text-gray-600 dark:text-gray-400">
            <LoadingSpinner size="sm" />
            <span>Zero is crafting a personalized CTF for you…</span>
          </div>
        )}
      </div>

      {generatedChallenge && (
        <div className="space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            Latest Generated Challenge
          </h2>
          <GeneratedChallengeCard challenge={generatedChallenge} highlight />
        </div>
      )}

      <div className="space-y-4">
        <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
          My Generated Challenges
        </h2>
        {loadingList ? (
          <div className="flex items-center justify-center py-8">
            <LoadingSpinner />
          </div>
        ) : myChallenges.length === 0 ? (
          <p className="text-gray-600 dark:text-gray-400">
            No AI-generated challenges yet. Generate your first one above and it’ll show up here.
          </p>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
            {myChallenges.map((ch) => (
              <GeneratedChallengeCard key={ch.id} challenge={ch} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default GenerateChallengePage;



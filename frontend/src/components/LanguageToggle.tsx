import React from 'react';
import { motion } from 'framer-motion';
import { useLanguage } from '../contexts/LanguageContext';

const LanguageToggle: React.FC = () => {
  const { language, setLanguage } = useLanguage();

  return (
    <motion.button
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      onClick={() => setLanguage(language === 'en' ? 'zh' : 'en')}
      className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-xs font-medium text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-dark-700 transition-colors duration-200"
      title="Switch language / 切换语言"
    >
      <span className="text-base leading-none">{language === 'en' ? '🇨🇳' : '🇬🇧'}</span>
      <span>{language === 'en' ? '中文' : 'EN'}</span>
    </motion.button>
  );
};

export default LanguageToggle;

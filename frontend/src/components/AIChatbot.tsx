import React, { useState, useEffect, useRef, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import { useLanguage } from '../contexts/LanguageContext';

interface Message {
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: Date;
  type?: string;
}

interface AIChatbotProps {
  challengeId?: number;
  onChallengeStart?: () => void;
}

interface ProactiveTip {
  tip: string;
  challenge_hint?: string;
  show: boolean;
}

// Encouraging messages for the kind lecturer
const lecturerMessages = {
  en: {
    welcome: [
      "Welcome! I'm your friendly learning guide. Feel free to ask me anything about cybersecurity!",
      "Hello there! Ready to learn something new today? I'm here to help you every step of the way!",
      "Hi! Think of me as your personal tutor. No question is too simple - let's learn together!"
    ],
    encouragement: [
      "You're doing great! Every expert was once a beginner.",
      "Don't worry if it seems hard at first - that's how learning works!",
      "I believe in you! Take your time and ask if you need help.",
      "Remember: making mistakes is part of learning. Keep going!"
    ],
    checkIn: [
      "How's it going? Need any help with the challenge?",
      "I'm here if you need guidance! Don't hesitate to ask.",
      "Taking a moment to check in - everything making sense so far?",
      "Remember, I'm just a click away if you get stuck!"
    ],
    stuck: [
      "It looks like you might be stuck. Would you like a gentle hint?",
      "No worries if this is challenging - that means you're learning! Need some guidance?",
      "This is a tricky one! Want me to explain the concept behind it?"
    ]
  },
  zh: {
    welcome: [
      "欢迎！我是你的学习向导。有任何关于网络安全的问题都可以问我！",
      "你好！准备好学习新知识了吗？我会陪伴你的每一步！",
      "嗨！把我当作你的私人导师。没有问题是太简单的 - 让我们一起学习！"
    ],
    encouragement: [
      "你做得很棒！每个专家都曾是初学者。",
      "如果一开始觉得难，不要担心 - 这就是学习的过程！",
      "我相信你！慢慢来，有问题随时问。",
      "记住：犯错是学习的一部分。继续加油！"
    ],
    checkIn: [
      "进展如何？需要帮助吗？",
      "有问题随时问我！不要犹豫。",
      "来看看你 - 到目前为止都理解了吗？",
      "记住，如果你卡住了，我就在这里！"
    ],
    stuck: [
      "看起来你可能遇到困难了。需要一点提示吗？",
      "这道题确实有挑战性 - 这意味着你在学习！需要一些指导吗？",
      "这是个难题！要我解释一下背后的概念吗？"
    ]
  }
};

const AIChatbot: React.FC<AIChatbotProps> = ({ challengeId, onChallengeStart }) => {
  const { user } = useAuth();
  const { language, t } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [aiAvailable, setAiAvailable] = useState(true);
  const [proactiveTip, setProactiveTip] = useState<ProactiveTip>({ tip: '', show: false });
  const [hintLevel, setHintLevel] = useState(1);
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [showWelcomePopup, setShowWelcomePopup] = useState(false);
  const [hasShownWelcome, setHasShownWelcome] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const tipTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const checkInTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Helper to get random message from array
  const getRandomMessage = (messages: string[]) => {
    return messages[Math.floor(Math.random() * messages.length)];
  };

  // Get lecturer messages based on current language
  const getLecturerMessages = () => {
    return language === 'zh' ? lecturerMessages.zh : lecturerMessages.en;
  };

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Focus input when chatbot opens
  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  // Show welcome popup after 5 seconds for new users
  useEffect(() => {
    const hasSeenWelcome = localStorage.getItem('z2h_welcome_shown');

    if (!hasSeenWelcome && !hasShownWelcome && !isOpen) {
      const welcomeTimer = setTimeout(() => {
        setShowWelcomePopup(true);
        setHasShownWelcome(true);
        localStorage.setItem('z2h_welcome_shown', 'true');
      }, 5000); // Show after 5 seconds

      return () => clearTimeout(welcomeTimer);
    }
  }, [hasShownWelcome, isOpen]);

  // Periodic check-in popup every 3 minutes when on a challenge
  useEffect(() => {
    if (challengeId && !isOpen) {
      checkInTimeoutRef.current = setTimeout(() => {
        const msgs = getLecturerMessages();
        setProactiveTip({
          tip: getRandomMessage(msgs.checkIn),
          show: true
        });
      }, 180000); // 3 minutes

      return () => {
        if (checkInTimeoutRef.current) {
          clearTimeout(checkInTimeoutRef.current);
        }
      };
    }
  }, [challengeId, isOpen, language]);

  // Check AI availability and add welcome message when chatbot opens
  useEffect(() => {
    if (isOpen && messages.length === 0) {
      checkAIAvailability();
    }
  }, [isOpen]);

  // Show proactive tip after user spends time on challenge
  useEffect(() => {
    if (challengeId && !isOpen) {
      // Show a helpful tip after 2 minutes on a challenge
      tipTimeoutRef.current = setTimeout(() => {
        showProactiveTip('stuck_long_time');
      }, 120000); // 2 minutes

      return () => {
        if (tipTimeoutRef.current) {
          clearTimeout(tipTimeoutRef.current);
        }
      };
    }
  }, [challengeId]);

  const showProactiveTip = async (context: string) => {
    try {
      const response = await api.post('/ai/proactive-tip', {
        context,
        challenge_id: challengeId
      });

      if (response.data.tip) {
        setProactiveTip({
          tip: response.data.tip,
          challenge_hint: response.data.challenge_hint,
          show: true
        });

        // Auto-hide after 10 seconds
        setTimeout(() => {
          setProactiveTip(prev => ({ ...prev, show: false }));
        }, 10000);
      }
    } catch (error) {
      console.log('Proactive tip unavailable');
    }
  };

  const dismissTip = () => {
    setProactiveTip(prev => ({ ...prev, show: false }));
  };

  const openChatWithTip = () => {
    setIsOpen(true);
    if (proactiveTip.challenge_hint) {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: `💡 ${proactiveTip.tip}\n\nHere's a hint to help you:\n${proactiveTip.challenge_hint}`,
        timestamp: new Date(),
        type: 'hint'
      }]);
    }
    dismissTip();
  };

  const checkAIAvailability = async () => {
    const msgs = getLecturerMessages();
    const welcomeMsg = getRandomMessage(msgs.welcome);
    const encourageMsg = getRandomMessage(msgs.encouragement);

    try {
      await api.get('/ai/models/status');
      setAiAvailable(true);
      setMessages([
        {
          role: 'assistant',
          content: language === 'zh'
            ? `${welcomeMsg}\n\n${user?.display_name ? `${user.display_name}，` : ''}${encourageMsg}\n\n我可以帮助你：\n• 解释网络安全概念\n• 提供循序渐进的提示\n• 指导你完成挑战\n• 生成适合你水平的练习\n\n有什么想学的吗？`
            : `${welcomeMsg}\n\n${user?.display_name ? `${user.display_name}, ` : ''}${encourageMsg}\n\nI can help you with:\n• Explaining cybersecurity concepts\n• Providing step-by-step hints\n• Guiding you through challenges\n• Generating practice exercises for your level\n\nWhat would you like to learn?`,
          timestamp: new Date(),
        },
      ]);
    } catch (error) {
      setAiAvailable(false);
      setMessages([
        {
          role: 'system',
          content: language === 'zh'
            ? `${welcomeMsg}\n\n⚠️ AI引擎目前离线，但我仍然可以用内置知识帮助你！\n\n${encourageMsg}\n\n你可以：\n• 浏览和尝试所有挑战\n• 使用内置提示系统\n• 问我基础概念问题\n• 查看学习目标`
            : `${welcomeMsg}\n\n⚠️ The AI engine is offline, but I can still help with built-in knowledge!\n\n${encourageMsg}\n\nYou can:\n• Browse and attempt all challenges\n• Use the built-in hint system\n• Ask me about basic concepts\n• View learning objectives`,
          timestamp: new Date(),
        },
      ]);
    }
  };

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!inputMessage.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInput = inputMessage;
    setInputMessage('');
    setIsLoading(true);

    // Check if user is asking for a personalized challenge
    const isAskingForChallenge = /generate|create|make|give me.*challenge|personalized|custom/i.test(currentInput);

    try {
      if (!aiAvailable) {
        // Provide helpful fallback responses when AI is unavailable
        const fallbackResponse = getFallbackResponse(currentInput, language);
        const assistantMessage: Message = {
          role: 'assistant',
          content: fallbackResponse,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else if (isAskingForChallenge) {
        // Handle challenge generation request
        const assistantMessage: Message = {
          role: 'assistant',
          content: language === 'zh'
            ? `好的！我会根据你的技能水平（${user?.skill_level || '初学者'}）为你生成一个个性化挑战。请稍等...\n\n你想要什么类型的挑战？\n• 密码学\n• Web安全\n• 网络安全\n• 隐写术\n• 取证\n\n请告诉我你感兴趣的类型和难度偏好！`
            : `Great! I'll generate a personalized challenge for you based on your skill level (${user?.skill_level || 'beginner'}). Let me work on that...\n\nWhat type of challenge would you like?\n• Cryptography\n• Web Security\n• Network Security\n• Steganography\n• Forensics\n\nTell me the type and your difficulty preference!`,
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Regular AI chat - now always works with smart fallback
        const conversationHistory = messages.filter(msg => msg.role !== 'system').map(msg => ({
          role: msg.role,
          content: msg.content,
        }));

        const response = await api.post('/ai/chatbot', {
          message: currentInput,
          challenge_id: challengeId || null,
          conversation_history: conversationHistory,
          user_skill_level: user?.skill_level || 'beginner',
        });

        const assistantMessage: Message = {
          role: 'assistant',
          content: response.data.response,
          timestamp: new Date(),
          type: response.data.type,
        };

        setMessages(prev => [...prev, assistantMessage]);

        // Update suggestions based on response
        if (response.data.suggestions) {
          setSuggestions(response.data.suggestions);
        }

        // Track hint level for progressive hints
        if (response.data.type === 'hint') {
          setHintLevel(prev => prev + 1);
        }
      }
    } catch (error: any) {
      console.error('Chatbot error:', error);

      // Check if it's a connection error
      if (error.code === 'ERR_NETWORK' || error.message?.includes('Network Error')) {
        setAiAvailable(false);
      }

      const errorMessage: Message = {
        role: 'assistant',
        content: language === 'zh'
          ? (error.response?.data?.detail || '连接出现问题。AI服务可能不可用。请稍后再试。')
          : (error.response?.data?.detail || "I'm having trouble connecting. The AI service might be unavailable. Please try again later."),
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const getFallbackResponse = (input: string, lang: string): string => {
    const lowercaseInput = input.toLowerCase();

    // SQL Injection
    if (lowercaseInput.includes('sql') || lowercaseInput.includes('injection')) {
      return lang === 'zh'
        ? 'SQL注入是一种攻击技术，攻击者将恶意SQL代码插入到应用程序查询中。要了解更多：\n\n1. 从基本的SELECT语句开始\n2. 学习\'OR 1=1\'技术\n3. 练习使用UNION查询\n4. 了解盲注技术\n\n虽然AI目前不可用，但你可以尝试挑战区的SQL注入练习！'
        : "SQL Injection is an attack technique where malicious SQL code is inserted into application queries. To learn more:\n\n1. Start with basic SELECT statements\n2. Learn the 'OR 1=1' technique\n3. Practice UNION-based queries\n4. Understand blind SQL injection\n\nWhile AI is unavailable, try the SQL injection challenges in the challenge section!";
    }

    // Cryptography
    if (lowercaseInput.includes('crypto') || lowercaseInput.includes('encrypt') || lowercaseInput.includes('cipher')) {
      return lang === 'zh'
        ? '密码学是保护信息的科学。基础概念：\n\n• 凯撒密码：简单的移位密码\n• Base64：编码（不是加密！）\n• XOR：位运算加密\n• AES/RSA：现代加密标准\n\n尝试挑战区的密码学挑战来实践！'
        : "Cryptography is the science of protecting information. Key concepts:\n\n• Caesar Cipher: Simple shift cipher\n• Base64: Encoding (not encryption!)\n• XOR: Bitwise encryption\n• AES/RSA: Modern encryption standards\n\nTry the cryptography challenges to practice!";
    }

    // Steganography
    if (lowercaseInput.includes('stegan') || lowercaseInput.includes('hidden') || lowercaseInput.includes('image')) {
      return lang === 'zh'
        ? '隐写术是在其他数据中隐藏信息的艺术。常见技术：\n\n• LSB（最低有效位）\n• 元数据隐藏\n• 文件追加\n• 音频/图像操作\n\n工具推荐：steghide、zsteg、exiftool'
        : "Steganography is the art of hiding information within other data. Common techniques:\n\n• LSB (Least Significant Bit)\n• Metadata hiding\n• File appending\n• Audio/image manipulation\n\nTools: steghide, zsteg, exiftool";
    }

    // Network
    if (lowercaseInput.includes('network') || lowercaseInput.includes('packet') || lowercaseInput.includes('wireshark')) {
      return lang === 'zh'
        ? '网络安全和数据包分析是CTF中的重要技能：\n\n• 使用Wireshark分析.pcap文件\n• 查找HTTP请求中的敏感数据\n• 分析TCP/UDP流\n• 识别异常流量模式\n\n尝试网络安全挑战来练习！'
        : "Network security and packet analysis are key CTF skills:\n\n• Use Wireshark for .pcap analysis\n• Look for sensitive data in HTTP requests\n• Analyze TCP/UDP streams\n• Identify abnormal traffic patterns\n\nTry the network challenges to practice!";
    }

    // Hint request
    if (lowercaseInput.includes('hint') || lowercaseInput.includes('help') || lowercaseInput.includes('stuck')) {
      return lang === 'zh'
        ? '虽然AI不可用，你仍然可以在每个挑战中使用内置提示系统！点击挑战页面的"解锁提示"按钮获取帮助。记住，使用提示会减少15%的分数。'
        : "While AI is unavailable, you can still use the built-in hint system on each challenge! Click the 'Unlock Hint' button on the challenge page. Remember, each hint reduces your score by 15%.";
    }

    // Default response
    return lang === 'zh'
      ? 'AI助手目前不可用。以下是一些你可以做的事情：\n\n• 浏览挑战区的各种挑战\n• 使用每个挑战的内置提示\n• 查看分析页面追踪你的进度\n• 在排行榜上与其他用户竞争\n\n如需启用AI功能，请确保Ollama服务正在运行。'
      : "AI is currently unavailable. Here's what you can do:\n\n• Browse various challenges in the Challenge section\n• Use built-in hints for each challenge\n• Check the Analytics page to track your progress\n• Compete with others on the Leaderboard\n\nTo enable AI features, make sure Ollama is running.";
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInputMessage(suggestion);
    inputRef.current?.focus();
  };

  const defaultSuggestions = language === 'zh'
    ? [
        "什么是SQL注入？",
        "为我生成一个挑战",
        "解释密码学基础",
        "给我一个提示",
      ]
    : [
        "What is SQL injection?",
        "Generate a challenge for me",
        "Explain cryptography basics",
        "Give me a hint",
      ];

  // Dismiss welcome popup
  const dismissWelcomePopup = () => {
    setShowWelcomePopup(false);
  };

  // Open chat from welcome popup
  const openChatFromWelcome = () => {
    setShowWelcomePopup(false);
    setIsOpen(true);
  };

  return (
    <>
      {/* Welcome Popup for New Users */}
      <AnimatePresence>
        {showWelcomePopup && !isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 50, scale: 0.9 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.9 }}
            className="fixed bottom-24 right-6 z-50 max-w-sm bg-gradient-to-br from-green-500 to-emerald-600
                       text-white rounded-2xl shadow-2xl p-5 border-2 border-green-400"
          >
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-12 h-12 bg-white/20 rounded-full flex items-center justify-center">
                <span className="text-3xl">👋</span>
              </div>
              <div className="flex-1">
                <h3 className="font-bold text-lg mb-1">
                  {language === 'zh' ? '你好！需要帮助吗？' : 'Hi there! Need help?'}
                </h3>
                <p className="text-sm text-white/90 mb-3">
                  {language === 'zh'
                    ? '我是你的学习向导！无论你是初学者还是想提升技能，我都会耐心地指导你。'
                    : "I'm your learning guide! Whether you're a beginner or looking to level up, I'll patiently guide you through."}
                </p>
                <div className="flex space-x-2">
                  <button
                    onClick={openChatFromWelcome}
                    className="px-4 py-2 bg-white text-green-600 rounded-full text-sm font-semibold
                             hover:bg-green-50 transition-colors shadow-md"
                  >
                    {language === 'zh' ? '开始学习' : 'Start Learning'}
                  </button>
                  <button
                    onClick={dismissWelcomePopup}
                    className="px-4 py-2 bg-white/20 text-white rounded-full text-sm
                             hover:bg-white/30 transition-colors"
                  >
                    {language === 'zh' ? '稍后' : 'Maybe Later'}
                  </button>
                </div>
              </div>
              <button
                onClick={dismissWelcomePopup}
                className="text-white/70 hover:text-white p-1"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            {/* Decorative elements */}
            <div className="absolute -top-2 -right-2 w-6 h-6 bg-yellow-400 rounded-full flex items-center justify-center shadow-lg">
              <span className="text-xs">✨</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Proactive Tip Popup */}
      <AnimatePresence>
        {proactiveTip.show && !isOpen && !showWelcomePopup && (
          <motion.div
            initial={{ opacity: 0, y: 20, x: 20 }}
            animate={{ opacity: 1, y: 0, x: 0 }}
            exit={{ opacity: 0, y: 20, x: 20 }}
            className="fixed bottom-24 right-6 z-50 max-w-sm bg-gradient-to-r from-primary-500 to-primary-600
                       text-white rounded-lg shadow-2xl p-4 border border-primary-400"
          >
            <div className="flex items-start space-x-3">
              <div className="flex-shrink-0">
                <span className="text-2xl">💡</span>
              </div>
              <div className="flex-1">
                <p className="font-medium text-sm mb-2">
                  {language === 'zh' ? 'AI助手提示' : 'AI Assistant Tip'}
                </p>
                <p className="text-sm text-white/90 mb-3">{proactiveTip.tip}</p>
                <div className="flex space-x-2">
                  <button
                    onClick={openChatWithTip}
                    className="px-3 py-1 bg-white text-primary-600 rounded-full text-xs font-medium hover:bg-gray-100 transition-colors"
                  >
                    {language === 'zh' ? '获取提示' : 'Get a Hint'}
                  </button>
                  <button
                    onClick={dismissTip}
                    className="px-3 py-1 bg-white/20 text-white rounded-full text-xs hover:bg-white/30 transition-colors"
                  >
                    {language === 'zh' ? '稍后' : 'Later'}
                  </button>
                </div>
              </div>
              <button
                onClick={dismissTip}
                className="text-white/70 hover:text-white"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Floating Button */}
      <motion.button
        onClick={() => setIsOpen(!isOpen)}
        className={`fixed bottom-6 right-6 z-50 w-14 h-14 ${
          aiAvailable ? 'bg-primary-600 hover:bg-primary-700' : 'bg-gray-500 hover:bg-gray-600'
        } text-white rounded-full shadow-lg flex items-center justify-center transition-colors duration-200`}
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        aria-label="Toggle AI Chatbot"
      >
        {isOpen ? (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                  d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </motion.button>

      {/* Chat Window */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 20, scale: 0.95 }}
            transition={{ duration: 0.2 }}
            className="fixed bottom-24 right-6 z-50 w-96 h-[600px] bg-white dark:bg-gray-800
                       rounded-lg shadow-2xl flex flex-col overflow-hidden border border-gray-200 dark:border-gray-700"
          >
            {/* Header */}
            <div className={`${aiAvailable ? 'bg-primary-600' : 'bg-gray-600'} text-white p-4 flex items-center justify-between`}>
              <div className="flex items-center space-x-3">
                <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                          d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                  </svg>
                </div>
                <div>
                  <h3 className="font-semibold">{language === 'zh' ? 'AI助手' : 'AI Assistant'}</h3>
                  <p className="text-xs text-white/80">
                    {aiAvailable
                      ? (language === 'zh' ? '由 LLaMA 3 驱动' : 'Powered by LLaMA 3')
                      : (language === 'zh' ? '离线模式' : 'Offline Mode')}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="text-white/80 hover:text-white transition-colors"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            {/* Messages Container */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-900">
              {messages.map((message, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3 }}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-lg px-4 py-2 ${
                      message.role === 'user'
                        ? 'bg-primary-600 text-white'
                        : message.role === 'system'
                        ? 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-800 dark:text-yellow-200 border border-yellow-200 dark:border-yellow-800'
                        : 'bg-white dark:bg-gray-800 text-gray-900 dark:text-white border border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className="text-xs mt-1 opacity-60">
                      {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </motion.div>
              ))}

              {/* Loading Indicator */}
              {isLoading && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start"
                >
                  <div className="bg-white dark:bg-gray-800 rounded-lg px-4 py-2 border border-gray-200 dark:border-gray-700">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </motion.div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Dynamic Suggestions */}
            {(messages.length <= 1 || suggestions.length > 0) && (
              <div className="px-4 py-2 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
                <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                  {language === 'zh' ? '试试这些：' : 'Try these:'}
                </p>
                <div className="flex flex-wrap gap-2">
                  {(suggestions.length > 0 ? suggestions : defaultSuggestions).map((suggestion, index) => (
                    <button
                      key={index}
                      onClick={() => handleSuggestionClick(suggestion)}
                      className="text-xs px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300
                                 rounded-full hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {/* Input Form */}
            <form onSubmit={handleSendMessage} className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
              <div className="flex space-x-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={inputMessage}
                  onChange={(e) => setInputMessage(e.target.value)}
                  placeholder={language === 'zh' ? '问我任何问题...' : 'Ask me anything...'}
                  disabled={isLoading}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg
                           bg-white dark:bg-gray-700 text-gray-900 dark:text-white
                           focus:ring-2 focus:ring-primary-500 focus:border-transparent
                           disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                />
                <button
                  type="submit"
                  disabled={!inputMessage.trim() || isLoading}
                  className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg
                           transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                  </svg>
                </button>
              </div>
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
                {language === 'zh' ? 'AI可能会犯错。请验证重要信息。' : 'AI can make mistakes. Verify important information.'}
              </p>
            </form>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default AIChatbot;

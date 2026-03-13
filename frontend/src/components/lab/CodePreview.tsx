import { useState, useEffect, useRef, lazy, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const MonacoEditor = lazy(() => import('@monaco-editor/react'));

interface CodePreviewProps {
  code: string;
  language?: string;
}

export default function CodePreview({ code, language = 'javascript' }: CodePreviewProps) {
  const [displayedCode, setDisplayedCode] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const prevCodeRef = useRef('');

  useEffect(() => {
    if (code === prevCodeRef.current) return;
    prevCodeRef.current = code;

    setIsTyping(true);
    let idx = 0;
    setDisplayedCode('');

    const interval = setInterval(() => {
      if (idx < code.length) {
        setDisplayedCode(code.slice(0, idx + 1));
        idx++;
      } else {
        clearInterval(interval);
        setIsTyping(false);
      }
    }, 15);

    return () => clearInterval(interval);
  }, [code]);

  return (
    <div className="flex flex-col h-full">
      <div className="flex items-center gap-2 mb-2">
        <span className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">
          Generated Code
        </span>
        <AnimatePresence>
          {isTyping && (
            <motion.span
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="text-xs text-primary-500"
            >
              typing...
            </motion.span>
          )}
        </AnimatePresence>
      </div>

      <div className="flex-1 rounded-xl overflow-hidden border border-gray-200 dark:border-dark-600 min-h-[300px]">
        <Suspense fallback={
          <div className="h-full bg-dark-900 flex items-center justify-center text-gray-400 text-sm">
            Loading editor...
          </div>
        }>
          <MonacoEditor
            height="100%"
            language={language}
            value={displayedCode}
            theme="vs-dark"
            options={{
              readOnly: true,
              minimap: { enabled: false },
              fontSize: 13,
              fontFamily: 'JetBrains Mono, Fira Code, monospace',
              lineHeight: 22,
              padding: { top: 16 },
              scrollBeyondLastLine: false,
              smoothScrolling: true,
              renderLineHighlight: 'none',
              lineNumbers: 'on',
              folding: false,
              contextmenu: false,
            }}
          />
        </Suspense>
      </div>
    </div>
  );
}

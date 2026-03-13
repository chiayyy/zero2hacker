import { useState, useCallback, lazy, Suspense } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import LabButton from './LabButton';
import { TestCase } from '../../types/lab';
import {
  PlayIcon,
  CheckCircleIcon,
  XCircleIcon,
  LightBulbIcon,
} from '@heroicons/react/24/outline';

const MonacoEditor = lazy(() => import('@monaco-editor/react'));

interface LabCodeEditorProps {
  starterCode: string;
  testCases?: TestCase[];
  hints: string[];
  onValidate: (code: string) => { correct: boolean; message: string };
  onComplete: (code: string) => void;
}

export default function LabCodeEditor({
  starterCode,
  testCases,
  hints,
  onValidate,
  onComplete,
}: LabCodeEditorProps) {
  const [code, setCode] = useState(starterCode);
  const [output, setOutput] = useState('');
  const [passed, setPassed] = useState<boolean | null>(null);
  const [showHint, setShowHint] = useState(-1);
  const [running, setRunning] = useState(false);

  const runCode = useCallback(() => {
    setRunning(true);
    setOutput('');
    setPassed(null);

    setTimeout(() => {
      try {
        const logs: string[] = [];
        const originalLog = console.log;
        console.log = (...args: unknown[]) => logs.push(args.join(' '));

        const fn = new Function(code);
        const result = fn();

        console.log = originalLog;

        const outputText = logs.length > 0 ? logs.join('\n') : String(result ?? '');
        setOutput(outputText);

        const validation = onValidate(code);
        setPassed(validation.correct);

        if (!validation.correct) {
          setOutput((prev) => prev + '\n' + validation.message);
        }
      } catch (error) {
        setOutput(`Error: ${error instanceof Error ? error.message : 'Unknown error'}`);
        setPassed(false);
      } finally {
        setRunning(false);
      }
    }, 500);
  }, [code, onValidate]);

  const revealHint = () => {
    if (showHint < hints.length - 1) setShowHint((prev) => prev + 1);
  };

  return (
    <div className="flex flex-col h-full gap-4">
      <div className="flex-1 rounded-xl overflow-hidden border border-gray-200 dark:border-dark-600 min-h-[300px]">
        <Suspense fallback={
          <div className="h-full bg-dark-900 flex items-center justify-center text-gray-400 text-sm">
            Loading editor...
          </div>
        }>
          <MonacoEditor
            height="100%"
            defaultLanguage="javascript"
            value={code}
            onChange={(value) => setCode(value || '')}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
              fontFamily: 'JetBrains Mono, Fira Code, monospace',
              lineHeight: 22,
              padding: { top: 16 },
              scrollBeyondLastLine: false,
              smoothScrolling: true,
              cursorBlinking: 'smooth',
              renderLineHighlight: 'all',
              bracketPairColorization: { enabled: true },
            }}
          />
        </Suspense>
      </div>

      {testCases && testCases.length > 0 && (
        <div className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-xl p-3">
          <span className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider mb-2 block">
            Test Cases
          </span>
          <div className="space-y-1">
            {testCases.map((tc, i) => (
              <div key={i} className="flex items-center gap-2 text-xs font-mono text-gray-600 dark:text-gray-400">
                <span>{tc.description}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex items-center gap-3">
        <LabButton onClick={runCode} loading={running}>
          <PlayIcon className="w-4 h-4" /> Run Code
        </LabButton>
        <LabButton variant="ghost" size="sm" onClick={revealHint} disabled={showHint >= hints.length - 1}>
          <LightBulbIcon className="w-4 h-4" /> Hint
        </LabButton>
        {passed && (
          <LabButton variant="secondary" onClick={() => onComplete(code)}>
            Submit Solution
          </LabButton>
        )}
      </div>

      <AnimatePresence>
        {showHint >= 0 && (
          <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}>
            {hints.slice(0, showHint + 1).map((hint, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-warning-600 dark:text-warning-400 mb-1">
                <LightBulbIcon className="w-4 h-4 mt-0.5 flex-shrink-0" />
                <span>{hint}</span>
              </div>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      <div className="bg-white dark:bg-dark-800 border border-gray-200 dark:border-dark-700 rounded-xl p-4 font-mono text-sm min-h-[80px]">
        <div className="flex items-center gap-2 mb-2">
          <span className="text-xs text-gray-500 dark:text-gray-400 uppercase tracking-wider">Output</span>
          {passed !== null && (
            <motion.span initial={{ scale: 0 }} animate={{ scale: 1 }}>
              {passed ? (
                <span className="flex items-center gap-1 text-xs text-success-600 dark:text-success-400">
                  <CheckCircleIcon className="w-4 h-4" /> All tests passed
                </span>
              ) : (
                <span className="flex items-center gap-1 text-xs text-danger-600 dark:text-danger-400">
                  <XCircleIcon className="w-4 h-4" /> Check your code
                </span>
              )}
            </motion.span>
          )}
        </div>
        <pre
          className={`whitespace-pre-wrap text-sm ${
            passed === false
              ? 'text-danger-600 dark:text-danger-400'
              : 'text-success-600 dark:text-success-400'
          }`}
        >
          {output || 'Run code to see output...'}
        </pre>
      </div>
    </div>
  );
}

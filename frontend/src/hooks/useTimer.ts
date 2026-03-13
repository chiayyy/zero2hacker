// ============================================
// Timer Hook
// ============================================

import { useEffect, useRef, useCallback, useState } from 'react';

interface UseTimerOptions {
  initialTime?: number;
  countdown?: boolean;
  onComplete?: () => void;
  autoStart?: boolean;
}

export function useTimer(options: UseTimerOptions = {}) {
  const { initialTime = 0, countdown = false, onComplete, autoStart = false } = options;
  const [time, setTime] = useState(countdown ? initialTime : 0);
  const [isRunning, setIsRunning] = useState(autoStart);
  const intervalRef = useRef<ReturnType<typeof setInterval> | null>(null);
  const onCompleteRef = useRef(onComplete);
  onCompleteRef.current = onComplete;

  const start = useCallback(() => setIsRunning(true), []);
  const pause = useCallback(() => setIsRunning(false), []);
  const reset = useCallback(() => {
    setIsRunning(false);
    setTime(countdown ? initialTime : 0);
  }, [countdown, initialTime]);

  useEffect(() => {
    if (!isRunning) {
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    intervalRef.current = setInterval(() => {
      setTime((prev) => {
        const next = countdown ? prev - 1 : prev + 1;
        if (countdown && next <= 0) {
          setIsRunning(false);
          onCompleteRef.current?.();
          return 0;
        }
        return next;
      });
    }, 1000);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [isRunning, countdown]);

  const formatTime = useCallback((seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  }, []);

  return {
    time,
    isRunning,
    start,
    pause,
    reset,
    formatted: formatTime(time),
  };
}

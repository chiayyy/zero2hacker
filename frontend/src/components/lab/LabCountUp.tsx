import { useSpring, useTransform, motion } from 'framer-motion';
import { useEffect } from 'react';

interface LabCountUpProps {
  value: number;
  duration?: number;
  className?: string;
  prefix?: string;
  suffix?: string;
}

export default function LabCountUp({
  value,
  duration = 1.5,
  className = '',
  prefix = '',
  suffix = '',
}: LabCountUpProps) {
  const spring = useSpring(0, { duration: duration * 1000 });
  const display = useTransform(spring, (v) => `${prefix}${Math.round(v)}${suffix}`);

  useEffect(() => {
    spring.set(value);
  }, [value, spring]);

  return <motion.span className={className}>{display}</motion.span>;
}

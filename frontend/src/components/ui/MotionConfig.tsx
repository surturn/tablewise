import React, { ReactNode } from 'react';
import { LazyMotion, domAnimation, m } from 'framer-motion';

export const springs = {
  snappy: { type: "spring" as const, stiffness: 400, damping: 30 },
  smooth: { type: "spring" as const, stiffness: 200, damping: 24 },
  gentle: { type: "spring" as const, stiffness: 120, damping: 20 },
};

export const MotionProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  return (
    <LazyMotion features={domAnimation} strict>
      {children}
    </LazyMotion>
  );
};

export const AnimatedPage: React.FC<{ children: ReactNode; className?: string }> = ({ children, className }) => {
  return (
    <m.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -10 }}
      transition={springs.smooth}
      className={className}
    >
      {children}
    </m.div>
  );
};

export const FadeIn: React.FC<{ children: ReactNode; className?: string; delay?: number }> = ({ children, className, delay = 0 }) => {
  return (
    <m.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ ...springs.smooth, delay }}
      className={className}
    >
      {children}
    </m.div>
  );
};

"use client";

import { AnimatePresence, motion, useAnimation } from "motion/react";
import { useEffect, useState } from "react";
import type { HTMLAttributes } from "react";
import { forwardRef, useCallback, useImperativeHandle, useRef } from "react";
import { cn } from "@/lib/utils";

export interface GripIconHandle {
  startAnimation: () => void;
  stopAnimation: () => void;
}

interface GripIconProps extends HTMLAttributes<HTMLDivElement> {
  size?: number;
  autoAnimate?: boolean; // Add a prop to control auto-animation
}

const CIRCLES = [
  { cx: 19, cy: 5 }, // Top right
  { cx: 12, cy: 5 }, // Top middle
  { cx: 19, cy: 12 }, // Middle right
  { cx: 5, cy: 5 }, // Top left
  { cx: 12, cy: 12 }, // Center
  { cx: 19, cy: 19 }, // Bottom right
  { cx: 5, cy: 12 }, // Middle left
  { cx: 12, cy: 19 }, // Bottom middle
  { cx: 5, cy: 19 }, // Bottom left
];

const GripIcon = forwardRef<GripIconHandle, GripIconProps>(
  (
    {
      onMouseEnter,
      onMouseLeave,
      className,
      size = 28,
      autoAnimate = true,
      ...props
    },
    ref
  ) => {
    const [isAnimating, setIsAnimating] = useState(autoAnimate);
    const controls = useAnimation();
    const isControlledRef = useRef(false);

    useImperativeHandle(ref, () => {
      isControlledRef.current = true;

      return {
        startAnimation: async () => setIsAnimating(true),
        stopAnimation: () => setIsAnimating(false),
      };
    });

    const handleMouseEnter = useCallback(
      (e: React.MouseEvent<HTMLDivElement>) => {
        if (!isControlledRef.current) {
          setIsAnimating(true);
        }
        onMouseEnter?.(e);
      },
      [onMouseEnter]
    );

    const handleMouseLeave = useCallback(
      (e: React.MouseEvent<HTMLDivElement>) => {
        if (!isControlledRef.current && !autoAnimate) {
          setIsAnimating(false);
        }
        onMouseLeave?.(e);
      },
      [onMouseLeave, autoAnimate]
    );

    useEffect(() => {
      let isMounted = true;

      const animateCircles = async () => {
        if (!isMounted || !isAnimating) return;

        await controls.start((i) => ({
          opacity: 0.3,
          transition: {
            delay: i * 0.1,
            duration: 0.2,
          },
        }));

        if (!isMounted) return;

        await controls.start((i) => ({
          opacity: 1,
          transition: {
            delay: i * 0.1,
            duration: 0.2,
          },
        }));

        if (isMounted && isAnimating) {
          requestAnimationFrame(animateCircles);
        }
      };

      // Start animation after component is mounted
      const animationTimeout = setTimeout(animateCircles, 0);

      return () => {
        isMounted = false;
        clearTimeout(animationTimeout);
      };
    }, [isAnimating, controls]);

    return (
      <div className="flex items-center justify-center h-84">
        <div
          className={cn(
            `cursor-pointer select-none p-2 hover:bg-accent rounded-md transition-colors duration-200 flex items-center justify-center`,
            className
          )}
          onMouseEnter={handleMouseEnter}
          onMouseLeave={handleMouseLeave}
          {...props}
        >
          <svg
            xmlns="http://www.w3.org/2000/svg"
            width={size}
            height={size}
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <AnimatePresence>
              {CIRCLES.map((circle, index) => (
                <motion.circle
                  key={`${circle.cx}-${circle.cy}`}
                  cx={circle.cx}
                  cy={circle.cy}
                  r="1"
                  initial="initial"
                  variants={{
                    initial: {
                      opacity: 1,
                    },
                  }}
                  animate={controls}
                  exit="initial"
                  custom={index}
                />
              ))}
            </AnimatePresence>
          </svg>
          <p>Loading model metadata</p>
        </div>
      </div>
    );
  }
);

GripIcon.displayName = "GripIcon";

export { GripIcon };

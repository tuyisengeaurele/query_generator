// One orchestrated hero sequence, subtle staggered scroll reveals, custom
// easing. No infinite background loops, no floating blobs.
export const easing = {
  standard: [0.22, 1, 0.36, 1] as [number, number, number, number],
  enter: [0.16, 1, 0.3, 1] as [number, number, number, number],
};

export const duration = {
  fast: 0.18,
  base: 0.32,
  slow: 0.6,
};

export const scrollReveal = {
  translateY: 20,
  staggerChildren: 0.08,
};

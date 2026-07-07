import "@testing-library/jest-dom/vitest";

class MockIntersectionObserver implements IntersectionObserver {
  readonly root: Element | null = null;
  readonly rootMargin: string = "";
  readonly thresholds: ReadonlyArray<number> = [];
  observe() {}
  unobserve() {}
  disconnect() {}
  takeRecords(): IntersectionObserverEntry[] {
    return [];
  }
}

// jsdom does not implement IntersectionObserver; framer-motion's
// whileInView feature needs it to mount without throwing in tests.
globalThis.IntersectionObserver = MockIntersectionObserver as unknown as typeof IntersectionObserver;


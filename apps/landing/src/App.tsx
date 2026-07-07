import { Hero } from "./sections/Hero";
import { HowItWorks } from "./sections/HowItWorks";
import { Pipeline } from "./sections/Pipeline";
import { Benchmark } from "./sections/Benchmark";
import { Architecture } from "./sections/Architecture";
import { Footer } from "./sections/Footer";

export default function App() {
  return (
    <div className="min-h-screen bg-ink">
      <Hero />
      <HowItWorks />
      <Pipeline />
      <Benchmark />
      <Architecture />
      <Footer />
    </div>
  );
}

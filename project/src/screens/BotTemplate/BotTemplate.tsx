import { useState } from "react";
import { Button } from "../../components/ui/button";
import { ContactSection } from "./sections/ContactSection/ContactSection";
import { HeroSection } from "./sections/HeroSection/HeroSection";
import { CTAAnalyzer } from "../../components/CTAAnalyzer";
import { CTAResults } from "../../components/CTAResults";
import { CTAAnalysisResponse } from "../../services/api";

export const BotTemplate = (): JSX.Element => {
  const [analysisResults, setAnalysisResults] = useState<CTAAnalysisResponse | null>(null);

  const handleAnalysisComplete = (results: CTAAnalysisResponse) => {
    setAnalysisResults(results);
  };

  const handleNewAnalysis = () => {
    setAnalysisResults(null);
  };

  return (
    <div className="bg-white w-full">
      <HeroSection />

      {/* Main Hero Section */}
      <section className="w-full relative bg-white">
        <div className="max-w-[1280px] mx-auto px-[100px] py-16">
          <div className="flex items-start justify-between">
            <div className="flex-1 max-w-[564px]">
              {/* Main Heading */}
              <div className="mb-8">
                <h1 className="text-5xl font-bold text-black mb-2">
                  Start your journey with
                </h1>
                <h1 className="text-5xl font-bold text-[#1482ff] mb-6">
                  Chatbot
                </h1>
                <p className="[font-family:'Inter',Helvetica] font-normal text-[#252525] text-lg tracking-[0] leading-[26px]">
                  An AI-powered assistant designed to engage, support, and
                  convert your audience.
                </p>
              </div>

              {/* CTA Buttons */}
              <div className="flex items-center gap-4">
                <Button className="h-auto inline-flex items-center justify-center gap-2.5 p-2.5 rounded bg-[linear-gradient(90deg,rgba(9,194,255,1)_0%,rgba(0,115,255,1)_100%)] hover:opacity-90">
                  <span className="[font-family:'Inter',Helvetica] font-medium text-white text-lg tracking-[0] leading-[normal]">
                    Start for Free
                  </span>
                </Button>

                <Button
                  variant="ghost"
                  className="h-auto inline-flex items-center justify-center gap-2.5 p-2.5 rounded hover:bg-gray-50"
                >
                  <span className="[font-family:'Inter',Helvetica] font-medium text-[#363636] text-lg tracking-[0] leading-[normal]">
                    Book Demo
                  </span>
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </Button>
              </div>
            </div>

            {/* Video Placeholder */}
            <div className="flex-shrink-0 ml-8">
              <div className="w-[469px] h-[433px] bg-gray-200 rounded-lg flex items-center justify-center relative">
                <div className="w-20 h-20 bg-gray-600 rounded-full flex items-center justify-center">
                  <svg
                    className="w-8 h-8 text-white ml-1"
                    fill="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path d="M8 5v14l11-7z" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Analyzer Section */}
      <section className="w-full bg-gray-50 py-16">
        <div className="max-w-[1280px] mx-auto px-[100px]">
          {analysisResults ? (
            <CTAResults 
              results={analysisResults} 
              onNewAnalysis={handleNewAnalysis}
            />
          ) : (
            <CTAAnalyzer onAnalysisComplete={handleAnalysisComplete} />
          )}
        </div>
      </section>

      <ContactSection />
    </div>
  );
};

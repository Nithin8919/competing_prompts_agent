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
              <div className="mb-10">
                <h1 className="text-5xl font-bold text-black mb-3 leading-tight">
                  Start your journey with
                </h1>
                <h1 className="text-5xl font-bold text-[#1482ff] mb-6 leading-tight">
                  Chatbot
                </h1>
                <p className="[font-family:'Inter',Helvetica] font-normal text-[#252525] text-lg tracking-[0] leading-[28px] mb-10">
                  An AI-powered assistant designed to engage, support, and
                  convert your audience.
                </p>
              </div>

              {/* CTA Buttons */}
              <div className="flex items-center gap-5">
                <Button 
                  variant="orange"
                  className="h-auto inline-flex items-center justify-center px-6 py-3 rounded-lg text-lg font-medium shadow-lg hover:shadow-xl transition-all duration-200"
                >
                  Start for Free
                </Button>

                <Button
                  variant="ghost"
                  className="h-auto inline-flex items-center justify-center gap-2 px-4 py-3 rounded-lg hover:bg-gray-50 transition-colors duration-200"
                >
                  <span className="[font-family:'Inter',Helvetica] font-medium text-[#363636] text-lg tracking-[0] leading-[normal]">
                    Book Demo
                  </span>
                  <svg
                    className="w-5 h-5"
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

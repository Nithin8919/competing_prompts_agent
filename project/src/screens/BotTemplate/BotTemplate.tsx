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
                <p className="[font-family:'Inter',Helvetica] font-normal text-[#252525] text-lg tracking-[0] leading-[28px] mb-6">
                  An AI-powered assistant designed to engage, support, and
                  convert your audience with intelligent conversations.
                </p>
                <p className="[font-family:'Inter',Helvetica] font-normal text-[#666666] text-base tracking-[0] leading-[24px] mb-10">
                  Boost conversions by 40% with personalized interactions that guide users through your sales funnel.
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

            {/* Video Section */}
            <div className="flex-shrink-0 ml-8">
              <div className="w-[469px] h-[433px] bg-gradient-to-br from-gray-50 to-gray-100 rounded-xl flex items-center justify-center relative overflow-hidden shadow-lg">
                {/* Video Container */}
                <div className="w-full h-full relative group cursor-pointer">
                  {/* Video Thumbnail/Preview */}
                  <div className="w-full h-full bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center relative">
                    {/* Play Button Overlay */}
                    <div className="absolute inset-0 bg-black bg-opacity-20 group-hover:bg-opacity-30 transition-all duration-300 flex items-center justify-center">
                      <div className="w-24 h-24 bg-white bg-opacity-90 rounded-full flex items-center justify-center shadow-xl group-hover:scale-110 transition-transform duration-300">
                        <svg
                          className="w-10 h-10 text-blue-600 ml-1"
                          fill="currentColor"
                          viewBox="0 0 24 24"
                        >
                          <path d="M8 5v14l11-7z" />
                        </svg>
                      </div>
                    </div>
                    
                    {/* Video Info */}
                    <div className="absolute bottom-4 left-4 right-4 text-center">
                      <p className="text-white text-sm font-medium bg-black bg-opacity-50 px-3 py-1 rounded-full inline-block">
                        Watch Demo (2:34)
                      </p>
                    </div>
                  </div>
                  
                  {/* Video Controls (hidden until video is loaded) */}
                  <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black to-transparent p-4 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <div className="flex items-center justify-between text-white text-sm">
                      <span>Chatbot Demo</span>
                      <div className="flex items-center space-x-2">
                        <button className="p-1 hover:bg-white hover:bg-opacity-20 rounded">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M6 19h4V5H6v14zm8-14v14h4V5h-4z"/>
                          </svg>
                        </button>
                        <button className="p-1 hover:bg-white hover:bg-opacity-20 rounded">
                          <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                          </svg>
                        </button>
                      </div>
                    </div>
                  </div>
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

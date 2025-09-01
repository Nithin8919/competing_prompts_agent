import React from "react";
import { Button } from "./ui/button";

export const Header: React.FC = () => {
  return (
    <header className="w-full bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-[1280px] mx-auto px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Logo - Left Side */}
          <div className="flex items-center">
            <div className="flex items-center space-x-2">
              <div className="text-2xl font-bold text-black">OI</div>
              <div className="text-sm font-medium text-black leading-tight">
                <div>Online Influence</div>
                <div>Institute</div>
              </div>
              {/* Light blue swoosh */}
              <div className="relative">
                <svg
                  className="w-8 h-4 text-blue-300"
                  viewBox="0 0 32 16"
                  fill="currentColor"
                >
                  <path d="M0 8 Q8 2 16 8 Q24 14 32 8" />
                </svg>
              </div>
            </div>
          </div>

          {/* Right Side - Rating and Button */}
          <div className="flex items-center space-x-4">
            {/* Rating */}
            <div className="flex items-center space-x-2">
              <div className="flex items-center space-x-1">
                {[...Array(5)].map((_, i) => (
                  <svg
                    key={i}
                    className="w-4 h-4 text-yellow-400"
                    fill="currentColor"
                    viewBox="0 0 20 20"
                  >
                    <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                  </svg>
                ))}
              </div>
              <span className="text-sm font-medium text-black">4.8/5</span>
            </div>

            {/* Join risk-free Button */}
            <Button 
              variant="outline"
              className="border-[#1482ff] text-[#1482ff] bg-white hover:bg-[#1482ff] hover:text-white font-medium px-4 py-2"
            >
              Join risk-free
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

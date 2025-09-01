import React from "react";
import { Button } from "../../../../components/ui/button";
import { Logo } from "../../../../components/Logo";

export const HeroSection = (): JSX.Element => {
  return (
    <header className="flex w-full items-center justify-between relative bg-white px-[100px] py-6">
      {/* Logo */}
      <Logo size="lg" />

      {/* Rating and Button */}
      <div className="inline-flex items-center gap-9 relative flex-[0_0_auto]">
        <div className="inline-flex items-center gap-2 relative flex-[0_0_auto]">
          <div className="flex items-center">
            <span className="text-yellow-400 text-lg">★★★★</span>
            <span className="ml-1 font-medium text-black leading-[normal] [font-family:'Inter',Helvetica] text-sm tracking-[0]">
              4.8/5
            </span>
          </div>
        </div>

        <Button
          variant="outline"
          className="w-[127px] h-[34px] border-[#1482ff] text-[#1482ff] hover:bg-[#1482ff] hover:text-white [font-family:'Inter',Helvetica] font-medium text-sm rounded-md"
        >
          Join risk-free
        </Button>
      </div>
    </header>
  );
};

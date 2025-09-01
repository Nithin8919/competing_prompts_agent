import React from "react";
import { Button } from "../../../../components/ui/button";
import { Checkbox } from "../../../../components/ui/checkbox";
import { Input } from "../../../../components/ui/input";
import { Label } from "../../../../components/ui/label";
import { Separator } from "../../../../components/ui/separator";
import { Textarea } from "../../../../components/ui/textarea";
import { Logo } from "../../../../components/Logo";

export const ContactSection = (): JSX.Element => {
  return (
    <footer className="w-full bg-gray-800">
      <div className="max-w-[1280px] mx-auto px-[100px] py-16">
        <div className="flex justify-between gap-16">
          {/* Left Column - Contact Information */}
          <div className="flex flex-col w-[418px]">
            <div className="mb-8">
              <h2 className="text-white text-[40px] font-medium mb-4">
                Contact us
              </h2>
              <p className="text-[#7c89a5] text-sm leading-6">
                We&apos;re always open to feedbacks, requests or remarks. Want a
                customised or private training? We&apos;d happily discuss the
                possibilities!
              </p>
            </div>

            {/* Contact Details */}
            <div className="space-y-4 mb-8">
              <div className="flex items-center gap-3">
                <div className="w-5 h-5 bg-white rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-gray-800" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.16.37 2.37.56 3.57.56.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/>
                  </svg>
                </div>
                <span className="text-white text-base">+31(0)854 898 441</span>
              </div>

              <div className="flex items-center gap-3">
                <div className="w-5 h-5 bg-white rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-gray-800" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                  </svg>
                </div>
                <span className="text-white text-base">info@onlineinfluence.com</span>
              </div>

              <div className="flex items-center gap-3">
                <div className="w-5 h-5 bg-white rounded-full flex items-center justify-center">
                  <svg className="w-3 h-3 text-gray-800" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5s1.12-2.5 2.5-2.5 2.5 1.12 2.5 2.5-1.12 2.5-2.5 2.5z"/>
                  </svg>
                </div>
                <span className="text-white text-base">Fellenoord 232 | 5611 ZC, Eindhoven | NL</span>
              </div>
            </div>

            {/* Logo */}
            <div className="mb-8">
              <Logo size="md" className="text-white" />
            </div>

            {/* Footer Links */}
            <div className="flex items-center gap-2 text-[#7c89a5] text-sm">
              <span>Privacy</span>
              <span>|</span>
              <span>Terms and conditions</span>
            </div>
          </div>

          {/* Right Column - Contact Form */}
          <div className="flex flex-col w-[484px]">
            <div className="space-y-6">
              {/* Name Fields */}
              <div className="flex gap-4">
                <div className="flex-1">
                  <Label className="text-[#7c89a5] text-xs mb-2 block">
                    First name
                  </Label>
                  <Input className="w-full h-[38px] bg-white rounded-[10px] border-0 text-gray-800" />
                </div>
                <div className="flex-1">
                  <Label className="text-[#7c89a5] text-xs mb-2 block">
                    Last name
                  </Label>
                  <Input className="w-full h-[38px] bg-white rounded-[10px] border-0 text-gray-800" />
                </div>
              </div>

              {/* Email Field */}
              <div>
                <Label className="text-[#7c89a5] text-xs mb-2 block">
                  E-mail address
                </Label>
                <Input className="w-full h-[38px] bg-white rounded-[10px] border-0 text-gray-800" />
              </div>

              {/* Phone Field */}
              <div>
                <Label className="text-[#7c89a5] text-xs mb-2 block">
                  Phone number
                </Label>
                <div className="h-[38px] bg-white rounded-[10px] flex items-center px-4">
                  <span className="text-[#7c89a5] text-xs mr-4">Nederland</span>
                  <div className="w-px h-6 bg-gray-300 mx-4"></div>
                  <span className="text-[#7c89a5] text-xs mr-4">+31</span>
                  <div className="flex-1">
                    <input 
                      type="text" 
                      className="w-full bg-transparent border-0 outline-none text-gray-800 text-sm"
                      placeholder="Enter phone number"
                    />
                  </div>
                  <svg className="w-4 h-4 text-[#7c89a5]" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>

              {/* Message Field */}
              <div>
                <Label className="text-[#7c89a5] text-xs mb-2 block">
                  Message
                </Label>
                <Textarea 
                  className="w-full h-[97px] bg-white rounded-[10px] border-0 text-gray-800 resize-none p-3" 
                  placeholder="Enter your message..."
                />
              </div>

              {/* Terms Text */}
              <p className="text-[#7c89a5] text-xs leading-5">
                By submitting this form, you consent to the{" "}
                <span className="underline cursor-pointer">terms and conditions.</span>
              </p>

              {/* Checkbox */}
              <div className="flex items-start gap-3">
                <Checkbox className="w-5 h-5 bg-white rounded-md border-0 mt-0.5" />
                <Label className="text-[#7c89a5] text-xs leading-5 flex-1">
                  I consent to receive messages sent by Online Influence Institute
                  and understand my data will be shared for workshop-related
                  purposes by email or text.
                </Label>
              </div>

              {/* Submit Button */}
              <Button className="w-[124px] h-[38px] bg-gradient-to-r from-[#09c2ff] to-[#0073ff] text-white rounded-[10px] border-0 font-medium text-base">
                Contact us
              </Button>
            </div>
          </div>
        </div>

        {/* Bottom Footer */}
        <div className="mt-16 pt-8 border-t border-[#7c89a5]">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2 text-[#7c89a5] text-sm">
              <span>Privacy</span>
              <span>|</span>
              <span>Terms and conditions</span>
            </div>

            <div className="flex flex-col items-end gap-1">
              <span className="text-white text-xs">Certified partner</span>
              <div className="w-[93px] h-[57px] bg-white rounded flex items-center justify-center">
                <span className="text-black font-bold text-lg">III</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

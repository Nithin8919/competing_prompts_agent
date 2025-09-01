import React from "react";

interface LogoProps {
  className?: string;
  size?: "sm" | "md" | "lg";
}

export const Logo: React.FC<LogoProps> = ({ className = "", size = "md" }) => {
  const sizeClasses = {
    sm: "h-8 w-auto",
    md: "h-12 w-auto", 
    lg: "h-16 w-auto"
  };

  return (
    <div className={`flex items-center ${className}`}>
      <img 
        src="/logo.jpeg" 
        alt="Online Influence Institute Logo" 
        className={`${sizeClasses[size]} object-contain`}
      />
    </div>
  );
};

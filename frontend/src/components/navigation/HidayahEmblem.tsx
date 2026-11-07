"use client";

import React from "react";

interface HidayahEmblemProps {
  className?: string;
}

export function HidayahEmblem({ className = "w-8 h-8" }: HidayahEmblemProps) {
  return (
    <svg
      viewBox="0 0 512 512"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Hidayah AI Sacred Emblem"
    >
      <defs>
        {/* Imperial Champagne Gold Gradient */}
        <linearGradient id="hidayahGold" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#FDE68A" />
          <stop offset="30%" stopColor="#D4AF37" />
          <stop offset="70%" stopColor="#B45309" />
          <stop offset="100%" stopColor="#F59E0B" />
        </linearGradient>

        {/* Deep Forest Emerald Gradient */}
        <linearGradient id="hidayahEmerald" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#064E3B" />
          <stop offset="50%" stopColor="#022c22" />
          <stop offset="100%" stopColor="#051b14" />
        </linearGradient>

        {/* Inner Luminous Glow */}
        <linearGradient id="hidayahIvory" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stopColor="#FFFFFF" />
          <stop offset="100%" stopColor="#E2E8F0" />
        </linearGradient>

        {/* Soft Radial Backlight */}
        <radialGradient id="centerGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#D4AF37" stopOpacity="0.25" />
          <stop offset="100%" stopColor="#D4AF37" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* Rounded Hexagonal / Shield Base */}
      <rect
        width="512"
        height="512"
        rx="112"
        fill="url(#hidayahEmerald)"
        stroke="url(#hidayahGold)"
        strokeWidth="10"
        strokeOpacity="0.6"
      />

      {/* Central Radiance */}
      <circle cx="256" cy="256" r="160" fill="url(#centerGlow)" />

      {/* Main Sacred Geometric Emblem (Centered at 256, 256) */}
      <g transform="translate(256, 256) scale(0.95)" strokeMiterlimit="10">
        {/* 1. Outer Rub el Hizb (8-Pointed Star of Revelation) */}
        <polygon
          points="
            0,-168 49,-119 119,-119 119,-49 
            168,0 119,49 119,119 49,119 
            0,168 -49,119 -119,119 -119,49 
            -168,0 -119,-49 -119,-119 -49,-119"
          stroke="url(#hidayahGold)"
          strokeWidth="13"
          strokeLinejoin="miter"
        />

        {/* 2. Inner Interlocking Star Accent */}
        <polyline
          points="
            -95,40 -135,0 -95,-40 -95,-95 -40,-95 
            0,-135 40,-95 95,-95 95,-40 135,0 95,40"
          stroke="url(#hidayahIvory)"
          strokeWidth="7"
          strokeLinecap="round"
          strokeLinejoin="miter"
          strokeOpacity="0.85"
        />

        {/* 3. Open Mushaf (Holy Scripture) Chevrons */}
        <polyline
          points="-80,34 0,84 80,34"
          stroke="url(#hidayahIvory)"
          strokeWidth="9"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <polyline
          points="-96,56 0,114 96,56"
          stroke="url(#hidayahGold)"
          strokeWidth="11"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
        <polyline
          points="-96,76 -96,96 -40,96 0,138 40,96 96,96 96,76"
          stroke="url(#hidayahGold)"
          strokeWidth="9"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* 4. Central 'H' & Arabic 'Haa' (هـ - Hidayah) Andalusian Arch */}
        {/* Left Pillar */}
        <line
          x1="-42"
          y1="-62"
          x2="-42"
          y2="28"
          stroke="url(#hidayahGold)"
          strokeWidth="11"
          strokeLinecap="round"
        />
        {/* Right Lower Pillar */}
        <line
          x1="42"
          y1="8"
          x2="42"
          y2="28"
          stroke="url(#hidayahGold)"
          strokeWidth="11"
          strokeLinecap="round"
        />

        {/* Pointed Mihrab Arch & Graceful 'Haa' Loop */}
        <path
          d="M -20,-32 
             Q -10,-64 0,-78 
             Q 20,-52 20,-16 
             C 20,8 -16,12 -16,-14 
             C -16,-32 6,-32 6,-16 
             C 6,0 -24,8 -42,22"
          stroke="url(#hidayahGold)"
          strokeWidth="11"
          strokeLinecap="round"
          strokeLinejoin="round"
        />

        {/* Right Ascending Ribbon */}
        <path
          d="M -12,-6 
             C 8,12 42,4 42,-22 
             L 42,-62"
          stroke="url(#hidayahGold)"
          strokeWidth="11"
          strokeLinecap="round"
        />
      </g>
    </svg>
  );
}

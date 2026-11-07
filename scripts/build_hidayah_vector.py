import math
from pathlib import Path

def generate_rub_el_hizb_points(cx, cy, r_out):
    """Generate exact Euclidean 16-point Rub el Hizb polygon points."""
    r_in = r_out * math.sqrt(2 - math.sqrt(2))
    pts = []
    for i in range(16):
        angle = -math.pi / 2 + i * (math.pi / 8)
        r = r_out if i % 2 == 0 else r_in
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        pts.append(f"{x:.2f},{y:.2f}")
    return " ".join(pts)

def create_hidayah_app_icon_svg() -> str:
    cx, cy = 256, 212
    outer_star = generate_rub_el_hizb_points(cx, cy, 154)
    inner_star = generate_rub_el_hizb_points(cx, cy, 142)
    accent_star = generate_rub_el_hizb_points(cx, cy, 134)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <!-- Background Radial Vignette (Sacred Deep Emerald) -->
    <radialGradient id="emeraldBg" cx="50%" cy="40%" r="65%">
      <stop offset="0%" stop-color="#0E3D2B" />
      <stop offset="45%" stop-color="#08281D" />
      <stop offset="80%" stop-color="#041811" />
      <stop offset="100%" stop-color="#020E0A" />
    </radialGradient>

    <!-- Inner Star Subtle Depth Glow -->
    <radialGradient id="starInnerGlow" cx="50%" cy="45%" r="55%">
      <stop offset="0%" stop-color="#144C36" stop-opacity="0.6" />
      <stop offset="60%" stop-color="#08281D" stop-opacity="0.2" />
      <stop offset="100%" stop-color="#03150E" stop-opacity="0" />
    </radialGradient>

    <!-- Master Champagne Satin Gold Gradient -->
    <linearGradient id="goldMetallic" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#FBF0B9" />
      <stop offset="25%" stop-color="#E5C772" />
      <stop offset="50%" stop-color="#D4AF37" />
      <stop offset="75%" stop-color="#AA8220" />
      <stop offset="100%" stop-color="#EED588" />
    </linearGradient>

    <!-- Bevel Highlight (Bright Rim Light) -->
    <linearGradient id="goldHighlight" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFF5D1" />
      <stop offset="50%" stop-color="#D4AF37" />
      <stop offset="100%" stop-color="#8F6A15" />
    </linearGradient>

    <!-- Deep Shadow Gold for Depth & Underside -->
    <linearGradient id="goldShadow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#9C771C" />
      <stop offset="60%" stop-color="#6E500D" />
      <stop offset="100%" stop-color="#4A3405" />
    </linearGradient>

    <!-- Subtle Drop Shadow Filter for Clean Optical Elevation -->
    <filter id="softShadow" x="-15%" y="-15%" width="130%" height="130%">
      <feDropShadow dx="0" dy="8" stdDeviation="10" flood-color="#010805" flood-opacity="0.75" />
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#000000" flood-opacity="0.5" />
    </filter>

    <!-- Inner Stroke Glow Filter -->
    <filter id="subtleGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="1.5" result="blur" />
      <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
  </defs>

  <!-- SQUIRCLE APP CONTAINER -->
  <rect width="512" height="512" rx="112" fill="url(#emeraldBg)" />
  <rect width="510" height="510" x="1" y="1" rx="111" fill="none" stroke="rgba(212, 175, 55, 0.15)" stroke-width="1.5" />

  <!-- MAIN EMBLEM GROUP WITH SUBTLE ELEVATION -->
  <g filter="url(#softShadow)">

    <!-- 1. RUB EL HIZB (SACRED 8-POINTED STAR) -->
    <!-- Star Inner Field Fill -->
    <polygon points="{outer_star}" fill="url(#starInnerGlow)" />

    <!-- Outer Star Rim -->
    <polygon points="{outer_star}" fill="none" stroke="url(#goldMetallic)" stroke-width="6.5" stroke-linejoin="miter" stroke-miterlimit="8" />

    <!-- Inner Recessed Star Track -->
    <polygon points="{inner_star}" fill="none" stroke="url(#goldShadow)" stroke-width="1.8" stroke-linejoin="miter" stroke-miterlimit="8" opacity="0.8" />
    <polygon points="{accent_star}" fill="none" stroke="url(#goldHighlight)" stroke-width="1.2" stroke-linejoin="miter" stroke-miterlimit="8" opacity="0.55" />

    <!-- 2. OPEN MUSHAF (PAGES OF SACRED KNOWLEDGE) -->
    <!-- Right Page (Outer Boundary) -->
    <path d="M 256,276 
             C 285,274 316,268 338,252 
             C 344,228 348,198 344,170 
             C 318,172 288,178 266,192 
             Z" 
          fill="none" stroke="url(#goldMetallic)" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round" />

    <!-- Right Page (Layered Turning Leaf Inside) -->
    <path d="M 270,202 
             C 292,192 318,188 334,188 
             C 338,208 336,232 328,244 
             C 308,256 284,260 268,262" 
          fill="none" stroke="url(#goldMetallic)" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" opacity="0.9" />

    <!-- Lower Book Spine Base Notch -->
    <path d="M 238,284 
             C 248,288 253,293 256,295 
             C 259,293 264,288 274,284" 
          fill="none" stroke="url(#goldHighlight)" stroke-width="4" stroke-linecap="round" />

    <!-- 3. THE CALLIGRAPHIC 'HAA' (هـ) RIBBON OF HIDAYAH -->
    <!-- Fluid Arabic Calligraphic Haa intertwined with the Book -->
    <!-- Outer Sweep of Haa (Left Page Wing & Ascender) -->
    <path d="M 244,130 
             C 246,144 238,158 226,172 
             C 206,196 186,216 172,238 
             C 162,254 166,270 182,274 
             C 204,280 230,272 256,258 
             C 252,246 244,232 238,220
             C 220,186 210,166 226,146 
             C 234,136 240,131 244,130 Z" 
          fill="url(#goldMetallic)" stroke="url(#goldHighlight)" stroke-width="1.2" stroke-linejoin="round" />

    <!-- Inner Loop / Eye of the 'Haa' (Arabic 'Ayn / Knot) -->
    <path d="M 226,172 
             C 242,160 262,170 260,192 
             C 258,212 238,224 220,214 
             C 208,206 212,184 226,172 Z" 
          fill="#062218" stroke="url(#goldMetallic)" stroke-width="3.5" stroke-linejoin="round" />

    <!-- Inner Calligraphic Ribbon Highlight Accent -->
    <path d="M 228,178 
             C 240,170 252,176 252,192 
             C 252,204 238,212 226,206" 
          fill="none" stroke="url(#goldHighlight)" stroke-width="2" stroke-linecap="round" />

    <!-- Left Page Outer Spine Swirl -->
    <path d="M 182,274 
             C 170,268 158,252 152,236 
             C 148,222 152,208 162,198 
             C 164,196 168,194 172,196" 
          fill="none" stroke="url(#goldMetallic)" stroke-width="3" stroke-linecap="round" />
  </g>

  <!-- 4. REFINED BRAND TYPOGRAPHY LOCKUP -->
  <g text-anchor="middle">
    <!-- Primary Brand Name -->
    <text x="256" y="426" 
          font-family="'Playfair Display', 'Cinzel', 'Georgia', 'Inter', -apple-system, sans-serif" 
          font-size="34" 
          font-weight="700" 
          letter-spacing="9" 
          fill="url(#goldMetallic)"
          filter="url(#subtleGlow)">HIDAYAH AI</text>

    <!-- Secondary Scholarly Subtitle -->
    <text x="256" y="456" 
          font-family="'Inter', -apple-system, 'SF Pro Display', sans-serif" 
          font-size="10.5" 
          font-weight="600" 
          letter-spacing="5.5" 
          fill="#97B8A6">ISLAMIC RESEARCH PLATFORM</text>
  </g>
</svg>"""
    return svg

def create_hidayah_transparent_svg() -> str:
    """Standalone emblem with transparent background for headers, sidebars, and watermarks."""
    cx, cy = 256, 212
    outer_star = generate_rub_el_hizb_points(cx, cy, 154)
    inner_star = generate_rub_el_hizb_points(cx, cy, 142)
    accent_star = generate_rub_el_hizb_points(cx, cy, 134)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" width="100%" height="100%">
  <defs>
    <linearGradient id="goldMetallicTrans" x1="15%" y1="0%" x2="85%" y2="100%">
      <stop offset="0%" stop-color="#FBF0B9" />
      <stop offset="25%" stop-color="#E5C772" />
      <stop offset="50%" stop-color="#D4AF37" />
      <stop offset="75%" stop-color="#AA8220" />
      <stop offset="100%" stop-color="#EED588" />
    </linearGradient>

    <linearGradient id="goldHighlightTrans" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FFF5D1" />
      <stop offset="50%" stop-color="#D4AF37" />
      <stop offset="100%" stop-color="#8F6A15" />
    </linearGradient>

    <filter id="subtleGlowTrans" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="4" stdDeviation="8" flood-color="#000000" flood-opacity="0.45" />
    </filter>
  </defs>

  <g filter="url(#subtleGlowTrans)">
    <!-- 1. RUB EL HIZB -->
    <polygon points="{outer_star}" fill="none" stroke="url(#goldMetallicTrans)" stroke-width="6.5" stroke-linejoin="miter" stroke-miterlimit="8" />
    <polygon points="{inner_star}" fill="none" stroke="#8E6B17" stroke-width="1.8" stroke-linejoin="miter" stroke-miterlimit="8" opacity="0.8" />
    <polygon points="{accent_star}" fill="none" stroke="url(#goldHighlightTrans)" stroke-width="1.2" stroke-linejoin="miter" stroke-miterlimit="8" opacity="0.6" />

    <!-- 2. OPEN MUSHAF -->
    <path d="M 256,276 C 285,274 316,268 338,252 C 344,228 348,198 344,170 C 318,172 288,178 266,192 Z" 
          fill="none" stroke="url(#goldMetallicTrans)" stroke-width="4.5" stroke-linejoin="round" stroke-linecap="round" />

    <path d="M 270,202 C 292,192 318,188 334,188 C 338,208 336,232 328,244 C 308,256 284,260 268,262" 
          fill="none" stroke="url(#goldMetallicTrans)" stroke-width="3" stroke-linejoin="round" stroke-linecap="round" opacity="0.9" />

    <path d="M 238,284 C 248,288 253,293 256,295 C 259,293 264,288 274,284" 
          fill="none" stroke="url(#goldHighlightTrans)" stroke-width="4" stroke-linecap="round" />

    <!-- 3. CALLIGRAPHIC 'HAA' (هـ) -->
    <path d="M 244,130 C 246,144 238,158 226,172 C 206,196 186,216 172,238 C 162,254 166,270 182,274 C 204,280 230,272 256,258 C 252,246 244,232 238,220 C 220,186 210,166 226,146 C 234,136 240,131 244,130 Z" 
          fill="url(#goldMetallicTrans)" stroke="url(#goldHighlightTrans)" stroke-width="1.2" stroke-linejoin="round" />

    <path d="M 226,172 C 242,160 262,170 260,192 C 258,212 238,224 220,214 C 208,206 212,184 226,172 Z" 
          fill="none" stroke="url(#goldMetallicTrans)" stroke-width="3.5" stroke-linejoin="round" />

    <path d="M 228,178 C 240,170 252,176 252,192 C 252,204 238,212 226,206" 
          fill="none" stroke="url(#goldHighlightTrans)" stroke-width="2" stroke-linecap="round" />

    <path d="M 182,274 C 170,268 158,252 152,236 C 148,222 152,208 162,198 C 164,196 168,194 172,196" 
          fill="none" stroke="url(#goldMetallicTrans)" stroke-width="3" stroke-linecap="round" />
  </g>

  <!-- 4. TYPOGRAPHY -->
  <g text-anchor="middle">
    <text x="256" y="426" 
          font-family="'Playfair Display', 'Cinzel', 'Georgia', 'Inter', -apple-system, sans-serif" 
          font-size="34" 
          font-weight="700" 
          letter-spacing="9" 
          fill="url(#goldMetallicTrans)">HIDAYAH AI</text>

    <text x="256" y="456" 
          font-family="'Inter', -apple-system, 'SF Pro Display', sans-serif" 
          font-size="10.5" 
          font-weight="600" 
          letter-spacing="5.5" 
          fill="#94A3B8">ISLAMIC RESEARCH PLATFORM</text>
  </g>
</svg>"""
    return svg

def create_hidayah_horizontal_svg() -> str:
    """Wide horizontal lockup (height 90, width 420) for top navbars and headers."""
    cx, cy = 52, 45
    r_scale = 36 / 154
    outer_star = generate_rub_el_hizb_points(cx, cy, 36)
    inner_star = generate_rub_el_hizb_points(cx, cy, 33)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 90" width="100%" height="100%">
  <defs>
    <linearGradient id="goldHz" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FBF0B9" />
      <stop offset="50%" stop-color="#D4AF37" />
      <stop offset="100%" stop-color="#AA8220" />
    </linearGradient>
  </defs>

  <!-- EMBLEM ICON (LEFT) -->
  <g transform="translate(0, 0)">
    <!-- Star -->
    <polygon points="{outer_star}" fill="#08281D" stroke="url(#goldHz)" stroke-width="2.2" stroke-linejoin="miter" stroke-miterlimit="6" />
    <polygon points="{inner_star}" fill="none" stroke="#9E7B21" stroke-width="0.8" stroke-linejoin="miter" stroke-miterlimit="6" opacity="0.7" />

    <!-- Scaled Book & Haa (Transformed to fit cx=52, cy=45, scale=0.235) -->
    <g transform="translate({cx}, {cy}) scale({r_scale}) translate(-256, -212)">
      <!-- Right Page -->
      <path d="M 256,276 C 285,274 316,268 338,252 C 344,228 348,198 344,170 C 318,172 288,178 266,192 Z" 
            fill="none" stroke="url(#goldHz)" stroke-width="12" stroke-linejoin="round" />
      <path d="M 270,202 C 292,192 318,188 334,188 C 338,208 336,232 328,244 C 308,256 284,260 268,262" 
            fill="none" stroke="url(#goldHz)" stroke-width="9" stroke-linejoin="round" opacity="0.9" />
      <path d="M 238,284 C 248,288 253,293 256,295 C 259,293 264,288 274,284" 
            fill="none" stroke="#FFF5D1" stroke-width="12" stroke-linecap="round" />

      <!-- Calligraphic Haa -->
      <path d="M 244,130 C 246,144 238,158 226,172 C 206,196 186,216 172,238 C 162,254 166,270 182,274 C 204,280 230,272 256,258 C 252,246 244,232 238,220 C 220,186 210,166 226,146 C 234,136 240,131 244,130 Z" 
            fill="url(#goldHz)" stroke="#FFF5D1" stroke-width="3" />
      <path d="M 226,172 C 242,160 262,170 260,192 C 258,212 238,224 220,214 C 208,206 212,184 226,172 Z" 
            fill="#08281D" stroke="url(#goldHz)" stroke-width="10" />
      <path d="M 182,274 C 170,268 158,252 152,236 C 148,222 152,208 162,198 C 164,196 168,194 172,196" 
            fill="none" stroke="url(#goldHz)" stroke-width="9" stroke-linecap="round" />
    </g>
  </g>

  <!-- TYPOGRAPHY (RIGHT) -->
  <g transform="translate(108, 0)">
    <text x="0" y="44" 
          font-family="'Playfair Display', 'Cinzel', 'Georgia', 'Inter', -apple-system, sans-serif" 
          font-size="28" 
          font-weight="700" 
          letter-spacing="5" 
          fill="#FFFFFF">HIDAYAH<tspan fill="url(#goldHz)"> AI</tspan></text>

    <text x="2" y="66" 
          font-family="'Inter', -apple-system, sans-serif" 
          font-size="10" 
          font-weight="500" 
          letter-spacing="3.5" 
          fill="#94A3B8">30-DAY RAMADAN RESEARCH COMPANION</text>
  </g>
</svg>"""
    return svg

if __name__ == "__main__":
    app_dir = Path(__file__).resolve().parent.parent

    # 1. Master hidayah_logo.svg in root
    root_svg = app_dir / "hidayah_logo.svg"
    app_icon_content = create_hidayah_app_icon_svg()
    root_svg.write_text(app_icon_content, encoding="utf-8")
    print(f"Generated: {root_svg} ({len(app_icon_content)} bytes)")

    # 2. Transparent & Horizontal in frontend/public/logos
    logos_dir = app_dir / "frontend" / "public" / "logos"
    logos_dir.mkdir(parents=True, exist_ok=True)

    icon_svg = logos_dir / "hidayah_app_icon.svg"
    icon_svg.write_text(app_icon_content, encoding="utf-8")

    trans_svg = logos_dir / "hidayah_logo_transparent.svg"
    trans_content = create_hidayah_transparent_svg()
    trans_svg.write_text(trans_content, encoding="utf-8")
    print(f"Generated: {trans_svg} ({len(trans_content)} bytes)")

    hz_svg = logos_dir / "hidayah_logo_horizontal.svg"
    hz_content = create_hidayah_horizontal_svg()
    hz_svg.write_text(hz_content, encoding="utf-8")
    print(f"Generated: {hz_svg} ({len(hz_content)} bytes)")

    # Copy to frontend/public root as well
    (app_dir / "frontend" / "public" / "hidayah_logo.svg").write_text(app_icon_content, encoding="utf-8")
    (app_dir / "frontend" / "public" / "hidayah_logo_horizontal.svg").write_text(hz_content, encoding="utf-8")

    print("Master vector suite build successful.")

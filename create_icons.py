import os
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import QApplication
import sys

ICONS_DIR = os.path.join(os.path.dirname(__file__), "assets", "icons")
os.makedirs(ICONS_DIR, exist_ok=True)

SVGS = {
    "app_logo.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="48" height="48">
  <defs>
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#0284C7" />
      <stop offset="50%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#1E1B4B" />
    </linearGradient>
    <linearGradient id="accentGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="100%" stop-color="#818CF8" />
    </linearGradient>
    <filter id="shadow" x="-10%" y="-10%" width="120%" height="120%">
      <feDropShadow dx="0" dy="2" stdDeviation="2" flood-color="#000" flood-opacity="0.3" />
    </filter>
  </defs>
  <!-- Background squircle -->
  <rect x="2" y="2" width="44" height="44" rx="10" fill="url(#bgGrad)" filter="url(#shadow)" />
  <rect x="3" y="3" width="42" height="42" rx="9" fill="none" stroke="#60A5FA" stroke-width="1" stroke-opacity="0.4" />
  
  <!-- Stylized Greek letter Mu (μ) -->
  <path d="M 12 18 V 32 M 12 25 C 12 22 15 20 18 20 C 22 20 22 24 22 26 V 32 M 12 36 V 30" 
        fill="none" stroke="#FFFFFF" stroke-width="3.2" stroke-linecap="round" stroke-linejoin="round" />
        
  <!-- Modern 'C' -->
  <path d="M 31 22 C 29.5 20.5 27 20.5 25.5 22 C 23.5 24 23.5 28 25.5 30 C 27 31.5 29.5 31.5 31 30" 
        fill="none" stroke="url(#accentGrad)" stroke-width="3" stroke-linecap="round" />
        
  <!-- Plus Plus (++) -->
  <path d="M 34 23 V 27 M 32 25 H 36" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" />
  <path d="M 40 23 V 27 M 38 25 H 42" fill="none" stroke="#38BDF8" stroke-width="2" stroke-linecap="round" />
</svg>""",

    "new_file.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <linearGradient id="docGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FFFFFF" />
      <stop offset="100%" stop-color="#F1F5F9" />
    </linearGradient>
  </defs>
  <!-- Document base -->
  <path d="M 5 3 C 4.45 3 4 3.45 4 4 L 4 20 C 4 20.55 4.45 21 5 21 L 19 21 C 19.55 21 20 20.55 20 20 L 20 9 L 14 3 L 5 3 Z" 
        fill="url(#docGrad)" stroke="#64748B" stroke-width="1.5" stroke-linejoin="round" />
  <!-- Folded corner -->
  <path d="M 14 3 L 14 9 L 20 9" fill="#E2E8F0" stroke="#64748B" stroke-width="1.5" stroke-linejoin="round" />
  <!-- Blue plus badge -->
  <circle cx="15.5" cy="15.5" r="5" fill="#2563EB" />
  <path d="M 15.5 13 V 18 M 13 15.5 H 18" stroke="#FFFFFF" stroke-width="1.6" stroke-linecap="round" />
</svg>""",

    "new_project.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <linearGradient id="projFolder" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#6366F1" />
      <stop offset="100%" stop-color="#4F46E5" />
    </linearGradient>
  </defs>
  <!-- Folder Back -->
  <path d="M 3 6 C 3 4.9 3.9 4 5 4 L 9 4 L 11 6 L 19 6 C 20.1 6 21 6.9 21 8 L 21 18 C 21 19.1 20.1 20 19 20 L 5 20 C 3.9 20 3 19.1 3 18 Z" 
        fill="url(#projFolder)" />
  <!-- Blueprint sheet sticking out -->
  <rect x="6" y="8" width="12" height="7" rx="1" fill="#EEF2FF" stroke="#A5B4FC" stroke-width="1" />
  <line x1="8" y1="11" x2="16" y2="11" stroke="#6366F1" stroke-width="1" stroke-dasharray="2 1" />
  <!-- Plus badge -->
  <circle cx="17" cy="16" r="4.5" fill="#10B981" />
  <path d="M 17 14 V 18 M 15 16 H 19" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round" />
</svg>""",

    "open_file.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <linearGradient id="folderFront" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FBBF24" />
      <stop offset="100%" stop-color="#D97706" />
    </linearGradient>
    <linearGradient id="folderBack" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#F59E0B" />
      <stop offset="100%" stop-color="#B45309" />
    </linearGradient>
  </defs>
  <!-- Folder Back -->
  <path d="M 3 6 C 3 4.9 3.9 4 5 4 L 9 4 L 11 6 L 19 6 C 20.1 6 21 6.9 21 8 L 21 18 C 21 19.1 20.1 20 19 20 L 5 20 C 3.9 20 3 19.1 3 18 Z" 
        fill="url(#folderBack)" />
  <!-- Open Front Flap -->
  <path d="M 2 11 L 5.5 20 L 22 20 L 21 11 Z" fill="url(#folderFront)" />
  <!-- Arrow emerging -->
  <path d="M 12 7 L 12 15 M 9 10 L 12 7 L 15 10" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
</svg>""",

    "save.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <linearGradient id="diskGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#1D4ED8" />
    </linearGradient>
  </defs>
  <!-- Disk body -->
  <path d="M 4 4 C 4 3.45 4.45 3 5 3 L 17 3 L 20 6 L 20 19 C 20 19.55 19.55 20 19 20 L 5 20 C 4.45 20 4 19.55 4 19 Z" 
        fill="url(#diskGrad)" stroke="#1E40AF" stroke-width="1.2" />
  <!-- Shutter / label top -->
  <rect x="7" y="3" width="10" height="6" rx="1" fill="#F8FAFC" />
  <rect x="13" y="4" width="2.5" height="4" fill="#2563EB" />
  <!-- Paper label bottom -->
  <rect x="6.5" y="12" width="11" height="8" rx="1" fill="#FFFFFF" stroke="#93C5FD" stroke-width="0.8" />
  <line x1="8.5" y1="15" x2="15.5" y2="15" stroke="#94A3B8" stroke-width="1.2" stroke-linecap="round" />
  <line x1="8.5" y1="17.5" x2="13.5" y2="17.5" stroke="#94A3B8" stroke-width="1.2" stroke-linecap="round" />
</svg>""",

    "save_all.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <linearGradient id="diskBackGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#60A5FA" />
      <stop offset="100%" stop-color="#3B82F6" />
    </linearGradient>
    <linearGradient id="diskFrontGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#1E40AF" />
    </linearGradient>
  </defs>
  <!-- Back disk -->
  <path d="M 2 4 C 2 3.45 2.45 3 3 3 L 13 3 L 16 6 L 16 15 C 16 15.55 15.55 16 15 16 L 3 16 C 2.45 16 2 15.55 2 15 Z" 
        fill="url(#diskBackGrad)" />
  <rect x="5" y="3" width="7" height="4" fill="#E2E8F0" />
  <!-- Front disk -->
  <path d="M 8 7 C 8 6.45 8.45 6 9 6 L 19 6 L 22 9 L 22 20 C 22 20.55 21.55 21 21 21 L 9 21 C 8.45 21 8 20.55 8 20 Z" 
        fill="url(#diskFrontGrad)" stroke="#1E3A8A" stroke-width="1" />
  <rect x="11" y="6" width="7" height="5" rx="0.5" fill="#F8FAFC" />
  <rect x="15" y="7" width="2" height="3" fill="#2563EB" />
  <rect x="10.5" y="14" width="9" height="7" rx="0.8" fill="#FFFFFF" />
  <line x1="12" y1="16.5" x2="17.5" y2="16.5" stroke="#94A3B8" stroke-width="1.2" stroke-linecap="round" />
</svg>""",

    "undo.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M 9 14 L 4 9 L 9 4" fill="none" stroke="#475569" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
  <path d="M 4 9 L 14 9 C 17.5 9 20 11.5 20 15 C 20 18.5 17.5 20 14 20 L 8 20" 
        fill="none" stroke="#475569" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
</svg>""",

    "redo.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <path d="M 15 14 L 20 9 L 15 4" fill="none" stroke="#475569" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
  <path d="M 20 9 L 10 9 C 6.5 9 4 11.5 4 15 C 4 18.5 6.5 20 10 20 L 16 20" 
        fill="none" stroke="#475569" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
</svg>""",

    "cut.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <circle cx="6" cy="18" r="3" fill="none" stroke="#475569" stroke-width="2" />
  <circle cx="6" cy="6" r="3" fill="none" stroke="#475569" stroke-width="2" />
  <line x1="8.5" y1="16" x2="20" y2="5" stroke="#475569" stroke-width="2" stroke-linecap="round" />
  <line x1="8.5" y1="8" x2="20" y2="19" stroke="#475569" stroke-width="2" stroke-linecap="round" />
  <circle cx="13" cy="12" r="1.5" fill="#3B82F6" />
</svg>""",

    "copy.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <!-- Back document -->
  <rect x="8" y="3" width="12" height="14" rx="2" fill="#E2E8F0" stroke="#64748B" stroke-width="1.5" />
  <!-- Front document -->
  <rect x="4" y="7" width="12" height="14" rx="2" fill="#FFFFFF" stroke="#3B82F6" stroke-width="1.8" />
  <line x1="7" y1="11" x2="13" y2="11" stroke="#93C5FD" stroke-width="1.5" stroke-linecap="round" />
  <line x1="7" y1="14" x2="13" y2="14" stroke="#93C5FD" stroke-width="1.5" stroke-linecap="round" />
  <line x1="7" y1="17" x2="11" y2="17" stroke="#93C5FD" stroke-width="1.5" stroke-linecap="round" />
</svg>""",

    "paste.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <!-- Clipboard board -->
  <rect x="5" y="5" width="14" height="16" rx="2" fill="#F8FAFC" stroke="#64748B" stroke-width="1.6" />
  <!-- Clipboard clip -->
  <rect x="8.5" y="2" width="7" height="4" rx="1" fill="#475569" />
  <!-- Content paper -->
  <rect x="8" y="8" width="11" height="12" rx="1.5" fill="#FFFFFF" stroke="#8B5CF6" stroke-width="1.5" />
  <line x1="10.5" y1="11.5" x2="16.5" y2="11.5" stroke="#C4B5FD" stroke-width="1.4" stroke-linecap="round" />
  <line x1="10.5" y1="14.5" x2="16.5" y2="14.5" stroke="#C4B5FD" stroke-width="1.4" stroke-linecap="round" />
  <line x1="10.5" y1="17.5" x2="14" y2="17.5" stroke="#C4B5FD" stroke-width="1.4" stroke-linecap="round" />
</svg>""",

    "find.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <radialGradient id="glassGlow" cx="40%" cy="40%" r="60%">
      <stop offset="0%" stop-color="#E0F2FE" />
      <stop offset="60%" stop-color="#BAE6FD" />
      <stop offset="100%" stop-color="#38BDF8" stop-opacity="0.6" />
    </radialGradient>
  </defs>
  <!-- Lens circle -->
  <circle cx="10.5" cy="10.5" r="6.5" fill="url(#glassGlow)" stroke="#0284C7" stroke-width="2.2" />
  <!-- Glass reflection highlight -->
  <path d="M 7 8 A 4.5 4.5 0 0 1 12 6" stroke="#FFFFFF" stroke-width="1.5" stroke-linecap="round" fill="none" />
  <!-- Handle -->
  <path d="M 15.5 15.5 L 21 21" stroke="#0369A1" stroke-width="2.8" stroke-linecap="round" />
</svg>""",

    "compile.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <linearGradient id="gearAmber" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FBBF24" />
      <stop offset="50%" stop-color="#F59E0B" />
      <stop offset="100%" stop-color="#D97706" />
    </linearGradient>
    <filter id="gearGlow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1" stdDeviation="1" flood-color="#D97706" flood-opacity="0.3" />
    </filter>
  </defs>
  <!-- Modern Gear (Compile) -->
  <path d="M 12 15 C 10.34 15 9 13.66 9 12 C 9 10.34 10.34 9 12 9 C 13.66 9 15 10.34 15 12 C 15 13.66 13.66 15 12 15 Z" fill="#78350F" />
  <path d="M 19.4 13 C 19.45 12.67 19.5 12.34 19.5 12 C 19.5 11.66 19.45 11.33 19.4 11 L 21.5 9.4 C 21.7 9.25 21.75 8.95 21.6 8.75 L 19.6 5.3 C 19.45 5.1 19.2 5 18.95 5.1 L 16.5 6.1 C 15.95 5.7 15.4 5.35 14.8 5.1 L 14.4 2.5 C 14.35 2.2 14.1 2 13.85 2 L 10.15 2 C 9.9 2 9.65 2.2 9.6 2.5 L 9.2 5.1 C 8.6 5.35 8.05 5.7 7.5 6.1 L 5.05 5.1 C 4.8 5 4.55 5.1 4.4 5.3 L 2.4 8.75 C 2.25 8.95 2.3 9.25 2.5 9.4 L 4.6 11 C 4.55 11.33 4.5 11.66 4.5 12 C 4.5 12.34 4.55 12.67 4.6 13 L 2.5 14.6 C 2.3 14.75 2.25 15.05 2.4 15.25 L 4.4 18.7 C 4.55 18.9 4.8 19 5.05 18.9 L 7.5 17.9 C 8.05 18.3 8.6 18.65 9.2 18.9 L 9.6 21.5 C 9.65 21.8 9.9 22 10.15 22 L 13.85 22 C 14.1 22 14.35 21.8 14.4 21.5 L 14.8 18.9 C 15.4 18.65 15.95 18.3 16.5 17.9 L 18.95 18.9 C 19.2 19 19.45 18.9 19.6 18.7 L 21.6 15.25 C 21.75 15.05 21.7 14.75 21.5 14.6 L 19.4 13 Z M 12 16.5 C 9.5 16.5 7.5 14.5 7.5 12 C 7.5 9.5 9.5 7.5 12 7.5 C 14.5 7.5 16.5 9.5 16.5 12 C 16.5 14.5 14.5 16.5 12 16.5 Z" 
        fill="url(#gearAmber)" filter="url(#gearGlow)" />
</svg>""",

    "run.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <linearGradient id="greenPlay" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34D399" />
      <stop offset="50%" stop-color="#10B981" />
      <stop offset="100%" stop-color="#059669" />
    </linearGradient>
    <filter id="playShadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="1.5" stdDeviation="1.5" flood-color="#059669" flood-opacity="0.4" />
    </filter>
  </defs>
  <!-- Circular container soft background -->
  <circle cx="12" cy="12" r="10" fill="#ECFDF5" stroke="#A7F3D0" stroke-width="1.2" />
  <!-- Glossy Play Triangle -->
  <path d="M 9.5 7.5 C 8.7 7.0 7.8 7.5 7.8 8.4 L 7.8 15.6 C 7.8 16.5 8.7 17.0 9.5 16.5 L 16.2 12.8 C 17 12.3 17 11.7 16.2 11.2 Z" 
        fill="url(#greenPlay)" filter="url(#playShadow)" />
</svg>""",

    "compile_run.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <linearGradient id="gearHalve" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#FBBF24" />
      <stop offset="100%" stop-color="#D97706" />
    </linearGradient>
    <linearGradient id="fastPlay" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#34D399" />
      <stop offset="100%" stop-color="#059669" />
    </linearGradient>
  </defs>
  <!-- Gear on the left -->
  <path d="M 8 3 L 9.2 5.5 C 8.6 6 8.1 6.6 7.7 7.2 L 5 6.4 L 3.8 8.4 L 6 10 C 5.9 10.6 5.9 11.4 6 12 L 3.8 13.6 L 5 15.6 L 7.7 14.8 C 8.1 15.4 8.6 16 9.2 16.5 L 8 19 L 10.5 19.5 L 11.5 17.2 C 12 17.3 12.5 17.3 13 17.2 L 13 15 C 11.3 15 10 13.7 10 12 C 10 10.3 11.3 9 13 9 L 13 6.8 C 12.5 6.7 12 6.7 11.5 6.8 L 10.5 4.5 Z" 
        fill="url(#gearHalve)" />
  <!-- Prominent Green Play Arrow on Right -->
  <path d="M 12 7 C 11.4 6.6 10.8 7 10.8 7.7 L 10.8 16.3 C 10.8 17 11.4 17.4 12 17 L 19.5 12.7 C 20.1 12.3 20.1 11.7 19.5 11.3 Z" 
        fill="url(#fastPlay)" stroke="#FFFFFF" stroke-width="1.2" stroke-linejoin="round" />
  <!-- Speed lines -->
  <line x1="19" y1="6" x2="22" y2="6" stroke="#10B981" stroke-width="1.5" stroke-linecap="round" />
  <line x1="20" y1="18" x2="23" y2="18" stroke="#10B981" stroke-width="1.5" stroke-linecap="round" />
</svg>""",

    "rebuild.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <linearGradient id="rebuildGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38BDF8" />
      <stop offset="100%" stop-color="#2563EB" />
    </linearGradient>
  </defs>
  <!-- Circular Arrow 1 -->
  <path d="M 20 12 A 8 8 0 0 1 6.5 18 L 8 16.5 M 6.5 18 L 3 18 L 3 14.5" 
        fill="none" stroke="url(#rebuildGrad)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
  <!-- Circular Arrow 2 -->
  <path d="M 4 12 A 8 8 0 0 1 17.5 6 L 16 7.5 M 17.5 6 L 21 6 L 21 9.5" 
        fill="none" stroke="url(#rebuildGrad)" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round" />
  <!-- Central golden mini gear -->
  <circle cx="12" cy="12" r="2.5" fill="#F59E0B" />
</svg>""",

    "settings.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <!-- Equalizer / Config sliders -->
  <line x1="4" y1="21" x2="4" y2="14" stroke="#475569" stroke-width="2" stroke-linecap="round" />
  <line x1="4" y1="10" x2="4" y2="3" stroke="#475569" stroke-width="2" stroke-linecap="round" />
  <circle cx="4" cy="12" r="2.5" fill="#3B82F6" stroke="#1D4ED8" stroke-width="1" />

  <line x1="12" y1="21" x2="12" y2="12" stroke="#475569" stroke-width="2" stroke-linecap="round" />
  <line x1="12" y1="8" x2="12" y2="3" stroke="#475569" stroke-width="2" stroke-linecap="round" />
  <circle cx="12" cy="10" r="2.5" fill="#3B82F6" stroke="#1D4ED8" stroke-width="1" />

  <line x1="20" y1="21" x2="20" y2="16" stroke="#475569" stroke-width="2" stroke-linecap="round" />
  <line x1="20" y1="12" x2="20" y2="3" stroke="#475569" stroke-width="2" stroke-linecap="round" />
  <circle cx="20" cy="14" r="2.5" fill="#3B82F6" stroke="#1D4ED8" stroke-width="1" />
</svg>""",

    "clean.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <!-- Eraser / Sparkle Broom -->
  <path d="M 19.5 4.5 L 14.5 9.5 M 17 2 L 22 7 L 19.5 9.5 L 14.5 4.5 Z" fill="#8B5CF6" />
  <path d="M 14.5 9.5 L 8 16 L 3 16 L 8 11 Z" fill="#C4B5FD" stroke="#7C3AED" stroke-width="1" />
  <!-- Sparkles -->
  <path d="M 6 5 L 7 7 L 9 8 L 7 9 L 6 11 L 5 9 L 3 8 L 5 7 Z" fill="#FBBF24" />
  <path d="M 16 17 L 16.6 18.2 L 18 18.8 L 16.6 19.4 L 16 21 L 15.4 19.4 L 14 18.8 L 15.4 18.2 Z" fill="#38BDF8" />
</svg>""",

    "stop.svg": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24">
  <defs>
    <linearGradient id="stopGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#F87171" />
      <stop offset="100%" stop-color="#DC2626" />
    </linearGradient>
  </defs>
  <!-- Stop rounded square -->
  <rect x="4" y="4" width="16" height="16" rx="3.5" fill="url(#stopGrad)" stroke="#B91C1C" stroke-width="1.2" />
  <!-- Inner soft border -->
  <rect x="6.5" y="6.5" width="11" height="11" rx="2" fill="none" stroke="#FFFFFF" stroke-width="1.2" stroke-opacity="0.6" />
</svg>"""
}

for name, content in SVGS.items():
    path = os.path.join(ICONS_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Created: {path}")

# Verify icons load
app = QApplication(sys.argv)
for name in SVGS.keys():
    path = os.path.join(ICONS_DIR, name)
    icon = QIcon(path)
    pix = icon.pixmap(32, 32)
    if pix.isNull():
        print(f"FAILED to load: {name}")
    else:
        print(f"SUCCESS {name}: {pix.width()}x{pix.height()}")

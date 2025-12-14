# Frontend Development Guide

## Overview

The frontend is a React 18 application built with TypeScript and Vite. It provides a dispatcher interface for handling emergency calls, including real-time audio transcription, incident classification, and case management.

## Tech Stack

| Technology | Version | Purpose |
|------------|---------|---------|
| React | 18.3.1 | UI framework |
| TypeScript | 5.7.2 | Type-safe JavaScript |
| Vite | 6.0.3 | Build tool & dev server |
| Tailwind CSS | 3.4.15 | Utility-first CSS |
| PostCSS | 8.4.49 | CSS processing |

---

## Project Structure

```
view/
├── src/
│   ├── App.tsx                    # Main application component
│   ├── main.tsx                   # Entry point
│   ├── components/
│   │   ├── ErrorBoundary.tsx      # Error handling wrapper
│   │   └── Layout.tsx             # Main layout component
│   ├── context/
│   │   ├── LanguageContext.tsx    # i18n context (ar/en)
│   │   └── ThemeContext.tsx       # Theme context (light/dark)
│   ├── hooks/                     # Custom React hooks
│   └── services/                  # API client services
│
├── realtime_incident/             # Real-time call handling view
│   ├── RealtimeIncidentView.tsx   # Main view component
│   ├── components/
│   │   ├── AnalysisPanel.tsx      # AI analysis display
│   │   ├── CallFooter.tsx         # Call controls
│   │   ├── CallHeader.tsx         # Call status header
│   │   ├── QuickNotesPanel.tsx    # Operator notes
│   │   ├── QuickTagsPanel.tsx     # Quick tags
│   │   ├── StatusLogPanel.tsx     # Status timeline
│   │   ├── SuggestedActionsPanel.tsx
│   │   ├── TranscriptionPanel.tsx # Live transcription
│   │   └── VoiceControlPanel.tsx  # Audio controls
│   └── index.ts                   # Exports
│
├── accepted_incident/             # Reviewed incident view
│   ├── AcceptedIncidentView.tsx
│   └── components/
│
├── incidents_list/                # Incident list view
│   ├── IncidentsListView.tsx
│   └── components/
│
├── shared/                        # Reusable components
│   ├── components/                # UI components
│   │   ├── ActionList.tsx
│   │   ├── AudioPlayer.tsx
│   │   ├── Badge.tsx
│   │   ├── Button.tsx
│   │   ├── Card.tsx
│   │   ├── Checkbox.tsx
│   │   ├── FeedbackButtons.tsx
│   │   ├── FilterChips.tsx
│   │   ├── HighlightedText.tsx
│   │   ├── InfoRow.tsx
│   │   ├── Input.tsx
│   │   ├── ListItem.tsx
│   │   ├── LiveIndicator.tsx
│   │   ├── MapPreview.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── RadioGroup.tsx
│   │   ├── Select.tsx
│   │   ├── SeveritySelector.tsx
│   │   ├── Slider.tsx
│   │   ├── StatusTimeline.tsx
│   │   ├── Tag.tsx
│   │   ├── TextArea.tsx
│   │   ├── Timer.tsx
│   │   ├── Toggle.tsx
│   │   └── index.ts               # Component exports
│   │
│   ├── hooks/                     # Shared hooks
│   │   ├── useSelection.ts
│   │   ├── useTimer.ts
│   │   ├── useToggle.ts
│   │   └── index.ts
│   │
│   ├── icons/                     # Icon components
│   │   └── index.tsx
│   │
│   ├── types/                     # TypeScript types
│   │   └── index.ts
│   │
│   └── index.ts
│
└── i18n/                          # Internationalization
    └── translations/
```

---

## Views

### 1. Real-time Incident View (`realtime_incident/`)
Handles live emergency calls with:
- Live audio transcription display
- AI-powered analysis panel
- Quick tags for classification
- Voice controls (volume, translation toggle)
- Status timeline
- Operator notes

### 2. Accepted Incident View (`accepted_incident/`)
Displays reviewed incidents with:
- Full transcription
- AI confidence scores
- Operator notes history
- Location map preview
- Feedback buttons
- Transfer/close actions

### 3. Incidents List View (`incidents_list/`)
Dashboard showing all incidents with:
- Search and filters
- Quick filter chips (urgent, high, pending)
- Sortable table
- Bulk selection
- Detail panel
- Audio player

---

## Shared Components

### UI Components
| Component | Purpose |
|-----------|---------|
| `Button` | Primary button component |
| `Card` | Container with shadow |
| `Badge` | Status indicators |
| `Input` | Text input field |
| `Select` | Dropdown selector |
| `TextArea` | Multi-line text input |
| `Checkbox` | Checkbox input |
| `Toggle` | Toggle switch |
| `Slider` | Range slider |
| `RadioGroup` | Radio button group |

### Display Components
| Component | Purpose |
|-----------|---------|
| `AudioPlayer` | Audio playback controls |
| `HighlightedText` | Text with highlights |
| `LiveIndicator` | Live status dot |
| `MapPreview` | Location map thumbnail |
| `ProgressBar` | Progress indicator |
| `StatusTimeline` | Status history timeline |
| `Timer` | Time display/countdown |
| `Tag` | Tag/chip component |

### Composite Components
| Component | Purpose |
|-----------|---------|
| `ActionList` | List of actions |
| `FeedbackButtons` | Yes/No feedback |
| `FilterChips` | Quick filter buttons |
| `InfoRow` | Label + value row |
| `ListItem` | List item with checkbox |
| `SeveritySelector` | Severity level picker |

---

## Context Providers

### LanguageContext
Manages Arabic/English language switching.

```tsx
import { useLanguage } from '../context/LanguageContext';

function MyComponent() {
  const { language, setLanguage, t } = useLanguage();

  return (
    <div dir={language === 'ar' ? 'rtl' : 'ltr'}>
      {t('greeting')}
    </div>
  );
}
```

### ThemeContext
Manages light/dark theme.

```tsx
import { useTheme } from '../context/ThemeContext';

function MyComponent() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button onClick={toggleTheme}>
      Current: {theme}
    </button>
  );
}
```

---

## Custom Hooks

### useTimer
Manages countdown/timer logic.

```tsx
const { time, isRunning, start, stop, reset } = useTimer(initialSeconds);
```

### useSelection
Manages list selection state.

```tsx
const { selected, selectAll, selectItem, isSelected } = useSelection(items);
```

### useToggle
Simple boolean toggle.

```tsx
const [isOpen, toggle] = useToggle(false);
```

---

## TypeScript Types

### Core Types (`shared/types/index.ts`)

```typescript
// Severity levels
type SeverityLevel = 'critical' | 'high' | 'medium' | 'low';

// Incident status
type IncidentStatus = 'new' | 'pending' | 'in_progress' | 'resolved' | 'closed';

// Authority types
type AuthorityType = 'traffic' | 'civil_defense' | 'ambulance' | 'police' | 'municipality';

// Select option
interface SelectOption {
  value: string;
  label: string;
}

// Audio player state
interface AudioPlayerState {
  isPlaying: boolean;
  currentTime: number;
  duration: number;
  volume: number;
  isMuted: boolean;
}

// Location
interface Location {
  address: string;
  latitude: number;
  longitude: number;
  mapUrl: string;
}

// Note
interface Note {
  id: string;
  content: string;
  createdAt: string;
  createdBy: string;
}
```

---

## Development

### Prerequisites
- Node.js 18+
- npm or yarn

### Setup
```bash
cd view
npm install
```

### Development Server
```bash
npm run dev
```
The app runs at http://localhost:5173 with hot reload.

### Build
```bash
npm run build
```
Output goes to `dist/` directory.

### Type Checking
```bash
npm run typecheck
```

### Linting
```bash
npm run lint
```

---

## API Integration

The frontend communicates with the backend via:

### REST API
- Base URL: `http://localhost:8000/api`
- Configured in `vite.config.ts` to proxy `/api` to backend

### WebSocket
- URL: `ws://localhost:8000/ws/audio`
- Used for real-time audio streaming

### Example API Call
```typescript
// In services/api.ts
export async function getCases() {
  const response = await fetch('/api/cases');
  return response.json();
}

export async function submitFeedback(caseId: string, feedback: Feedback) {
  const response = await fetch('/api/operator-feedback', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ case_id: caseId, ...feedback }),
  });
  return response.json();
}
```

---

## Styling with Tailwind

### RTL Support
The app supports RTL (right-to-left) for Arabic:

```tsx
<div className="text-right rtl:text-left">
  {/* Content */}
</div>
```

### Dark Mode
Use Tailwind's dark mode classes:

```tsx
<div className="bg-white dark:bg-gray-800">
  {/* Content */}
</div>
```

### Common Patterns
```tsx
// Card
<div className="bg-white rounded-lg shadow-md p-4">

// Button
<button className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600">

// Input
<input className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500">

// Badge
<span className="px-2 py-1 text-xs font-medium bg-red-100 text-red-800 rounded-full">
```

---

## File Naming Conventions

| Type | Convention | Example |
|------|------------|---------|
| Components | PascalCase | `AudioPlayer.tsx` |
| Hooks | camelCase with `use` | `useTimer.ts` |
| Types | PascalCase | `types/index.ts` |
| Utilities | camelCase | `formatDate.ts` |
| Views | PascalCase with `View` | `RealtimeIncidentView.tsx` |

---

## Adding a New Component

1. Create component file in appropriate directory
2. Export from `index.ts`
3. Add TypeScript props interface
4. Include JSDoc documentation

```tsx
// shared/components/NewComponent.tsx

interface NewComponentProps {
  /** Primary label text */
  label: string;
  /** Click handler */
  onClick?: () => void;
}

/**
 * NewComponent - Description of what it does
 */
export const NewComponent: React.FC<NewComponentProps> = ({ label, onClick }) => {
  return (
    <div onClick={onClick} className="...">
      {label}
    </div>
  );
};
```

---

## Adding a New View

1. Create directory under `view/`
2. Create main view component
3. Create `components/` subdirectory for sub-components
4. Export from `index.ts`
5. Add route in `App.tsx`

```
view/
└── new_view/
    ├── NewView.tsx
    ├── components/
    │   ├── SubComponent.tsx
    │   └── index.ts
    └── index.ts
```

---

## Troubleshooting

### Common Issues

**Vite not starting:**
```bash
rm -rf node_modules
npm install
npm run dev
```

**TypeScript errors:**
```bash
npm run typecheck
# Fix any type errors shown
```

**Tailwind not applying:**
- Check `tailwind.config.js` content paths
- Ensure PostCSS is configured

**API not connecting:**
- Check backend is running on port 8000
- Verify Vite proxy config in `vite.config.ts`

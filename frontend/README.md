# Financial Intelligence Frontend

World-class Next.js frontend with 3D effects and animations for the Financial Intelligence System.

## Features

- **3D Visualizations**: React Three Fiber with animated 3D elements
- **Smooth Animations**: Framer Motion for fluid transitions
- **Modern UI**: Tailwind CSS with custom dark theme
- **Real-time Updates**: WebSocket integration for live data
- **Responsive Design**: Mobile-first approach
- **Glassmorphism**: Modern glass effect UI components
- **Neon Glows**: Eye-catching visual effects
- **Gradient Text**: Beautiful text gradients

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **3D Graphics**: Three.js, React Three Fiber, React Three Drei
- **Animations**: Framer Motion
- **Icons**: Lucide React
- **Charts**: Recharts
- **API Client**: Axios
- **State Management**: Zustand
- **Real-time**: Socket.io Client

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Environment Variables

Create a `.env.local` file:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. Run Development Server

```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
npm start
```

## Project Structure

```
frontend/
├── app/
│   ├── layout.tsx          # Root layout
│   ├── page.tsx            # Landing page
│   └── globals.css         # Global styles
├── components/
│   └── Dashboard.tsx       # Main dashboard
├── lib/
│   └── api.ts             # API client
├── public/                # Static assets
├── package.json
├── next.config.js
├── tailwind.config.ts
└── tsconfig.json
```

## API Integration

The frontend connects to the Python FastAPI backend at `http://localhost:8000`.

### Available Endpoints

- `GET /intelligence/{symbol}` - Composite intelligence score
- `GET /macro` - Macro intelligence overview
- `GET /macro/scenarios` - Macro scenarios
- `GET /multi-asset/{symbol}` - Multi-asset analysis
- `GET /scenarios/{symbol}` - Asset scenarios
- `GET /correlation` - Correlation matrix
- `GET /allocation/{strategy}` - Asset allocation
- `GET /risk-sentiment` - Risk sentiment

## 3D Effects

The frontend includes:

- **Animated 3D Sphere**: Distorted mesh with auto-rotation
- **Floating Elements**: Smooth floating animations
- **Neon Glows**: Glowing effects on interactive elements
- **3D Card Effects**: Cards that rotate on hover
- **Particle Background**: Dynamic particle system

## Animations

- **Page Transitions**: Smooth fade-in and slide animations
- **Hover Effects**: Scale and color transitions
- **Loading States**: Spinner and pulse animations
- **Scroll Animations**: Elements animate as they enter viewport

## Custom Components

### Glass Effect
```tsx
<div className="glass rounded-2xl p-6">
  Content
</div>
```

### Neon Glow
```tsx
<div className="neon-glow">
  Content
</div>
```

### Gradient Text
```tsx
<h1 className="gradient-text">
  Text
</h1>
```

### 3D Card
```tsx
<div className="card-3d">
  <div className="card-3d-inner">
    Content
  </div>
</div>
```

## Color Palette

- **Background**: #0B0F14
- **Panel BG**: #111827
- **Border**: #1F2937
- **Text Primary**: #E5E7EB
- **Text Secondary**: #9CA3AF
- **Bullish**: #22C55E
- **Bearish**: #EF4444
- **Neutral**: #F59E0B
- **Accent**: #3B82F6

## Performance Optimization

- **Code Splitting**: Automatic with Next.js
- **Image Optimization**: Next.js Image component
- **Lazy Loading**: Components load on demand
- **Tree Shaking**: Unused code removed
- **Minification**: Production builds are minified

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Deployment

### Vercel (Recommended)

```bash
npm install -g vercel
vercel
```

### Netlify

```bash
npm run build
# Deploy the .next folder
```

### Docker

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]
```

## Troubleshooting

### Dependencies Not Found

If you see errors about missing modules, run:

```bash
npm install
```

### Tailwind Not Working

Ensure `tailwind.config.ts` is in the root and `globals.css` has the directives.

### 3D Not Rendering

Check that Three.js and React Three Fiber are installed:

```bash
npm install three @react-three/fiber @react-three/drei
```

## Development Tips

1. **Hot Reload**: Changes reflect automatically
2. **TypeScript**: Enjoy type safety
3. **ESLint**: Code quality checks
4. **Prettier**: Code formatting (optional)

## Future Enhancements

- [ ] WebSocket real-time updates
- [ ] More 3D visualizations
- [ ] Advanced chart components
- [ ] User authentication
- [ ] Portfolio management UI
- [ ] Scenario visualization
- [ ] Correlation heatmap
- [ ] Mobile app (React Native)

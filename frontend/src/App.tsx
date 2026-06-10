import { Analytics } from '@vercel/analytics/react';
import { DashboardPage } from './pages/DashboardPage';

export default function App() {
  return (
    <>
      <DashboardPage />
      <Analytics />
    </>
  );
}

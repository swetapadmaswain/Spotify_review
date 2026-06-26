import { useEffect, useState } from 'react';
import {
  api, InsightSummary, SentimentTrend, Pattern, Segment, Recommendation,
} from './api/client';
import SummaryCards from './components/SummaryCards';
import SentimentTrendChart from './components/SentimentTrendChart';
import KeyFindingsList from './components/KeyFindingsList';
import PatternDashboard from './components/PatternDashboard';
import SegmentDashboard from './components/SegmentDashboard';
import RecommendationsList from './components/RecommendationsList';

type Tab = 'executive' | 'patterns' | 'segments' | 'recommendations';

export default function App() {
  const [tab, setTab] = useState<Tab>('executive');
  const [summary, setSummary] = useState<InsightSummary | null>(null);
  const [trends, setTrends] = useState<SentimentTrend[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      api.getSummary(),
      api.getSentimentTrends(),
      api.getPatterns(),
      api.getSegments(),
      api.getRecommendations(),
    ])
      .then(([s, t, p, seg, rec]) => {
        setSummary(s);
        setTrends(t);
        setPatterns(p);
        setSegments(seg);
        setRecommendations(rec);
      })
      .catch((e) => setError(e.message));
  }, []);

  const tabs: { id: Tab; label: string }[] = [
    { id: 'executive', label: 'Executive' },
    { id: 'patterns', label: 'Patterns' },
    { id: 'segments', label: 'Segments' },
    { id: 'recommendations', label: 'Recommendations' },
  ];

  return (
    <div className="min-h-screen bg-dark">
      <header className="border-b border-white/10 px-6 py-4 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">
            <span className="text-spotify">Spotify</span> Discovery Insights
          </h1>
          <p className="text-muted text-sm">AI-Powered Review Discovery Engine</p>
        </div>
      </header>

      <nav className="flex gap-2 px-6 py-3 border-b border-white/10">
        {tabs.map((t) => (
          <button
            key={t.id}
            onClick={() => setTab(t.id)}
            className={`px-4 py-2 rounded-full text-sm font-medium transition ${
              tab === t.id ? 'bg-spotify text-black' : 'text-muted hover:text-white'
            }`}
          >
            {t.label}
          </button>
        ))}
      </nav>

      <main className="p-6 max-w-7xl mx-auto space-y-6">
        {error && (
          <div className="bg-red-500/20 text-red-300 p-4 rounded-lg">
            Failed to load data: {error}. Ensure the API is running on port 8000.
          </div>
        )}

        {tab === 'executive' && (
          <>
            <SummaryCards data={summary} />
            <SentimentTrendChart data={trends} />
            <div className="grid md:grid-cols-2 gap-6">
              <KeyFindingsList findings={summary?.key_findings || []} />
              <KeyFindingsList findings={summary?.top_unmet_needs || []} />
            </div>
          </>
        )}

        {tab === 'patterns' && <PatternDashboard data={patterns} />}
        {tab === 'segments' && <SegmentDashboard data={segments} />}
        {tab === 'recommendations' && <RecommendationsList data={recommendations} />}
      </main>
    </div>
  );
}

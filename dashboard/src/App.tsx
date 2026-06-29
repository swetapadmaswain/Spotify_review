import { useCallback, useEffect, useState } from 'react';
import {
  api, InsightSummary, SentimentTrend, TopicEvolution, Pattern, Segment,
  Recommendation, UnmetNeed, RootCause, RoadmapItem,
} from './api/client';
import {
  computeDiscoveryScore, buildAINarrative, dominantSentiment,
} from './utils/insights';
import IntelligenceHeader from './components/IntelligenceHeader';
import SummaryCards from './components/SummaryCards';
import SentimentTrendChart from './components/SentimentTrendChart';
import SentimentDistribution from './components/SentimentDistribution';
import TopicEvolutionChart from './components/TopicEvolutionChart';
import KeyFindingsList from './components/KeyFindingsList';
import PatternDashboard from './components/PatternDashboard';
import SegmentDashboard from './components/SegmentDashboard';
import RootCausePanel from './components/RootCausePanel';
import UnmetNeedsPanel from './components/UnmetNeedsPanel';
import RecommendationsPanel from './components/RecommendationsPanel';
import Button from './components/ui/Button';

type Tab = 'executive' | 'patterns' | 'segments' | 'insights' | 'recommendations' | 'reports';

const TABS: { id: Tab; label: string; icon: string; desc: string }[] = [
  { id: 'executive', label: 'Executive', icon: '📊', desc: 'Health score & overview' },
  { id: 'patterns', label: 'Patterns', icon: '🔍', desc: 'Behavioral signals' },
  { id: 'segments', label: 'Segments', icon: '👥', desc: 'User clusters' },
  { id: 'insights', label: 'Deep Insights', icon: '🧠', desc: 'Root causes & gaps' },
  { id: 'recommendations', label: 'Actions', icon: '🎯', desc: 'Roadmap & strategy' },
  { id: 'reports', label: 'Reports', icon: '📄', desc: 'View & download reports' },
];

export default function App() {
  const [tab, setTab] = useState<Tab>('executive');
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [analyzing, setAnalyzing] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [summary, setSummary] = useState<InsightSummary | null>(null);
  const [trends, setTrends] = useState<SentimentTrend[]>([]);
  const [topicEvolution, setTopicEvolution] = useState<TopicEvolution[]>([]);
  const [sentimentDist, setSentimentDist] = useState<{ sentiment: string; count: number }[]>([]);
  const [patterns, setPatterns] = useState<Pattern[]>([]);
  const [segments, setSegments] = useState<Segment[]>([]);
  const [unmetNeeds, setUnmetNeeds] = useState<UnmetNeed[]>([]);
  const [rootCauses, setRootCauses] = useState<RootCause[]>([]);
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [reports, setReports] = useState<any[]>([]);
  const [analysisTimeout, setAnalysisTimeout] = useState(false);
  const [roadmap, setRoadmap] = useState<RoadmapItem[]>([]);

  const showToast = (msg: string) => {
    setToast(msg);
    setTimeout(() => setToast(null), 4000);
  };

  const loadData = useCallback(async (isRefresh = false) => {
    if (isRefresh) setRefreshing(true);
    else setLoading(true);
    setError(null);

    try {
      const [
        s, t, te, sd, p, seg, un, rc, rec, rm,
      ] = await Promise.all([
        api.getSummary(),
        api.getSentimentTrends(days),
        api.getTopicEvolution(days),
        api.getSentimentDistribution(),
        api.getPatterns(),
        api.getSegments(),
        api.getUnmetNeeds(),
        api.getRootCauses(),
        api.getRecommendations(),
        api.getRoadmap(),
      ]);
      setSummary(s);
      setTrends(t);
      setTopicEvolution(te);
      setSentimentDist(sd);
      setPatterns(p);
      setSegments(seg);
      setUnmetNeeds(un);
      setRootCauses(rc);
      setRecommendations(rec);
      setRoadmap(rm);
      setLastUpdated(new Date());
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : 'Failed to load data';
      setError(message);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [days]);

  useEffect(() => { loadData(); }, [loadData]);

  useEffect(() => {
    if (tab === 'reports') {
      loadReports();
    }
  }, [tab]);

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    try {
      await loadData(true);
      showToast('Data has been refreshed');
    } catch (e: any) {
      showToast('Failed to refresh data');
    } finally {
      setAnalyzing(false);
    }
  };

  const loadReports = async () => {
    try {
      const data = await api.getReports();
      setReports(data);
    } catch (e: any) {
      console.error('Failed to load reports:', e);
    }
  };

  const handleExportReport = async () => {
    try {
      showToast('Generating report...');
      const result = await api.generateReport();
      const report = result?.report;
      if (!report) {
        showToast('Report generated but no content returned');
        return;
      }

      const lines: string[] = [
        'SPOTIFY REVIEW DISCOVERY — INSIGHTS REPORT',
        '='.repeat(50),
        `Generated: ${new Date(report.generated_at).toLocaleString()}`,
        `Total Reviews Analyzed: ${report.total_reviews}`,
        '',
        'SENTIMENT BREAKDOWN',
        '-'.repeat(50),
        ...Object.entries(report.sentiment_breakdown).map(([k, v]) => `  ${k}: ${v}`),
        '',
        `PATTERNS IDENTIFIED: ${report.pattern_count}`,
        '-'.repeat(50),
        ...report.top_patterns.map((p, i) => `  ${i + 1}. ${p}`),
        '',
        `USER SEGMENTS: ${report.segment_count}`,
        '',
        'TOP UNMET NEEDS',
        '-'.repeat(50),
        ...report.top_unmet_needs.map((n, i) => `  ${i + 1}. ${n}`),
        '',
        'RECOMMENDATIONS',
        '-'.repeat(50),
        ...report.recommendations.map((r, i) => `  ${i + 1}. ${r}`),
      ];

      const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `spotify-insights-report-${new Date().toISOString().slice(0, 10)}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast('Report downloaded');
      await loadReports();
    } catch {
      showToast('Report generation failed');
    }
  };

  const handleDownloadReport = async (id: number) => {
    try {
      showToast('Loading report...');
      const report = await api.getReport(id);
      const content = report?.content;
      if (!content) {
        showToast('Report content not found');
        return;
      }

      const lines: string[] = [
        'SPOTIFY REVIEW DISCOVERY — INSIGHTS REPORT',
        '='.repeat(50),
        `Generated: ${new Date(content.generated_at).toLocaleString()}`,
        `Total Reviews Analyzed: ${content.total_reviews}`,
        '',
        'SENTIMENT BREAKDOWN',
        '-'.repeat(50),
        ...Object.entries(content.sentiment_breakdown).map(([k, v]) => `  ${k}: ${v}`),
        '',
        `PATTERNS IDENTIFIED: ${content.pattern_count}`,
        '-'.repeat(50),
        ...content.top_patterns.map((p: string, i: number) => `  ${i + 1}. ${p}`),
        '',
        `USER SEGMENTS: ${content.segment_count}`,
        '',
        'TOP UNMET NEEDS',
        '-'.repeat(50),
        ...content.top_unmet_needs.map((n: string, i: number) => `  ${i + 1}. ${n}`),
        '',
        'RECOMMENDATIONS',
        '-'.repeat(50),
        ...content.recommendations.map((r: string, i: number) => `  ${i + 1}. ${r}`),
      ];

      const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `spotify-insights-report-${id}-${new Date().toISOString().slice(0, 10)}.txt`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
      showToast('Report downloaded');
    } catch {
      showToast('Failed to download report');
    }
  };

  const score = computeDiscoveryScore(summary, sentimentDist);
  const narrative = buildAINarrative(summary, patterns, segments, unmetNeeds);
  const dominant = dominantSentiment(trends);

  return (
    <div className="min-h-screen bg-[#0a0a0a]">
      {/* Toast */}
      {toast && (
        <div className="fixed top-4 right-4 z-50 glass-card px-4 py-3 text-sm text-spotify border-spotify/30 animate-fade-in">
          {toast}
        </div>
      )}

      {/* Header */}
      <header className="border-b border-white/10 px-6 py-4">
        <div className="max-w-7xl mx-auto flex flex-col lg:flex-row lg:items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-extrabold tracking-tight">
              <span className="text-spotify">Spotify</span>{' '}
              <span className="text-white">Discovery Intelligence</span>
            </h1>
            <p className="text-muted text-sm mt-0.5">AI-Powered Review Discovery Engine · Phase 4 Dashboard</p>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button variant="secondary" loading={refreshing} onClick={() => loadData(true)}>
              ↻ Refresh Data
            </Button>
            <Button variant="secondary" onClick={handleExportReport}>
              📄 Export Report
            </Button>
          </div>
        </div>
      </header>

      {/* Tab nav */}
      <nav className="border-b border-white/10 px-6 py-3 overflow-x-auto">
        <div className="max-w-7xl mx-auto flex gap-2">
          {TABS.map((t) => (
            <button
              key={t.id}
              onClick={() => setTab(t.id)}
              className={`flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium transition-all whitespace-nowrap ${
                tab === t.id
                  ? 'bg-spotify text-black shadow-lg shadow-spotify/20'
                  : 'text-muted hover:text-white hover:bg-white/5'
              }`}
            >
              <span>{t.icon}</span>
              <span>{t.label}</span>
            </button>
          ))}
        </div>
      </nav>

      <main className="p-6 max-w-7xl mx-auto space-y-6">
        {error && (
          <div className="glass-card p-4 border-red-500/30 text-red-300 text-sm flex items-center justify-between">
            <span>⚠ {error}</span>
            <Button variant="ghost" onClick={() => loadData(true)}>Retry</Button>
          </div>
        )}

        {loading ? (
          <div className="flex flex-col items-center justify-center py-32 gap-4">
            <div className="w-12 h-12 border-3 border-spotify border-t-transparent rounded-full animate-spin" />
            <p className="text-muted">Loading intelligence data...</p>
          </div>
        ) : (
          <>
            {tab === 'executive' && (
              <div className="space-y-6 animate-fade-in">
                <IntelligenceHeader
                  score={score}
                  summary={summary}
                  narrative={narrative}
                  lastUpdated={lastUpdated}
                  dominantSentiment={dominant}
                />
                <SummaryCards data={summary} onCardClick={(t) => setTab(t as Tab)} />
                <div className="grid lg:grid-cols-3 gap-6">
                  <div className="lg:col-span-2">
                    <SentimentTrendChart data={trends} days={days} onDaysChange={setDays} />
                  </div>
                  <SentimentDistribution data={sentimentDist} />
                </div>
                <TopicEvolutionChart data={topicEvolution} />
                <div className="grid md:grid-cols-2 gap-6">
                  <KeyFindingsList title="Key Findings" findings={summary?.key_findings || []} />
                  <KeyFindingsList title="Top Unmet Needs" findings={summary?.top_unmet_needs || []} variant="needs" />
                </div>
              </div>
            )}

            {tab === 'patterns' && <PatternDashboard data={patterns} />}
            {tab === 'segments' && <SegmentDashboard data={segments} />}

            {tab === 'insights' && (
              <div className="space-y-6 animate-fade-in">
                <RootCausePanel data={rootCauses} />
                <UnmetNeedsPanel data={unmetNeeds} />
                <TopicEvolutionChart data={topicEvolution} />
              </div>
            )}

            {tab === 'recommendations' && (
              <RecommendationsPanel recommendations={recommendations} roadmap={roadmap} />
            )}

            {tab === 'reports' && (
              <div className="space-y-6 animate-fade-in">
                <h2 className="text-2xl font-bold text-white">Reports</h2>
                <div className="grid gap-4">
                  {reports.map((r) => (
                    <div key={r.id} className="glass-card p-4 flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">Report #{r.id}</p>
                        <p className="text-muted text-sm">
                          {r.report_type} · {r.template_type} · {new Date(r.created_at).toLocaleString()}
                        </p>
                      </div>
                      <Button onClick={() => handleDownloadReport(r.id)}>Download</Button>
                    </div>
                  ))}
                  {reports.length === 0 && (
                    <div className="glass-card p-8 text-center">
                      <p className="text-muted">No reports generated yet</p>
                    </div>
                  )}
                </div>
              </div>
            )}
          </>
        )}
      </main>

      <footer className="border-t border-white/10 px-6 py-4 text-center text-xs text-muted">
        Spotify Review Discovery Engine · {patterns.length} patterns · {segments.length} segments · {recommendations.length} recommendations
      </footer>
    </div>
  );
}

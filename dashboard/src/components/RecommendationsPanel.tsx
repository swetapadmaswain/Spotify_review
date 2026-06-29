import { useState } from 'react';
import { Recommendation, RoadmapItem } from '../api/client';
import Card from './ui/Card';
import Badge from './ui/Badge';
import Button from './ui/Button';

interface Props {
  recommendations: Recommendation[];
  roadmap: RoadmapItem[];
}

const priorityVariant: Record<string, 'danger' | 'warning' | 'success'> = {
  high: 'danger',
  medium: 'warning',
  low: 'success',
};

const complexityOrder: Record<string, number> = { 'low': 1, 'medium': 2, 'high': 3 };

export default function RecommendationsPanel({ recommendations, roadmap }: Props) {
  const [expanded, setExpanded] = useState<number | null>(0);
  const [view, setView] = useState<'recs' | 'roadmap'>('recs');
  const [filter, setFilter] = useState<'all' | 'high' | 'medium' | 'low'>('all');

  const filteredRecs = filter === 'all' 
    ? recommendations 
    : recommendations.filter(r => r.priority === filter);

  const sortedRecs = [...filteredRecs].sort((a, b) => {
    const priorityScore: Record<string, number> = { high: 3, medium: 2, low: 1 };
    const priorityDiff = priorityScore[b.priority] - priorityScore[a.priority];
    if (priorityDiff !== 0) return priorityDiff;
    return (complexityOrder[a.complexity] || 2) - (complexityOrder[b.complexity] || 2);
  });

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Explanation Header */}
      <Card className="bg-gradient-to-r from-spotify/10 to-transparent border-spotify/20">
        <h3 className="text-lg font-semibold mb-2">🎯 Actions & Roadmap</h3>
        <p className="text-sm text-muted mb-3">
          Actionable recommendations based on user feedback analysis. These are prioritized by impact and effort to help you make data-driven decisions.
        </p>
        <div className="grid md:grid-cols-3 gap-3 text-xs">
          <div className="p-2 rounded bg-white/5">
            <strong className="text-red-400">High Priority:</strong> Critical issues
          </div>
          <div className="p-2 rounded bg-white/5">
            <strong className="text-yellow-400">Medium Priority:</strong> Important improvements
          </div>
          <div className="p-2 rounded bg-white/5">
            <strong className="text-green-400">Low Priority:</strong> Nice to have
          </div>
        </div>
      </Card>

      {/* View Toggle */}
      <div className="flex gap-2">
        <Button variant={view === 'recs' ? 'primary' : 'ghost'} onClick={() => setView('recs')}>
          📋 Recommendations ({recommendations.length})
        </Button>
        <Button variant={view === 'roadmap' ? 'primary' : 'ghost'} onClick={() => setView('roadmap')}>
          📅 Product Roadmap ({roadmap.length})
        </Button>
      </div>

      {view === 'recs' && (
        <div className="space-y-4">
          {/* Priority Filter */}
          <div className="flex flex-wrap gap-2">
            <Button
              variant={filter === 'all' ? 'primary' : 'ghost'}
              onClick={() => setFilter('all')}
            >
              All ({recommendations.length})
            </Button>
            <Button
              variant={filter === 'high' ? 'primary' : 'ghost'}
              onClick={() => setFilter('high')}
            >
              🔥 High ({recommendations.filter(r => r.priority === 'high').length})
            </Button>
            <Button
              variant={filter === 'medium' ? 'primary' : 'ghost'}
              onClick={() => setFilter('medium')}
            >
              ⚡ Medium ({recommendations.filter(r => r.priority === 'medium').length})
            </Button>
            <Button
              variant={filter === 'low' ? 'primary' : 'ghost'}
              onClick={() => setFilter('low')}
            >
              📌 Low ({recommendations.filter(r => r.priority === 'low').length})
            </Button>
          </div>

          {sortedRecs.length === 0 ? (
            <Card><p className="text-muted text-sm">No recommendations found for this filter.</p></Card>
          ) : (
            sortedRecs.map((rec, i) => (
              <Card key={i} className={expanded === i ? 'border-spotify/30' : ''}>
                <button
                  className="w-full text-left"
                  onClick={() => setExpanded(expanded === i ? null : i)}
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-2">
                        <h4 className="font-semibold">{rec.title}</h4>
                        <Badge label={rec.priority} variant={priorityVariant[rec.priority] || 'default'} />
                      </div>
                      <div className="flex flex-wrap gap-2">
                        <Badge label={rec.category} variant="info" />
                        <Badge label={`${rec.complexity} effort`} variant="default" />
                        <Badge label={`${rec.expected_impact} impact`} variant="warning" />
                      </div>
                    </div>
                    <span className="text-muted">{expanded === i ? '▲' : '▼'}</span>
                  </div>
                </button>
                {expanded === i && (
                  <div className="mt-4 pt-4 border-t border-white/10 space-y-4 animate-fade-in">
                    {/* Issue Description */}
                    <div className="p-3 rounded-lg bg-red-500/10 border border-red-500/20">
                      <p className="text-xs text-red-400 mb-1 font-semibold">🚨 THE PROBLEM</p>
                      <p className="text-sm text-white/90 leading-relaxed">{rec.description}</p>
                    </div>

                    {/* Action Plan */}
                    <div className="p-3 rounded-lg bg-blue-500/10 border border-blue-500/20">
                      <p className="text-xs text-blue-400 mb-2 font-semibold">📋 WHAT TO DO</p>
                      <ul className="text-sm text-white/80 space-y-1 list-disc list-inside">
                        <li>Analyze the root cause of this issue</li>
                        <li>Develop a solution plan with clear milestones</li>
                        <li>Implement and test the fix</li>
                        <li>Monitor success metrics to validate improvement</li>
                      </ul>
                    </div>

                    {/* Priority & Impact */}
                    <div className="grid sm:grid-cols-3 gap-3">
                      <div className="p-3 rounded-lg bg-white/5">
                        <p className="text-xs text-muted">Priority</p>
                        <p className="font-semibold capitalize">{rec.priority}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-white/5">
                        <p className="text-xs text-muted">Effort Required</p>
                        <p className="font-semibold capitalize">{rec.complexity}</p>
                      </div>
                      <div className="p-3 rounded-lg bg-white/5">
                        <p className="text-xs text-muted">Expected Impact</p>
                        <p className="font-semibold capitalize">{rec.expected_impact}</p>
                      </div>
                    </div>

                    {/* Success Metrics */}
                    {rec.success_metrics && rec.success_metrics.length > 0 && (
                      <div className="p-3 rounded-lg bg-spotify/10 border border-spotify/20">
                        <p className="text-xs text-spotify mb-2 font-semibold">📊 HOW TO MEASURE SUCCESS</p>
                        <div className="flex flex-wrap gap-2">
                          {rec.success_metrics.map((m, j) => (
                            <Badge key={j} label={m} variant="success" />
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Why This Matters */}
                    <div className="p-3 rounded-lg bg-white/5">
                      <p className="text-xs text-muted mb-1 font-semibold">💡 WHY THIS MATTERS</p>
                      <p className="text-sm text-white/80">
                        {rec.priority === 'high' ? 'This addresses a critical user pain point affecting many users. Immediate action required to prevent churn.' :
                         rec.priority === 'medium' ? 'This is an important improvement that will enhance user experience and satisfaction. Should be addressed in the next sprint.' :
                         'This is a nice-to-have feature that can improve the product. Implement when resources and priorities allow.'}
                      </p>
                    </div>
                  </div>
                )}
              </Card>
            ))
          )}
        </div>
      )}

      {view === 'roadmap' && (
        <div className="space-y-4">
          <Card className="bg-white/5">
            <p className="text-sm text-muted">
              <strong>📅 Product Roadmap:</strong> A timeline view of when recommendations should be implemented based on priority and dependencies.
            </p>
          </Card>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {['Q1', 'Q2', 'Q3', 'Q4'].map((q) => {
              const items = roadmap.filter((r) => r.quarter === q);
              return (
                <Card key={q} className={items.length > 0 ? 'border-spotify/20' : ''}>
                  <h4 className="font-bold text-spotify mb-3">{q}</h4>
                  {items.length === 0 ? (
                    <p className="text-xs text-muted">No items scheduled</p>
                  ) : (
                    <ul className="space-y-3">
                      {items.map((item) => (
                        <li key={item.id} className="p-3 rounded-lg bg-white/5 text-sm">
                          <p className="font-medium mb-2">{item.title}</p>
                          {item.description && (
                            <p className="text-xs text-muted mb-2">{item.description}</p>
                          )}
                          <div className="flex items-center gap-2 mb-2">
                            <Badge label={item.priority} variant={priorityVariant[item.priority] || 'default'} />
                            <span className="text-xs text-muted">{item.estimated_effort}</span>
                          </div>
                          {item.dependencies && item.dependencies.length > 0 && (
                            <div className="mt-2">
                              <p className="text-xs text-muted mb-1">Dependencies:</p>
                              <div className="flex flex-wrap gap-1">
                                {item.dependencies.map((dep, j) => (
                                  <Badge key={j} label={dep} variant="default" />
                                ))}
                              </div>
                            </div>
                          )}
                        </li>
                      ))}
                    </ul>
                  )}
                </Card>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}

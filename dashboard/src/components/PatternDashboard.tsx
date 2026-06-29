import { useState } from 'react';
import { Pattern } from '../api/client';
import Card from './ui/Card';
import Button from './ui/Button';
import Badge from './ui/Badge';

interface Props {
  data: Pattern[];
}

const PATTERN_EXPLANATIONS: Record<string, string> = {
  temporal: 'Time-based patterns showing how user behavior changes over days, weeks, or months',
  thematic: 'Topic-based patterns revealing common themes in user feedback',
  cross_platform: 'Patterns that appear across different platforms (App Store, Play Store, etc.)',
};

export default function PatternDashboard({ data }: Props) {
  const [filter, setFilter] = useState<string | null>(null);
  const [selected, setSelected] = useState<Pattern | null>(null);

  const filtered = filter ? data.filter((p) => p.pattern_type === filter) : data;
  const topPatterns = filtered.sort((a, b) => b.frequency - a.frequency).slice(0, 8);

  return (
    <div className="space-y-6 animate-fade-in">
      {/* Explanation Header */}
      <Card className="bg-gradient-to-r from-spotify/10 to-transparent border-spotify/20">
        <h3 className="text-lg font-semibold mb-2">🔍 What are Patterns?</h3>
        <p className="text-sm text-muted mb-3">
          Patterns are recurring behaviors or themes we discovered in user reviews. They help you understand what users consistently mention or do.
        </p>
        <div className="grid md:grid-cols-3 gap-3 text-xs">
          <div className="p-2 rounded bg-white/5">
            <strong className="text-spotify">Temporal:</strong> Time-based trends
          </div>
          <div className="p-2 rounded bg-white/5">
            <strong className="text-blue-400">Thematic:</strong> Common topics
          </div>
          <div className="p-2 rounded bg-white/5">
            <strong className="text-orange-400">Cross-Platform:</strong> Multi-platform patterns
          </div>
        </div>
      </Card>

      {/* Filter Buttons */}
      <div className="flex flex-wrap gap-2">
        <Button
          variant={filter === null ? 'primary' : 'ghost'}
          onClick={() => { setFilter(null); setSelected(null); }}
        >
          All Patterns ({uniquePatterns.length})
        </Button>
        <Button
          variant={filter === 'temporal' ? 'primary' : 'ghost'}
          onClick={() => { setFilter('temporal'); setSelected(null); }}
        >
          ⏰ Temporal ({uniquePatterns.filter((p) => p.pattern_type === 'temporal').length})
        </Button>
        <Button
          variant={filter === 'thematic' ? 'primary' : 'ghost'}
          onClick={() => { setFilter('thematic'); setSelected(null); }}
        >
          📝 Thematic ({uniquePatterns.filter((p) => p.pattern_type === 'thematic').length})
        </Button>
        <Button
          variant={filter === 'cross_platform' ? 'primary' : 'ghost'}
          onClick={() => { setFilter('cross_platform'); setSelected(null); }}
        >
          🌐 Cross-Platform ({uniquePatterns.filter((p) => p.pattern_type === 'cross_platform').length})
        </Button>
      </div>

      {/* Current Filter Explanation */}
      {filter && (
        <Card className="bg-white/5">
          <p className="text-sm text-muted">
            <strong>Showing:</strong> {PATTERN_EXPLANATIONS[filter] || filter}
          </p>
        </Card>
      )}

      {/* Pattern List */}
      <div className="grid gap-4">
        {topPatterns.length === 0 ? (
          <Card>
            <p className="text-muted text-center py-8">No patterns found for this filter</p>
          </Card>
        ) : (
          topPatterns.map((pattern, index) => (
            <Card
              key={pattern.id}
              className={`cursor-pointer transition-all hover:border-spotify/40 ${
                selected?.id === pattern.id ? 'border-spotify bg-spotify/5' : ''
              }`}
              onClick={() => setSelected(pattern)}
            >
              <div className="flex items-start gap-4">
                <div className="text-2xl font-bold text-muted/50 w-8">
                  #{index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2">
                    <Badge label={pattern.pattern_type} variant="info" />
                    <span className="text-xs text-muted">
                      Seen {pattern.frequency} times · {Math.round((pattern.confidence || 0) * 100)}% confidence
                    </span>
                  </div>
                  <p className="text-white font-medium mb-2">{pattern.pattern_description}</p>
                  {selected?.id === pattern.id && (
                    <div className="mt-4 pt-4 border-t border-white/10 space-y-2">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-xs text-muted">Frequency</p>
                          <p className="text-xl font-bold text-spotify">{pattern.frequency}</p>
                        </div>
                        <div>
                          <p className="text-xs text-muted">Confidence</p>
                          <p className="text-xl font-bold">{Math.round((pattern.confidence || 0) * 100)}%</p>
                        </div>
                      </div>
                      {pattern.time_period && (
                        <p className="text-xs text-muted">
                          <strong>Time Period:</strong> {pattern.time_period}
                        </p>
                      )}
                      <p className="text-xs text-muted">
                        <strong>What this means:</strong> Users consistently show this behavior, indicating it's a genuine pattern worth addressing.
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))
        )}
      </div>

      {filtered.length > 8 && (
        <p className="text-center text-sm text-muted">
          Showing top 8 of {filtered.length} patterns. Click on a pattern to see more details.
        </p>
      )}
    </div>
  );
}

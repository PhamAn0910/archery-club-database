import { useState } from 'react';
import { mockRounds } from '../data/mockData';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { BookOpen, Target } from 'lucide-react';

export function Home() {
  const [selectedRoundId, setSelectedRoundId] = useState<string | null>(null);

  const selectedRound = mockRounds.find(r => r.id === selectedRoundId);

  return (
    <div className="max-w-4xl mx-auto p-4 space-y-6">
      <div>
        <h1 className="mb-2">Round Definitions</h1>
        <p className="text-muted-foreground">Reference guide for all archery rounds</p>
      </div>

      {/* Round List */}
      {!selectedRound && (
        <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
          {mockRounds.map(round => (
            <Card
              key={round.id}
              className="p-4 hover:shadow-lg transition-shadow cursor-pointer"
              onClick={() => setSelectedRoundId(round.id)}
            >
              <div className="flex items-start gap-3">
                <div className="p-2 bg-primary/10 rounded-lg">
                  <Target className="w-6 h-6 text-primary" />
                </div>
                <div className="flex-1">
                  <h3 className="mb-1">{round.name}</h3>
                  <p className="text-muted-foreground">
                    {round.ranges.length} {round.ranges.length === 1 ? 'range' : 'ranges'}
                  </p>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Round Details */}
      {selectedRound && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="mb-1">{selectedRound.name}</h2>
              <p className="text-muted-foreground">
                Total of {selectedRound.ranges.reduce((sum, r) => sum + r.numberOfEnds, 0)} ends
              </p>
            </div>
            <Button variant="outline" onClick={() => setSelectedRoundId(null)}>
              Back to List
            </Button>
          </div>

          <div className="space-y-3">
            {selectedRound.ranges.map((range, index) => (
              <Card key={range.id} className="p-4">
                <div className="flex items-start gap-4">
                  <div className="flex items-center justify-center w-12 h-12 rounded-full bg-primary/10 text-primary">
                    {index + 1}
                  </div>
                  <div className="flex-1">
                    <h3 className="mb-2">Range {index + 1}</h3>
                    <div className="grid gap-2 sm:grid-cols-3">
                      <div>
                        <div className="text-muted-foreground">Distance</div>
                        <div>{range.distance}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Face Size</div>
                        <div>{range.faceSize}</div>
                      </div>
                      <div>
                        <div className="text-muted-foreground">Ends</div>
                        <div>
                          {range.numberOfEnds} ends × 6 arrows = {range.numberOfEnds * 6} arrows
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Summary Card */}
          <Card className="p-4 bg-muted/50">
            <div className="flex items-start gap-3">
              <BookOpen className="w-5 h-5 text-muted-foreground mt-1" />
              <div>
                <div className="mb-1">Total Arrows</div>
                <div className="text-muted-foreground">
                  {selectedRound.ranges.reduce((sum, r) => sum + (r.numberOfEnds * 6), 0)} arrows across{' '}
                  {selectedRound.ranges.length} {selectedRound.ranges.length === 1 ? 'range' : 'ranges'}
                </div>
              </div>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}

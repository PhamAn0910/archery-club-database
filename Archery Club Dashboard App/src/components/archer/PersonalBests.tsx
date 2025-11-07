import { useState } from 'react';
import { Division, PersonalBest } from '../../types/archery';
import { mockScores, mockRounds } from '../../data/mockData';
import { Card } from '../ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Trophy, TrendingUp } from 'lucide-react';

function calculatePersonalBests(archerId: string, division?: Division): PersonalBest[] {
  const archerScores = mockScores.filter(
    score => score.archerId === archerId && score.status === 'Confirmed' && (!division || score.division === division)
  );

  const pbsByRound: { [roundId: string]: PersonalBest } = {};

  archerScores.forEach(score => {
    if (!pbsByRound[score.roundId] || score.totalScore > pbsByRound[score.roundId].score) {
      pbsByRound[score.roundId] = {
        roundId: score.roundId,
        roundName: score.roundName,
        score: score.totalScore,
        date: score.date,
        division: score.division,
      };
    }
  });

  return Object.values(pbsByRound).sort((a, b) => a.roundName.localeCompare(b.roundName));
}

function calculateClubRecords(): PersonalBest[] {
  const confirmedScores = mockScores.filter(score => score.status === 'Confirmed');
  const recordsByRound: { [key: string]: PersonalBest & { archerName: string } } = {};

  confirmedScores.forEach(score => {
    const key = `${score.roundId}-${score.division}`;
    if (!recordsByRound[key] || score.totalScore > recordsByRound[key].score) {
      recordsByRound[key] = {
        roundId: score.roundId,
        roundName: score.roundName,
        score: score.totalScore,
        date: score.date,
        division: score.division,
        archerName: score.archerName,
      };
    }
  });

  return Object.values(recordsByRound).sort((a, b) => {
    const roundCompare = a.roundName.localeCompare(b.roundName);
    if (roundCompare !== 0) return roundCompare;
    return a.division.localeCompare(b.division);
  });
}

export function PersonalBests({ archerId }: { archerId: string }) {
  const [selectedDivision, setSelectedDivision] = useState<Division | 'all'>('all');

  const divisions: Division[] = ['Recurve', 'Compound', 'Barebow', 'Longbow'];
  
  const personalBests = calculatePersonalBests(
    archerId,
    selectedDivision === 'all' ? undefined : selectedDivision
  );
  
  const clubRecords = calculateClubRecords();

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <div>
        <h1 className="mb-2">Personal Bests & Club Records</h1>
        <p className="text-muted-foreground">Track your achievements and club records</p>
      </div>

      <Tabs defaultValue="pbs" className="w-full">
        <TabsList className="grid w-full max-w-md grid-cols-2">
          <TabsTrigger value="pbs">My Personal Bests</TabsTrigger>
          <TabsTrigger value="records">Club Records</TabsTrigger>
        </TabsList>

        <TabsContent value="pbs" className="space-y-4">
          {/* Division Filter */}
          <Card className="p-4">
            <label className="block mb-2">Filter by Division</label>
            <Select
              value={selectedDivision}
              onValueChange={(value) => setSelectedDivision(value as Division | 'all')}
            >
              <SelectTrigger className="max-w-xs">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Divisions</SelectItem>
                {divisions.map(div => (
                  <SelectItem key={div} value={div}>
                    {div}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </Card>

          {/* Personal Bests Grid */}
          {personalBests.length === 0 ? (
            <Card className="p-8 text-center text-muted-foreground">
              <TrendingUp className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>No personal bests yet. Start shooting to set your records!</p>
            </Card>
          ) : (
            <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
              {personalBests.map(pb => (
                <Card key={`${pb.roundId}-${pb.division}`} className="p-4 hover:shadow-lg transition-shadow">
                  <div className="flex items-start gap-3">
                    <div className="p-2 bg-primary/10 rounded-lg">
                      <Trophy className="w-6 h-6 text-primary" />
                    </div>
                    <div className="flex-1">
                      <h3 className="mb-1">{pb.roundName}</h3>
                      <div className="text-muted-foreground mb-3">{pb.division}</div>
                      <div className="text-3xl mb-1">{pb.score}</div>
                      <div className="text-muted-foreground">{formatDate(pb.date)}</div>
                    </div>
                  </div>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="records" className="space-y-4">
          {/* Club Records Grid */}
          <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
            {clubRecords.map(record => (
              <Card key={`${record.roundId}-${record.division}`} className="p-4">
                <div className="flex items-start gap-3">
                  <div className="p-2 bg-yellow-500/10 rounded-lg">
                    <Trophy className="w-6 h-6 text-yellow-600" />
                  </div>
                  <div className="flex-1">
                    <h3 className="mb-1">{record.roundName}</h3>
                    <div className="text-muted-foreground mb-3">{record.division}</div>
                    <div className="text-3xl mb-1">{record.score}</div>
                    <div className="text-muted-foreground">
                      {(record as any).archerName}
                    </div>
                    <div className="text-muted-foreground">{formatDate(record.date)}</div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
}

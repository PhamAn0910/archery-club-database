import { useState } from 'react';
import { mockCompetitions, mockScores } from '../../data/mockData';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Card } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Badge } from '../ui/badge';
import { Trophy, Medal } from 'lucide-react';

function calculateAgeClass(birthYear: number, competitionYear: number): string {
  const age = competitionYear - birthYear;
  if (age < 18) return 'Under 18';
  if (age >= 70) return '70+';
  if (age >= 60) return '60+';
  if (age >= 50) return '50+';
  return 'Open';
}

function getCategory(score: any, competitionYear: number): string {
  // In a real app, we'd get birth year from archer data
  const ageClass = 'Open'; // Simplified for mock data
  return `${score.division} ${ageClass} ${score.archerName.includes('Sarah') || score.archerName.includes('Emma') || score.archerName.includes('Lisa') ? 'Female' : 'Male'}`;
}

export function CompetitionResults() {
  const [selectedCompId, setSelectedCompId] = useState<string>('');

  const selectedCompetition = mockCompetitions.find(c => c.id === selectedCompId);

  // Get scores for selected competition
  const competitionScores = selectedCompetition
    ? mockScores.filter(
        score =>
          score.status === 'Confirmed' &&
          selectedCompetition.roundIds.includes(score.roundId) &&
          new Date(score.date) >= new Date(selectedCompetition.startDate) &&
          new Date(score.date) <= new Date(selectedCompetition.endDate)
      )
    : [];

  // Group by category and rank
  const categorizedResults: { [category: string]: any[] } = {};
  
  competitionScores.forEach(score => {
    const category = getCategory(score, 2025);
    if (!categorizedResults[category]) {
      categorizedResults[category] = [];
    }
    // Add AV Number from archer data (using memberId for now)
    const archer = mockScores.find(s => s.archerId === score.archerId);
    categorizedResults[category].push({
      ...score,
      avNumber: score.archerId.toUpperCase().replace('ARCHER', 'AV') // Mock AV number
    });
  });

  // Sort each category by score (highest first) and X count for tie-breaks
  Object.keys(categorizedResults).forEach(category => {
    categorizedResults[category].sort((a, b) => {
      if (b.totalScore !== a.totalScore) {
        return b.totalScore - a.totalScore;
      }
      return b.xCount - a.xCount;
    });
  });

  const getRankBadge = (rank: number) => {
    if (rank === 1) {
      return (
        <div className="flex items-center gap-2">
          <Trophy className="w-5 h-5 text-yellow-600" />
          <span>1st</span>
        </div>
      );
    }
    if (rank === 2) {
      return (
        <div className="flex items-center gap-2">
          <Medal className="w-5 h-5 text-gray-400" />
          <span>2nd</span>
        </div>
      );
    }
    if (rank === 3) {
      return (
        <div className="flex items-center gap-2">
          <Medal className="w-5 h-5 text-orange-600" />
          <span>3rd</span>
        </div>
      );
    }
    return `${rank}th`;
  };

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <div>
        <h1 className="mb-2">Competition Results</h1>
        <p className="text-muted-foreground">View official competition results</p>
      </div>

      {/* Competition Selector */}
      <Card className="p-4">
        <label className="block mb-2">Select Competition</label>
        <Select value={selectedCompId} onValueChange={setSelectedCompId}>
          <SelectTrigger>
            <SelectValue placeholder="Choose a competition..." />
          </SelectTrigger>
          <SelectContent>
            {mockCompetitions.map(comp => (
              <SelectItem key={comp.id} value={comp.id}>
                {comp.name}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </Card>

      {/* Results */}
      {selectedCompetition && (
        <div className="space-y-6">
          {Object.keys(categorizedResults).length === 0 ? (
            <Card className="p-8 text-center text-muted-foreground">
              No results available for this competition
            </Card>
          ) : (
            Object.entries(categorizedResults).map(([category, scores]) => (
              <Card key={category} className="p-6">
                <h2 className="mb-4">{category}</h2>
                
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead className="w-24">Rank</TableHead>
                      <TableHead>AV Number</TableHead>
                      <TableHead>Round</TableHead>
                      <TableHead className="text-right">Score</TableHead>
                      <TableHead className="text-right">X Count</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {scores.map((score, index) => (
                      <TableRow key={score.id}>
                        <TableCell>{getRankBadge(index + 1)}</TableCell>
                        <TableCell>{score.avNumber}</TableCell>
                        <TableCell>{score.roundName}</TableCell>
                        <TableCell className="text-right">{score.totalScore}</TableCell>
                        <TableCell className="text-right">{score.xCount}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </Card>
            ))
          )}
        </div>
      )}
    </div>
  );
}
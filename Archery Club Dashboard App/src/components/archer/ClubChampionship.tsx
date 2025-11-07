import { mockScores, mockChampionshipSettings, mockArchers } from '../../data/mockData';
import { Card } from '../ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Trophy, Medal, Award } from 'lucide-react';

function calculateChampionshipStandings() {
  const { year, roundIds, scoringRule } = mockChampionshipSettings;
  
  // Get number of scores to count based on rule
  const numberOfScores = scoringRule === 'Best score' ? 1 : 2;

  // Get relevant scores
  const relevantScores = mockScores.filter(
    score => 
      score.status === 'Confirmed' &&
      roundIds.includes(score.roundId) &&
      new Date(score.date).getFullYear() === year
  );

  // Group by archer and category
  const archerScores: { [key: string]: any } = {};

  relevantScores.forEach(score => {
    const category = `${score.division} Open`; // Simplified
    const key = `${score.archerId}-${category}`;
    
    if (!archerScores[key]) {
      // Get AV Number from archer data
      const avNumber = score.archerId.toUpperCase().replace('ARCHER', 'AV');
      archerScores[key] = {
        archerId: score.archerId,
        avNumber,
        category,
        division: score.division,
        scores: [],
      };
    }
    
    archerScores[key].scores.push(score.totalScore);
  });

  // Calculate championship scores
  const standings = Object.values(archerScores).map(archer => {
    // Sort scores highest to lowest and take top N
    const topScores = [...archer.scores]
      .sort((a, b) => b - a)
      .slice(0, numberOfScores);
    
    const championshipScore = topScores.reduce((sum, score) => sum + score, 0);
    
    return {
      ...archer,
      championshipScore,
      countedScores: topScores,
    };
  });

  // Group by category
  const categorizedStandings: { [category: string]: any[] } = {};
  
  standings.forEach(standing => {
    if (!categorizedStandings[standing.category]) {
      categorizedStandings[standing.category] = [];
    }
    categorizedStandings[standing.category].push(standing);
  });

  // Sort each category
  Object.keys(categorizedStandings).forEach(category => {
    categorizedStandings[category].sort((a, b) => b.championshipScore - a.championshipScore);
  });

  return categorizedStandings;
}

export function ClubChampionship() {
  const standings = calculateChampionshipStandings();
  const { year, scoringRule } = mockChampionshipSettings;

  const getRankIcon = (rank: number) => {
    if (rank === 1) return <Trophy className="w-6 h-6 text-yellow-600" />;
    if (rank === 2) return <Medal className="w-6 h-6 text-gray-400" />;
    if (rank === 3) return <Medal className="w-6 h-6 text-orange-600" />;
    return <Award className="w-6 h-6 text-muted-foreground" />;
  };

  return (
    <div className="max-w-6xl mx-auto p-4 space-y-6">
      <div>
        <h1 className="mb-2">Club Championship {year}</h1>
        <p className="text-muted-foreground">
          Ranking based on {scoringRule.toLowerCase()}
        </p>
      </div>

      {/* Championship Info */}
      <Card className="p-4 bg-muted/50">
        <div className="flex items-center gap-2 text-muted-foreground">
          <Award className="w-5 h-5" />
          <span>
            Championship scoring: Sum of {scoringRule.toLowerCase()} across eligible rounds
          </span>
        </div>
      </Card>

      {/* Standings by Category */}
      <div className="space-y-6">
        {Object.entries(standings).map(([category, categoryStandings]) => (
          <Card key={category} className="p-6">
            <h2 className="mb-4">{category}</h2>
            
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-16"></TableHead>
                  <TableHead className="w-16">Rank</TableHead>
                  <TableHead>AV Number</TableHead>
                  <TableHead className="text-right">Championship Score</TableHead>
                  <TableHead className="text-right">Counted Scores</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {categoryStandings.map((standing, index) => (
                  <TableRow key={standing.archerId} className={index < 3 ? 'bg-muted/30' : ''}>
                    <TableCell>{getRankIcon(index + 1)}</TableCell>
                    <TableCell>
                      <div>
                        {index + 1}
                        {index === 0 && 'st'}
                        {index === 1 && 'nd'}
                        {index === 2 && 'rd'}
                        {index > 2 && 'th'}
                      </div>
                    </TableCell>
                    <TableCell>{standing.avNumber}</TableCell>
                    <TableCell className="text-right text-lg">
                      {standing.championshipScore}
                    </TableCell>
                    <TableCell className="text-right text-muted-foreground">
                      {standing.countedScores.join(', ')}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        ))}
      </div>
    </div>
  );
}
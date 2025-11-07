import { useState } from 'react';
import { Score } from '../../types/archery';
import { mockScores, mockRounds } from '../../data/mockData';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Card } from '../ui/card';
import { Badge } from '../ui/badge';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { ArrowDown, ArrowUp } from 'lucide-react';

type SortField = 'date' | 'score';
type SortOrder = 'asc' | 'desc';

export function ScoreHistory({ archerId }: { archerId: string }) {
  const [selectedRoundFilter, setSelectedRoundFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('date');
  const [sortOrder, setSortOrder] = useState<SortOrder>('desc');
  const [selectedScore, setSelectedScore] = useState<Score | null>(null);

  // Filter scores for this archer
  const archerScores = mockScores.filter(score => score.archerId === archerId);

  // Apply round filter
  const filteredScores = selectedRoundFilter === 'all'
    ? archerScores
    : archerScores.filter(score => score.roundId === selectedRoundFilter);

  // Apply sorting
  const sortedScores = [...filteredScores].sort((a, b) => {
    if (sortField === 'date') {
      const comparison = new Date(a.date).getTime() - new Date(b.date).getTime();
      return sortOrder === 'asc' ? comparison : -comparison;
    } else {
      const comparison = a.totalScore - b.totalScore;
      return sortOrder === 'asc' ? comparison : -comparison;
    }
  });

  const toggleSort = (field: SortField) => {
    if (sortField === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortOrder(field === 'date' ? 'desc' : 'desc');
    }
  };

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
        <h1 className="mb-2">My Score History</h1>
        <p className="text-muted-foreground">View all your recorded scores</p>
      </div>

      {/* Filters */}
      <Card className="p-4">
        <div className="flex flex-col sm:flex-row gap-4">
          <div className="flex-1">
            <label className="block mb-2">Filter by Round</label>
            <Select value={selectedRoundFilter} onValueChange={setSelectedRoundFilter}>
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Rounds</SelectItem>
                {mockRounds.map(round => (
                  <SelectItem key={round.id} value={round.id}>
                    {round.name}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </Card>

      {/* Scores Table */}
      <Card>
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>
                <Button
                  variant="ghost"
                  onClick={() => toggleSort('date')}
                  className="flex items-center gap-1 p-0"
                >
                  Date
                  {sortField === 'date' && (
                    sortOrder === 'asc' ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />
                  )}
                </Button>
              </TableHead>
              <TableHead>Round Name</TableHead>
              <TableHead>
                <Button
                  variant="ghost"
                  onClick={() => toggleSort('score')}
                  className="flex items-center gap-1 p-0"
                >
                  Total Score
                  {sortField === 'score' && (
                    sortOrder === 'asc' ? <ArrowUp className="w-4 h-4" /> : <ArrowDown className="w-4 h-4" />
                  )}
                </Button>
              </TableHead>
              <TableHead>X Count</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Actions</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {sortedScores.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center text-muted-foreground">
                  No scores found
                </TableCell>
              </TableRow>
            ) : (
              sortedScores.map(score => (
                <TableRow key={score.id}>
                  <TableCell>{formatDate(score.date)}</TableCell>
                  <TableCell>{score.roundName}</TableCell>
                  <TableCell>{score.totalScore}</TableCell>
                  <TableCell>{score.xCount}</TableCell>
                  <TableCell>
                    <Badge variant={score.status === 'Confirmed' ? 'default' : 'secondary'}>
                      {score.status}
                    </Badge>
                  </TableCell>
                  <TableCell>
                    <Button variant="outline" size="sm" onClick={() => setSelectedScore(score)}>
                      View Details
                    </Button>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </Card>

      {/* Score Details Dialog */}
      <Dialog open={!!selectedScore} onOpenChange={() => setSelectedScore(null)}>
        <DialogContent className="max-w-4xl max-h-[80vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              {selectedScore?.roundName} - {selectedScore && formatDate(selectedScore.date)}
            </DialogTitle>
            <DialogDescription>
              View detailed breakdown of your score by range and end
            </DialogDescription>
          </DialogHeader>
          
          {selectedScore && (
            <div className="space-y-6">
              {/* Summary */}
              <div className="grid grid-cols-3 gap-4 text-center">
                <Card className="p-4">
                  <div className="text-muted-foreground mb-1">Total Score</div>
                  <div className="text-3xl">{selectedScore.totalScore}</div>
                </Card>
                <Card className="p-4">
                  <div className="text-muted-foreground mb-1">X Count</div>
                  <div className="text-3xl">{selectedScore.xCount}</div>
                </Card>
                <Card className="p-4">
                  <div className="text-muted-foreground mb-1">Status</div>
                  <Badge variant={selectedScore.status === 'Confirmed' ? 'default' : 'secondary'} className="mt-2">
                    {selectedScore.status}
                  </Badge>
                </Card>
              </div>

              {/* Range Breakdown */}
              {selectedScore.rangeScores.map((rangeScore, rangeIndex) => (
                <Card key={rangeIndex} className="p-4">
                  <div className="mb-4">
                    <h3 className="mb-1">
                      {rangeScore.distance} ({rangeScore.faceSize} face)
                    </h3>
                    <div className="flex gap-4 text-muted-foreground">
                      <span>Range Total: {rangeScore.total}</span>
                      <span>X's: {rangeScore.xCount}</span>
                    </div>
                  </div>

                  <div className="space-y-2">
                    {rangeScore.ends.map((end, endIndex) => (
                      <div key={endIndex} className="flex items-center gap-3 p-2 border rounded">
                        <div className="w-16 text-muted-foreground">
                          End {end.endNumber}
                        </div>
                        <div className="flex gap-2 flex-1">
                          {end.arrows.map((arrow, arrowIndex) => (
                            <div
                              key={arrowIndex}
                              className="flex-1 text-center p-2 bg-muted rounded"
                            >
                              {arrow}
                            </div>
                          ))}
                        </div>
                        <div className="w-16 text-right">
                          {end.total}
                        </div>
                      </div>
                    ))}
                  </div>
                </Card>
              ))}
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
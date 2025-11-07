import { useState } from 'react';
import { mockScores } from '../../data/mockData';
import { Score, ArrowValue } from '../../types/archery';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from '../ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Check, X, Edit, AlertCircle } from 'lucide-react';

const arrowValues: ArrowValue[] = ['X', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', 'M'];

export function ScoreApproval() {
  const [scores, setScores] = useState(mockScores);
  const [editingScore, setEditingScore] = useState<Score | null>(null);
  const [editedArrows, setEditedArrows] = useState<any>({});

  const preliminaryScores = scores.filter(s => s.status === 'Preliminary');

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-AU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const handleConfirm = (scoreId: string) => {
    setScores(prev =>
      prev.map(s => (s.id === scoreId ? { ...s, status: 'Confirmed' as const } : s))
    );
  };

  const handleReject = (scoreId: string) => {
    if (confirm('Are you sure you want to reject this score?')) {
      setScores(prev =>
        prev.map(s => (s.id === scoreId ? { ...s, status: 'Rejected' as const } : s))
      );
    }
  };

  const handleEdit = (score: Score) => {
    setEditingScore(score);
    // Initialize edited arrows with current values
    const initialArrows: any = {};
    score.rangeScores.forEach((rangeScore, rangeIdx) => {
      rangeScore.ends.forEach((end, endIdx) => {
        const key = `${rangeIdx}-${endIdx}`;
        initialArrows[key] = [...end.arrows];
      });
    });
    setEditedArrows(initialArrows);
  };

  const handleArrowChange = (rangeIdx: number, endIdx: number, arrowIdx: number, value: ArrowValue) => {
    const key = `${rangeIdx}-${endIdx}`;
    setEditedArrows((prev: any) => {
      const newArrows = { ...prev };
      if (!newArrows[key]) {
        newArrows[key] = [...(editingScore?.rangeScores[rangeIdx].ends[endIdx].arrows || [])];
      }
      newArrows[key][arrowIdx] = value;
      return newArrows;
    });
  };

  const handleSaveEdit = () => {
    if (!editingScore) return;

    // In a real app, this would save to backend
    alert('Score updated successfully');
    setEditingScore(null);
    setEditedArrows({});
  };

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-6">
      <div>
        <h1 className="mb-2">Score Approval</h1>
        <p className="text-muted-foreground">Review and approve preliminary scores</p>
      </div>

      {preliminaryScores.length === 0 ? (
        <Card className="p-8 text-center text-muted-foreground">
          <AlertCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <p>No preliminary scores waiting for approval</p>
        </Card>
      ) : (
        <Card>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Date</TableHead>
                  <TableHead>Archer</TableHead>
                  <TableHead>Round</TableHead>
                  <TableHead>Division</TableHead>
                  <TableHead className="text-right">Total Score</TableHead>
                  <TableHead className="text-right">X Count</TableHead>
                  <TableHead className="text-right">Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {preliminaryScores.map(score => (
                  <TableRow key={score.id}>
                    <TableCell>{formatDate(score.date)}</TableCell>
                    <TableCell>{score.archerName}</TableCell>
                    <TableCell>{score.roundName}</TableCell>
                    <TableCell>{score.division}</TableCell>
                    <TableCell className="text-right">{score.totalScore}</TableCell>
                    <TableCell className="text-right">{score.xCount}</TableCell>
                    <TableCell>
                      <div className="flex justify-end gap-2">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleEdit(score)}
                        >
                          <Edit className="w-4 h-4 mr-1" />
                          Edit
                        </Button>
                        <Button
                          size="sm"
                          variant="default"
                          onClick={() => handleConfirm(score.id)}
                        >
                          <Check className="w-4 h-4 mr-1" />
                          Confirm
                        </Button>
                        <Button
                          size="sm"
                          variant="destructive"
                          onClick={() => handleReject(score.id)}
                        >
                          <X className="w-4 h-4 mr-1" />
                          Reject
                        </Button>
                      </div>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>
      )}

      {/* Edit Score Dialog */}
      <Dialog open={!!editingScore} onOpenChange={() => setEditingScore(null)}>
        <DialogContent className="max-w-5xl max-h-[90vh] overflow-y-auto">
          <DialogHeader>
            <DialogTitle>
              Edit Score: {editingScore?.archerName} - {editingScore?.roundName}
            </DialogTitle>
            <DialogDescription>
              Edit arrow values for each end. Changes will be saved to the score record.
            </DialogDescription>
          </DialogHeader>

          {editingScore && (
            <div className="space-y-6">
              {editingScore.rangeScores.map((rangeScore, rangeIdx) => (
                <Card key={rangeIdx} className="p-4">
                  <h3 className="mb-4">
                    {rangeScore.distance} ({rangeScore.faceSize} face)
                  </h3>

                  <div className="space-y-3">
                    {rangeScore.ends.map((end, endIdx) => {
                      const key = `${rangeIdx}-${endIdx}`;
                      const currentArrows = editedArrows[key] || end.arrows;

                      return (
                        <div key={endIdx} className="border rounded p-3">
                          <div className="mb-2">End {end.endNumber}</div>
                          <div className="grid grid-cols-6 gap-2">
                            {currentArrows.map((arrow: ArrowValue, arrowIdx: number) => (
                              <div key={arrowIdx}>
                                <Select
                                  value={arrow}
                                  onValueChange={(value) =>
                                    handleArrowChange(rangeIdx, endIdx, arrowIdx, value as ArrowValue)
                                  }
                                >
                                  <SelectTrigger>
                                    <SelectValue />
                                  </SelectTrigger>
                                  <SelectContent>
                                    {arrowValues.map(val => (
                                      <SelectItem key={val} value={val}>
                                        {val}
                                      </SelectItem>
                                    ))}
                                  </SelectContent>
                                </Select>
                              </div>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </Card>
              ))}

              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => setEditingScore(null)}>
                  Cancel
                </Button>
                <Button onClick={handleSaveEdit}>Save Changes</Button>
              </div>
            </div>
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
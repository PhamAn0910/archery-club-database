import { useState } from 'react';
import { ArrowValue, Round } from '../../types/archery';
import { mockRounds } from '../../data/mockData';
import { Button } from '../ui/button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Card } from '../ui/card';
import { Check } from 'lucide-react';

const arrowValues: ArrowValue[] = ['X', '10', '9', '8', '7', '6', '5', '4', '3', '2', '1', 'M'];

const getArrowPoints = (arrow: ArrowValue | null): number => {
  if (!arrow) return 0;
  if (arrow === 'X' || arrow === '10') return 10;
  if (arrow === 'M') return 0;
  return parseInt(arrow);
};

export function LiveScoreEntry({ archerName }: { archerName: string }) {
  const [selectedRound, setSelectedRound] = useState<Round | null>(null);
  const [currentRangeIndex, setCurrentRangeIndex] = useState(0);
  const [currentEndNumber, setCurrentEndNumber] = useState(1);
  const [currentArrows, setCurrentArrows] = useState<(ArrowValue | null)[]>([null, null, null, null, null, null]);
  const [runningTotal, setRunningTotal] = useState(0);
  const [roundComplete, setRoundComplete] = useState(false);

  const handleRoundSelect = (roundId: string) => {
    const round = mockRounds.find(r => r.id === roundId);
    if (round) {
      setSelectedRound(round);
      setCurrentRangeIndex(0);
      setCurrentEndNumber(1);
      setCurrentArrows([null, null, null, null, null, null]);
      setRunningTotal(0);
      setRoundComplete(false);
    }
  };

  const handleArrowInput = (index: number, value: ArrowValue) => {
    const newArrows = [...currentArrows];
    newArrows[index] = value;
    setCurrentArrows(newArrows);
  };

  const calculateEndTotal = () => {
    return currentArrows.reduce((sum, arrow) => sum + getArrowPoints(arrow), 0);
  };

  const handleSubmitEnd = () => {
    const endTotal = calculateEndTotal();
    const newRunningTotal = runningTotal + endTotal;
    setRunningTotal(newRunningTotal);

    if (!selectedRound) return;

    const currentRange = selectedRound.ranges[currentRangeIndex];
    
    // Check if this is the last end of the current range
    if (currentEndNumber >= currentRange.numberOfEnds) {
      // Check if this is the last range
      if (currentRangeIndex >= selectedRound.ranges.length - 1) {
        setRoundComplete(true);
      } else {
        // Move to next range
        setCurrentRangeIndex(currentRangeIndex + 1);
        setCurrentEndNumber(1);
        setCurrentArrows([null, null, null, null, null, null]);
      }
    } else {
      // Move to next end
      setCurrentEndNumber(currentEndNumber + 1);
      setCurrentArrows([null, null, null, null, null, null]);
    }
  };

  const handleSubmitFinalScore = () => {
    alert(`Score submitted! Total: ${runningTotal}`);
    // Reset for new round
    setSelectedRound(null);
    setCurrentRangeIndex(0);
    setCurrentEndNumber(1);
    setCurrentArrows([null, null, null, null, null, null]);
    setRunningTotal(0);
    setRoundComplete(false);
  };

  const endTotal = calculateEndTotal();
  const currentRange = selectedRound?.ranges[currentRangeIndex];
  const isEndComplete = currentArrows.every(arrow => arrow !== null);

  return (
    <div className="max-w-2xl mx-auto p-4 space-y-6">
      {/* Header */}
      <div className="text-center">
        <h1 className="mb-2">{archerName}</h1>
        <p className="text-muted-foreground">Live Score Entry</p>
      </div>

      {/* Round Selection */}
      {!selectedRound && (
        <Card className="p-6">
          <label className="block mb-3">Select Round</label>
          <Select onValueChange={handleRoundSelect}>
            <SelectTrigger>
              <SelectValue placeholder="Choose a round..." />
            </SelectTrigger>
            <SelectContent>
              {mockRounds.map(round => (
                <SelectItem key={round.id} value={round.id}>
                  {round.name}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </Card>
      )}

      {/* Score Entry Interface */}
      {selectedRound && !roundComplete && currentRange && (
        <div className="space-y-6">
          {/* Current Range Info */}
          <Card className="p-4 bg-muted/50">
            <div className="text-center">
              <div className="mb-1">Now Shooting</div>
              <div>
                {currentRange.numberOfEnds} ends at {currentRange.distance}, {currentRange.faceSize} face
              </div>
            </div>
          </Card>

          {/* End Number */}
          <div className="text-center">
            <div className="text-muted-foreground">End {currentEndNumber} of {currentRange.numberOfEnds}</div>
          </div>

          {/* Arrow Input Grid */}
          <div className="grid grid-cols-2 gap-4 md:grid-cols-3">
            {currentArrows.map((arrow, index) => (
              <div key={index} className="space-y-2">
                <div className="text-center">
                  Arrow {index + 1}
                </div>
                <div className="relative aspect-square">
                  <Select
                    value={arrow || ''}
                    onValueChange={(value) => handleArrowInput(index, value as ArrowValue)}
                  >
                    <SelectTrigger className="h-full text-lg">
                      <SelectValue placeholder="-" />
                    </SelectTrigger>
                    <SelectContent>
                      {arrowValues.map(val => (
                        <SelectItem key={val} value={val} className="text-lg">
                          {val}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                  {arrow && (
                    <div className="absolute -top-1 -right-1 bg-primary text-primary-foreground rounded-full w-6 h-6 flex items-center justify-center">
                      <Check className="w-4 h-4" />
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* End Total & Running Total */}
          <Card className="p-6">
            <div className="grid grid-cols-2 gap-6 text-center">
              <div>
                <div className="text-muted-foreground mb-1">End Total</div>
                <div className="text-3xl">{endTotal}</div>
              </div>
              <div>
                <div className="text-muted-foreground mb-1">Running Total</div>
                <div className="text-3xl">{runningTotal}</div>
              </div>
            </div>
          </Card>

          {/* Submit Button */}
          <Button
            onClick={handleSubmitEnd}
            disabled={!isEndComplete}
            className="w-full h-14 text-lg"
          >
            Submit End
          </Button>
        </div>
      )}

      {/* Round Complete */}
      {roundComplete && (
        <Card className="p-8 text-center space-y-6">
          <div>
            <h2 className="mb-2">Round Complete!</h2>
            <p className="text-muted-foreground">Total Score</p>
            <div className="text-5xl mt-4">{runningTotal}</div>
          </div>
          <Button onClick={handleSubmitFinalScore} className="w-full h-14 text-lg">
            Submit Final Score
          </Button>
        </Card>
      )}
    </div>
  );
}

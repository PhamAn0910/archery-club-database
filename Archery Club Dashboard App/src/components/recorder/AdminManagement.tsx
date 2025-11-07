import { useState } from 'react';
import { mockArchers, mockRounds, mockCompetitions, mockChampionshipSettings } from '../../data/mockData';
import { Archer, Round, Competition, Division, Gender, FaceSize } from '../../types/archery';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../ui/tabs';
import { Card } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '../ui/table';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger, DialogDescription } from '../ui/dialog';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Plus, Edit } from 'lucide-react';

export function RecorderManagement() {
  const [archers, setArchers] = useState(mockArchers);
  const [rounds, setRounds] = useState(mockRounds);
  const [competitions, setCompetitions] = useState(mockCompetitions);
  const [championshipSettings, setChampionshipSettings] = useState(mockChampionshipSettings);

  // Member Management
  const [showAddMemberDialog, setShowAddMemberDialog] = useState(false);
  const [newMember, setNewMember] = useState({
    memberId: '',
    fullName: '',
    birthYear: new Date().getFullYear() - 30,
    gender: 'Male' as Gender,
    defaultDivision: 'Recurve' as Division,
  });

  const handleAddMember = () => {
    const archer: Archer = {
      id: `archer${archers.length + 1}`,
      ...newMember,
    };
    setArchers([...archers, archer]);
    setShowAddMemberDialog(false);
    setNewMember({
      memberId: '',
      fullName: '',
      birthYear: new Date().getFullYear() - 30,
      gender: 'Male',
      defaultDivision: 'Recurve',
    });
  };

  // Round Management
  const [showAddRoundDialog, setShowAddRoundDialog] = useState(false);
  const [newRound, setNewRound] = useState({
    name: '',
    ranges: [] as any[],
  });
  const [newRange, setNewRange] = useState({
    distance: '',
    faceSize: '122cm' as FaceSize,
    numberOfEnds: 5,
  });

  const handleAddRange = () => {
    setNewRound({
      ...newRound,
      ranges: [
        ...newRound.ranges,
        {
          id: `range-${Date.now()}`,
          ...newRange,
        },
      ],
    });
    setNewRange({
      distance: '',
      faceSize: '122cm',
      numberOfEnds: 5,
    });
  };

  const handleRemoveRange = (index: number) => {
    setNewRound({
      ...newRound,
      ranges: newRound.ranges.filter((_, i) => i !== index),
    });
  };

  const handleAddRound = () => {
    if (newRound.name && newRound.ranges.length > 0) {
      const round: Round = {
        id: newRound.name.toLowerCase().replace(/\s+/g, '-'),
        ...newRound,
      };
      setRounds([...rounds, round]);
      setShowAddRoundDialog(false);
      setNewRound({ name: '', ranges: [] });
    }
  };

  // Competition Management
  const [showAddCompDialog, setShowAddCompDialog] = useState(false);
  const [newCompetition, setNewCompetition] = useState({
    name: '',
    startDate: '',
    endDate: '',
    roundIds: [] as string[],
  });

  const handleAddCompetition = () => {
    const competition: Competition = {
      id: `comp${competitions.length + 1}`,
      ...newCompetition,
    };
    setCompetitions([...competitions, competition]);
    setShowAddCompDialog(false);
    setNewCompetition({
      name: '',
      startDate: '',
      endDate: '',
      roundIds: [],
    });
  };

  return (
    <div className="max-w-7xl mx-auto p-4 space-y-6">
      <div>
        <h1 className="mb-2">Recorder Management</h1>
        <p className="text-muted-foreground">Manage club members, rounds, and competitions</p>
      </div>

      <Tabs defaultValue="members" className="w-full">
        <TabsList className="grid w-full max-w-2xl grid-cols-4">
          <TabsTrigger value="members">Members</TabsTrigger>
          <TabsTrigger value="rounds">Rounds</TabsTrigger>
          <TabsTrigger value="competitions">Competitions</TabsTrigger>
          <TabsTrigger value="championship">Championship</TabsTrigger>
        </TabsList>

        {/* Member Management Tab */}
        <TabsContent value="members" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2>Club Members</h2>
            <Dialog open={showAddMemberDialog} onOpenChange={setShowAddMemberDialog}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Add New Archer
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add New Archer</DialogTitle>
                  <DialogDescription>
                    Enter the archer's details to add them to the club database.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="memberId">Member ID (e.g., Archery Victoria Number)</Label>
                    <Input
                      id="memberId"
                      value={newMember.memberId}
                      onChange={e => setNewMember({ ...newMember, memberId: e.target.value })}
                      placeholder="AV12345"
                    />
                  </div>
                  <div>
                    <Label htmlFor="fullName">Full Name</Label>
                    <Input
                      id="fullName"
                      value={newMember.fullName}
                      onChange={e => setNewMember({ ...newMember, fullName: e.target.value })}
                      placeholder="John Smith"
                    />
                  </div>
                  <div>
                    <Label htmlFor="birthYear">Birth Year</Label>
                    <Input
                      id="birthYear"
                      type="number"
                      value={newMember.birthYear}
                      onChange={e => setNewMember({ ...newMember, birthYear: parseInt(e.target.value) })}
                    />
                  </div>
                  <div>
                    <Label htmlFor="gender">Gender</Label>
                    <Select
                      value={newMember.gender}
                      onValueChange={(value: Gender) => setNewMember({ ...newMember, gender: value })}
                    >
                      <SelectTrigger id="gender">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Male">Male</SelectItem>
                        <SelectItem value="Female">Female</SelectItem>
                        <SelectItem value="Other">Other</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="division">Default Division (Bow Type)</Label>
                    <Select
                      value={newMember.defaultDivision}
                      onValueChange={(value: Division) => setNewMember({ ...newMember, defaultDivision: value })}
                    >
                      <SelectTrigger id="division">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Recurve">Recurve</SelectItem>
                        <SelectItem value="Compound">Compound</SelectItem>
                        <SelectItem value="Barebow">Barebow</SelectItem>
                        <SelectItem value="Longbow">Longbow</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <Button onClick={handleAddMember} className="w-full">
                    Add Archer
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Member ID</TableHead>
                  <TableHead>Name</TableHead>
                  <TableHead>Birth Year</TableHead>
                  <TableHead>Gender</TableHead>
                  <TableHead>Default Division</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {archers.map(archer => (
                  <TableRow key={archer.id}>
                    <TableCell>{archer.memberId}</TableCell>
                    <TableCell>{archer.fullName}</TableCell>
                    <TableCell>{archer.birthYear}</TableCell>
                    <TableCell>{archer.gender}</TableCell>
                    <TableCell>{archer.defaultDivision}</TableCell>
                    <TableCell>
                      <Button size="sm" variant="outline">
                        <Edit className="w-4 h-4 mr-1" />
                        Edit
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        {/* Round Management Tab */}
        <TabsContent value="rounds" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2>Rounds</h2>
            <Dialog open={showAddRoundDialog} onOpenChange={setShowAddRoundDialog}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Add New Round
                </Button>
              </DialogTrigger>
              <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
                <DialogHeader>
                  <DialogTitle>Add New Round</DialogTitle>
                  <DialogDescription>
                    Define a new round by adding ranges with distance, face size, and number of ends.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="roundName">Round Name</Label>
                    <Input
                      id="roundName"
                      value={newRound.name}
                      onChange={e => setNewRound({ ...newRound, name: e.target.value })}
                      placeholder="e.g., Adelaide"
                    />
                  </div>

                  <div className="border-t pt-4">
                    <h3 className="mb-3">Add Ranges</h3>
                    <div className="grid grid-cols-3 gap-3 mb-3">
                      <div>
                        <Label>Distance</Label>
                        <Input
                          value={newRange.distance}
                          onChange={e => setNewRange({ ...newRange, distance: e.target.value })}
                          placeholder="e.g., 70m"
                        />
                      </div>
                      <div>
                        <Label>Face Size</Label>
                        <Select
                          value={newRange.faceSize}
                          onValueChange={(value: FaceSize) => setNewRange({ ...newRange, faceSize: value })}
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="122cm">122cm</SelectItem>
                            <SelectItem value="80cm">80cm</SelectItem>
                            <SelectItem value="60cm">60cm</SelectItem>
                            <SelectItem value="40cm">40cm</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Number of Ends</Label>
                        <Input
                          type="number"
                          value={newRange.numberOfEnds}
                          onChange={e => setNewRange({ ...newRange, numberOfEnds: parseInt(e.target.value) })}
                        />
                      </div>
                    </div>
                    <Button onClick={handleAddRange} variant="outline" size="sm" className="w-full">
                      <Plus className="w-4 h-4 mr-2" />
                      Add Range
                    </Button>
                  </div>

                  {newRound.ranges.length > 0 && (
                    <div className="border-t pt-4">
                      <h3 className="mb-3">Ranges in this Round</h3>
                      <div className="space-y-2">
                        {newRound.ranges.map((range, idx) => (
                          <div key={idx} className="flex items-center justify-between p-2 bg-muted rounded">
                            <span>
                              {range.distance} - {range.faceSize} face - {range.numberOfEnds} ends
                            </span>
                            <Button
                              size="sm"
                              variant="ghost"
                              onClick={() => handleRemoveRange(idx)}
                            >
                              Remove
                            </Button>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}

                  <Button onClick={handleAddRound} className="w-full" disabled={!newRound.name || newRound.ranges.length === 0}>
                    Create Round
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            {rounds.map(round => (
              <Card key={round.id} className="p-4">
                <div className="flex items-start justify-between mb-3">
                  <h3>{round.name}</h3>
                  <Button size="sm" variant="outline">
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                </div>
                <div className="space-y-2 text-muted-foreground">
                  {round.ranges.map((range, idx) => (
                    <div key={range.id}>
                      Range {idx + 1}: {range.numberOfEnds} ends at {range.distance}, {range.faceSize} face
                    </div>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Competition Management Tab */}
        <TabsContent value="competitions" className="space-y-4">
          <div className="flex justify-between items-center">
            <h2>Competitions</h2>
            <Dialog open={showAddCompDialog} onOpenChange={setShowAddCompDialog}>
              <DialogTrigger asChild>
                <Button>
                  <Plus className="w-4 h-4 mr-2" />
                  Add New Competition
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Add New Competition</DialogTitle>
                  <DialogDescription>
                    Create a new competition by setting dates and selecting eligible rounds.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="compName">Competition Name</Label>
                    <Input
                      id="compName"
                      value={newCompetition.name}
                      onChange={e => setNewCompetition({ ...newCompetition, name: e.target.value })}
                      placeholder="e.g., Winter Championship 2025"
                    />
                  </div>
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label htmlFor="startDate">Start Date</Label>
                      <Input
                        id="startDate"
                        type="date"
                        value={newCompetition.startDate}
                        onChange={e => setNewCompetition({ ...newCompetition, startDate: e.target.value })}
                      />
                    </div>
                    <div>
                      <Label htmlFor="endDate">End Date</Label>
                      <Input
                        id="endDate"
                        type="date"
                        value={newCompetition.endDate}
                        onChange={e => setNewCompetition({ ...newCompetition, endDate: e.target.value })}
                      />
                    </div>
                  </div>
                  <div>
                    <Label>Included Rounds</Label>
                    <div className="space-y-2 mt-2">
                      {rounds.map(round => (
                        <label key={round.id} className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={newCompetition.roundIds.includes(round.id)}
                            onChange={e => {
                              if (e.target.checked) {
                                setNewCompetition({
                                  ...newCompetition,
                                  roundIds: [...newCompetition.roundIds, round.id],
                                });
                              } else {
                                setNewCompetition({
                                  ...newCompetition,
                                  roundIds: newCompetition.roundIds.filter(id => id !== round.id),
                                });
                              }
                            }}
                          />
                          {round.name}
                        </label>
                      ))}
                    </div>
                  </div>
                  <Button onClick={handleAddCompetition} className="w-full">
                    Create Competition
                  </Button>
                </div>
              </DialogContent>
            </Dialog>
          </div>

          <div className="space-y-4">
            {competitions.map(comp => (
              <Card key={comp.id} className="p-4">
                <div className="flex items-start justify-between mb-2">
                  <h3>{comp.name}</h3>
                  <Button size="sm" variant="outline">
                    <Edit className="w-4 h-4 mr-1" />
                    Edit
                  </Button>
                </div>
                <div className="text-muted-foreground mb-2">
                  {new Date(comp.startDate).toLocaleDateString()} - {new Date(comp.endDate).toLocaleDateString()}
                </div>
                <div className="text-muted-foreground">
                  Rounds: {comp.roundIds.map(id => rounds.find(r => r.id === id)?.name).join(', ')}
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>

        {/* Championship Management Tab */}
        <TabsContent value="championship" className="space-y-4">
          <h2>Club Championship Settings</h2>
          
          <Card className="p-6 space-y-4">
            <div>
              <Label htmlFor="champYear">Championship Year</Label>
              <Input
                id="champYear"
                type="number"
                value={championshipSettings.year}
                onChange={e => setChampionshipSettings({ ...championshipSettings, year: parseInt(e.target.value) })}
              />
            </div>

            <div>
              <Label>Scores to include</Label>
              <Select
                value={championshipSettings.scoringRule}
                onValueChange={(value: 'Best score' | 'Best 2 scores') => setChampionshipSettings({ ...championshipSettings, scoringRule: value })}
              >
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Best score">Best score</SelectItem>
                  <SelectItem value="Best 2 scores">Best 2 scores</SelectItem>
                </SelectContent>
              </Select>
            </div>

            <div>
              <Label>Eligible Rounds</Label>
              <div className="space-y-2 mt-2">
                {rounds.map(round => (
                  <label key={round.id} className="flex items-center gap-2">
                    <input
                      type="checkbox"
                      checked={championshipSettings.roundIds.includes(round.id)}
                      onChange={e => {
                        if (e.target.checked) {
                          setChampionshipSettings({
                            ...championshipSettings,
                            roundIds: [...championshipSettings.roundIds, round.id],
                          });
                        } else {
                          setChampionshipSettings({
                            ...championshipSettings,
                            roundIds: championshipSettings.roundIds.filter(id => id !== round.id),
                          });
                        }
                      }}
                    />
                    {round.name}
                  </label>
                ))}
              </div>
            </div>

            <Button className="w-full">Save Championship Settings</Button>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
// Mock data for the Archery Club app
import { Round, Archer, Score, Competition, ChampionshipSettings, ArrowValue } from '../types/archery';

export const mockRounds: Round[] = [
  {
    id: 'wa900',
    name: 'WA 900',
    ranges: [
      { id: 'wa900-60', distance: '60m', faceSize: '122cm', numberOfEnds: 5 },
      { id: 'wa900-50', distance: '50m', faceSize: '122cm', numberOfEnds: 5 },
      { id: 'wa900-40', distance: '40m', faceSize: '80cm', numberOfEnds: 5 },
    ],
  },
  {
    id: 'melbourne',
    name: 'Melbourne',
    ranges: [
      { id: 'melb-90', distance: '90m', faceSize: '122cm', numberOfEnds: 6 },
      { id: 'melb-70', distance: '70m', faceSize: '122cm', numberOfEnds: 6 },
    ],
  },
  {
    id: 'brisbane',
    name: 'Brisbane',
    ranges: [
      { id: 'bris-70', distance: '70m', faceSize: '122cm', numberOfEnds: 5 },
      { id: 'bris-60', distance: '60m', faceSize: '122cm', numberOfEnds: 5 },
      { id: 'bris-50', distance: '50m', faceSize: '80cm', numberOfEnds: 5 },
      { id: 'bris-40', distance: '40m', faceSize: '80cm', numberOfEnds: 5 },
    ],
  },
  {
    id: 'canberra',
    name: 'Canberra',
    ranges: [
      { id: 'canb-90', distance: '90m', faceSize: '122cm', numberOfEnds: 6 },
      { id: 'canb-70', distance: '70m', faceSize: '122cm', numberOfEnds: 6 },
      { id: 'canb-50', distance: '50m', faceSize: '80cm', numberOfEnds: 6 },
    ],
  },
  {
    id: 'short-metric',
    name: 'Short Metric',
    ranges: [
      { id: 'sm-50', distance: '50m', faceSize: '80cm', numberOfEnds: 6 },
      { id: 'sm-30', distance: '30m', faceSize: '80cm', numberOfEnds: 6 },
    ],
  },
];

export const mockArchers: Archer[] = [
  {
    id: 'archer1',
    memberId: 'AV12345',
    fullName: 'Sarah Johnson',
    birthYear: 1995,
    gender: 'Female',
    defaultDivision: 'Recurve',
  },
  {
    id: 'archer2',
    memberId: 'AV12346',
    fullName: 'Michael Chen',
    birthYear: 1988,
    gender: 'Male',
    defaultDivision: 'Compound',
  },
  {
    id: 'archer3',
    memberId: 'AV12347',
    fullName: 'Emma Wilson',
    birthYear: 2007,
    gender: 'Female',
    defaultDivision: 'Recurve',
  },
  {
    id: 'archer4',
    memberId: 'AV12348',
    fullName: 'James Anderson',
    birthYear: 1965,
    gender: 'Male',
    defaultDivision: 'Barebow',
  },
  {
    id: 'archer5',
    memberId: 'AV12349',
    fullName: 'Lisa Thompson',
    birthYear: 1992,
    gender: 'Female',
    defaultDivision: 'Compound',
  },
];

// Helper function to calculate arrow value
const getArrowPoints = (arrow: ArrowValue | null): number => {
  if (!arrow) return 0;
  if (arrow === 'X' || arrow === '10') return 10;
  if (arrow === 'M') return 0;
  return parseInt(arrow);
};

// Helper function to count X's
const countXs = (arrows: (ArrowValue | null)[]): number => {
  return arrows.filter(a => a === 'X').length;
};

// Generate some mock end data
const generateMockEnd = (endNumber: number): ArrowValue[] => {
  const possibleScores: ArrowValue[] = ['X', '10', '9', '9', '8', '7', '8', '9', '10', 'X'];
  const shuffled = [...possibleScores].sort(() => Math.random() - 0.5);
  return shuffled.slice(0, 6) as ArrowValue[];
};

export const mockScores: Score[] = [
  {
    id: 'score1',
    archerId: 'archer1',
    archerName: 'Sarah Johnson',
    roundId: 'wa900',
    roundName: 'WA 900',
    date: '2025-11-01',
    division: 'Recurve',
    status: 'Confirmed',
    rangeScores: [
      {
        rangeId: 'wa900-60',
        distance: '60m',
        faceSize: '122cm',
        ends: [
          { endNumber: 1, arrows: ['X', '10', '9', '9', '8', '7'], total: 53 },
          { endNumber: 2, arrows: ['10', '9', '9', '8', '8', '7'], total: 51 },
          { endNumber: 3, arrows: ['X', '10', '10', '9', '8', '8'], total: 55 },
          { endNumber: 4, arrows: ['9', '9', '9', '8', '7', '7'], total: 49 },
          { endNumber: 5, arrows: ['10', '9', '9', '8', '8', '8'], total: 52 },
        ],
        total: 260,
        xCount: 2,
      },
      {
        rangeId: 'wa900-50',
        distance: '50m',
        faceSize: '122cm',
        ends: [
          { endNumber: 1, arrows: ['X', 'X', '10', '9', '9', '8'], total: 56 },
          { endNumber: 2, arrows: ['10', '10', '9', '9', '8', '8'], total: 54 },
          { endNumber: 3, arrows: ['X', '10', '9', '9', '9', '8'], total: 55 },
          { endNumber: 4, arrows: ['10', '9', '9', '9', '8', '7'], total: 52 },
          { endNumber: 5, arrows: ['X', '10', '10', '9', '8', '8'], total: 55 },
        ],
        total: 272,
        xCount: 4,
      },
      {
        rangeId: 'wa900-40',
        distance: '40m',
        faceSize: '80cm',
        ends: [
          { endNumber: 1, arrows: ['X', 'X', '10', '10', '9', '9'], total: 58 },
          { endNumber: 2, arrows: ['X', '10', '10', '9', '9', '8'], total: 56 },
          { endNumber: 3, arrows: ['10', '10', '9', '9', '9', '9'], total: 56 },
          { endNumber: 4, arrows: ['X', '10', '10', '9', '9', '8'], total: 56 },
          { endNumber: 5, arrows: ['X', 'X', '10', '9', '9', '8'], total: 56 },
        ],
        total: 282,
        xCount: 6,
      },
    ],
    totalScore: 814,
    xCount: 12,
  },
  {
    id: 'score2',
    archerId: 'archer1',
    archerName: 'Sarah Johnson',
    roundId: 'brisbane',
    roundName: 'Brisbane',
    date: '2025-10-15',
    division: 'Recurve',
    status: 'Confirmed',
    rangeScores: [
      {
        rangeId: 'bris-70',
        distance: '70m',
        faceSize: '122cm',
        ends: [
          { endNumber: 1, arrows: ['10', '9', '9', '8', '8', '7'], total: 51 },
          { endNumber: 2, arrows: ['X', '9', '9', '8', '7', '7'], total: 50 },
          { endNumber: 3, arrows: ['10', '10', '9', '8', '8', '7'], total: 52 },
          { endNumber: 4, arrows: ['9', '9', '8', '8', '7', '6'], total: 47 },
          { endNumber: 5, arrows: ['10', '9', '9', '8', '8', '7'], total: 51 },
        ],
        total: 251,
        xCount: 1,
      },
      {
        rangeId: 'bris-60',
        distance: '60m',
        faceSize: '122cm',
        ends: [
          { endNumber: 1, arrows: ['X', '10', '9', '9', '8', '8'], total: 54 },
          { endNumber: 2, arrows: ['10', '9', '9', '9', '8', '7'], total: 52 },
          { endNumber: 3, arrows: ['X', '10', '9', '8', '8', '8'], total: 53 },
          { endNumber: 4, arrows: ['10', '9', '9', '8', '8', '7'], total: 51 },
          { endNumber: 5, arrows: ['10', '10', '9', '9', '8', '7'], total: 53 },
        ],
        total: 263,
        xCount: 2,
      },
      {
        rangeId: 'bris-50',
        distance: '50m',
        faceSize: '80cm',
        ends: [
          { endNumber: 1, arrows: ['X', '10', '10', '9', '9', '8'], total: 56 },
          { endNumber: 2, arrows: ['X', '10', '9', '9', '9', '8'], total: 55 },
          { endNumber: 3, arrows: ['10', '10', '9', '9', '8', '8'], total: 54 },
          { endNumber: 4, arrows: ['X', '10', '10', '9', '8', '8'], total: 55 },
          { endNumber: 5, arrows: ['10', '9', '9', '9', '9', '8'], total: 54 },
        ],
        total: 274,
        xCount: 3,
      },
      {
        rangeId: 'bris-40',
        distance: '40m',
        faceSize: '80cm',
        ends: [
          { endNumber: 1, arrows: ['X', 'X', '10', '10', '9', '9'], total: 58 },
          { endNumber: 2, arrows: ['X', '10', '10', '9', '9', '9'], total: 57 },
          { endNumber: 3, arrows: ['10', '10', '10', '9', '9', '8'], total: 56 },
          { endNumber: 4, arrows: ['X', '10', '10', '9', '9', '8'], total: 56 },
          { endNumber: 5, arrows: ['X', 'X', '10', '10', '9', '8'], total: 57 },
        ],
        total: 284,
        xCount: 6,
      },
    ],
    totalScore: 1072,
    xCount: 12,
  },
  {
    id: 'score3',
    archerId: 'archer1',
    archerName: 'Sarah Johnson',
    roundId: 'wa900',
    roundName: 'WA 900',
    date: '2025-09-22',
    division: 'Recurve',
    status: 'Preliminary',
    rangeScores: [
      {
        rangeId: 'wa900-60',
        distance: '60m',
        faceSize: '122cm',
        ends: [
          { endNumber: 1, arrows: ['X', '10', '9', '8', '8', '7'], total: 52 },
          { endNumber: 2, arrows: ['10', '9', '9', '8', '7', '7'], total: 50 },
          { endNumber: 3, arrows: ['X', '10', '9', '9', '8', '7'], total: 53 },
          { endNumber: 4, arrows: ['9', '9', '8', '8', '7', '7'], total: 48 },
          { endNumber: 5, arrows: ['10', '9', '9', '8', '8', '7'], total: 51 },
        ],
        total: 254,
        xCount: 2,
      },
      {
        rangeId: 'wa900-50',
        distance: '50m',
        faceSize: '122cm',
        ends: [
          { endNumber: 1, arrows: ['X', '10', '10', '9', '8', '8'], total: 55 },
          { endNumber: 2, arrows: ['10', '10', '9', '9', '8', '7'], total: 53 },
          { endNumber: 3, arrows: ['X', '10', '9', '9', '8', '8'], total: 54 },
          { endNumber: 4, arrows: ['10', '9', '9', '8', '8', '7'], total: 51 },
          { endNumber: 5, arrows: ['X', '10', '9', '9', '9', '8'], total: 55 },
        ],
        total: 268,
        xCount: 3,
      },
      {
        rangeId: 'wa900-40',
        distance: '40m',
        faceSize: '80cm',
        ends: [
          { endNumber: 1, arrows: ['X', 'X', '10', '9', '9', '9'], total: 57 },
          { endNumber: 2, arrows: ['X', '10', '10', '9', '9', '8'], total: 56 },
          { endNumber: 3, arrows: ['10', '10', '9', '9', '9', '8'], total: 55 },
          { endNumber: 4, arrows: ['X', '10', '10', '9', '8', '8'], total: 55 },
          { endNumber: 5, arrows: ['X', 'X', '10', '10', '9', '8'], total: 57 },
        ],
        total: 280,
        xCount: 6,
      },
    ],
    totalScore: 802,
    xCount: 11,
  },
  {
    id: 'score4',
    archerId: 'archer2',
    archerName: 'Michael Chen',
    roundId: 'wa900',
    roundName: 'WA 900',
    date: '2025-11-01',
    division: 'Compound',
    status: 'Confirmed',
    rangeScores: [
      {
        rangeId: 'wa900-60',
        distance: '60m',
        faceSize: '122cm',
        ends: [
          { endNumber: 1, arrows: ['X', 'X', 'X', '10', '10', '10'], total: 60 },
          { endNumber: 2, arrows: ['X', 'X', '10', '10', '10', '9'], total: 59 },
          { endNumber: 3, arrows: ['X', 'X', 'X', '10', '10', '9'], total: 59 },
          { endNumber: 4, arrows: ['X', '10', '10', '10', '10', '9'], total: 59 },
          { endNumber: 5, arrows: ['X', 'X', '10', '10', '10', '10'], total: 60 },
        ],
        total: 297,
        xCount: 11,
      },
      {
        rangeId: 'wa900-50',
        distance: '50m',
        faceSize: '122cm',
        ends: [
          { endNumber: 1, arrows: ['X', 'X', 'X', '10', '10', '10'], total: 60 },
          { endNumber: 2, arrows: ['X', 'X', '10', '10', '10', '10'], total: 60 },
          { endNumber: 3, arrows: ['X', 'X', 'X', 'X', '10', '10'], total: 60 },
          { endNumber: 4, arrows: ['X', 'X', '10', '10', '10', '9'], total: 59 },
          { endNumber: 5, arrows: ['X', 'X', 'X', '10', '10', '10'], total: 60 },
        ],
        total: 299,
        xCount: 15,
      },
      {
        rangeId: 'wa900-40',
        distance: '40m',
        faceSize: '80cm',
        ends: [
          { endNumber: 1, arrows: ['X', 'X', 'X', 'X', '10', '10'], total: 60 },
          { endNumber: 2, arrows: ['X', 'X', 'X', '10', '10', '10'], total: 60 },
          { endNumber: 3, arrows: ['X', 'X', 'X', 'X', 'X', '10'], total: 60 },
          { endNumber: 4, arrows: ['X', 'X', '10', '10', '10', '10'], total: 60 },
          { endNumber: 5, arrows: ['X', 'X', 'X', 'X', '10', '10'], total: 60 },
        ],
        total: 300,
        xCount: 19,
      },
    ],
    totalScore: 896,
    xCount: 45,
  },
  {
    id: 'score5',
    archerId: 'archer3',
    archerName: 'Emma Wilson',
    roundId: 'short-metric',
    roundName: 'Short Metric',
    date: '2025-10-28',
    division: 'Recurve',
    status: 'Confirmed',
    rangeScores: [
      {
        rangeId: 'sm-50',
        distance: '50m',
        faceSize: '80cm',
        ends: [
          { endNumber: 1, arrows: ['10', '10', '9', '9', '8', '8'], total: 54 },
          { endNumber: 2, arrows: ['X', '10', '9', '9', '8', '7'], total: 53 },
          { endNumber: 3, arrows: ['10', '9', '9', '9', '8', '8'], total: 53 },
          { endNumber: 4, arrows: ['X', '10', '9', '8', '8', '7'], total: 52 },
          { endNumber: 5, arrows: ['10', '10', '9', '9', '8', '7'], total: 53 },
          { endNumber: 6, arrows: ['X', '10', '10', '9', '8', '8'], total: 55 },
        ],
        total: 320,
        xCount: 3,
      },
      {
        rangeId: 'sm-30',
        distance: '30m',
        faceSize: '80cm',
        ends: [
          { endNumber: 1, arrows: ['X', 'X', '10', '10', '9', '9'], total: 58 },
          { endNumber: 2, arrows: ['X', '10', '10', '9', '9', '9'], total: 57 },
          { endNumber: 3, arrows: ['X', 'X', '10', '10', '9', '8'], total: 57 },
          { endNumber: 4, arrows: ['X', '10', '10', '10', '9', '9'], total: 58 },
          { endNumber: 5, arrows: ['X', 'X', '10', '9', '9', '9'], total: 57 },
          { endNumber: 6, arrows: ['X', '10', '10', '10', '10', '9'], total: 59 },
        ],
        total: 346,
        xCount: 8,
      },
    ],
    totalScore: 666,
    xCount: 11,
  },
];

export const mockCompetitions: Competition[] = [
  {
    id: 'comp1',
    name: 'Spring Championship 2025',
    startDate: '2025-10-01',
    endDate: '2025-10-15',
    roundIds: ['wa900', 'brisbane'],
  },
  {
    id: 'comp2',
    name: 'Summer Open 2025',
    startDate: '2025-11-01',
    endDate: '2025-11-05',
    roundIds: ['wa900', 'melbourne'],
  },
];

export const mockChampionshipSettings: ChampionshipSettings = {
  year: 2025,
  roundIds: ['wa900', 'canberra', 'brisbane'],
  scoringRule: 'Best 2 scores',
};
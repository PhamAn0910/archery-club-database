// Core data types for the Archery Club app

export type ArrowValue = 'X' | '10' | '9' | '8' | '7' | '6' | '5' | '4' | '3' | '2' | '1' | 'M';

export type Division = 'Recurve' | 'Compound' | 'Barebow' | 'Longbow';

export type Gender = 'Male' | 'Female' | 'Other';

export type AgeClass = 'Under 18' | 'Open' | '50+' | '60+' | '70+';

export type FaceSize = '122cm' | '80cm' | '60cm' | '40cm';

export interface Range {
  id: string;
  distance: string; // e.g., "70m", "60m"
  faceSize: FaceSize;
  numberOfEnds: number;
}

export interface Round {
  id: string;
  name: string;
  ranges: Range[];
}

export interface End {
  endNumber: number;
  arrows: (ArrowValue | null)[];
  total: number;
}

export interface RangeScore {
  rangeId: string;
  distance: string;
  faceSize: FaceSize;
  ends: End[];
  total: number;
  xCount: number;
}

export type ScoreStatus = 'Preliminary' | 'Confirmed' | 'Rejected';

export interface Score {
  id: string;
  archerId: string;
  archerName: string;
  roundId: string;
  roundName: string;
  date: string;
  rangeScores: RangeScore[];
  totalScore: number;
  xCount: number;
  status: ScoreStatus;
  division: Division;
}

export interface Archer {
  id: string;
  memberId: string;
  fullName: string;
  birthYear: number;
  gender: Gender;
  defaultDivision: Division;
}

export interface Competition {
  id: string;
  name: string;
  startDate: string;
  endDate: string;
  roundIds: string[];
}

export interface Category {
  gender: Gender;
  ageClass: AgeClass;
  division: Division;
}

export interface CompetitionResult extends Score {
  category: string;
  rank: number;
}

export interface ChampionshipSettings {
  year: number;
  roundIds: string[];
  scoringRule: 'Best score' | 'Best 2 scores';
}

export interface PersonalBest {
  roundId: string;
  roundName: string;
  score: number;
  date: string;
  division: Division;
}
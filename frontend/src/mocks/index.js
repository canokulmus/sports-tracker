// src/mocks/index.js
// DEPRECATED: These mock data are no longer used.
// The application now uses real WebSocket API (ws://localhost:8888)
// Kept for reference only.

// ==========================================
// TEAMS
// ==========================================
export const mockTeams = [
  { 
    id: 1, 
    name: "Galatasaray", 
    players: { "Icardi": { no: 9 }, "Muslera": { no: 1 }, "Mertens": { no: 14 } }
  },
  { 
    id: 2, 
    name: "Fenerbahçe", 
    players: { "Dzeko": { no: 9 }, "Altay": { no: 1 } }
  },
  { 
    id: 3, 
    name: "Beşiktaş", 
    players: { "Muci": { no: 7 }, "Ersin": { no: 1 } }
  },
  { 
    id: 4, 
    name: "Trabzonspor", 
    players: { "Trezeguet": { no: 10 } }
  },
  { id: 5, name: "Başakşehir", players: {} },
  { id: 6, name: "Adana Demirspor", players: {} },
  { id: 7, name: "Antalyaspor", players: {} },
  { id: 8, name: "Konyaspor", players: {} },
];

// ==========================================
// GAMES
// ==========================================
export const mockGames = [
  {
    id: 1,
    home: { id: 1, name: "Galatasaray" },
    away: { id: 2, name: "Fenerbahçe" },
    state: "RUNNING",
    score: { home: 2, away: 1 },
    scorers: {
      home: [
        { player: "Icardi", minute: 23 },
        { player: "Mertens", minute: 67 },
      ],
      away: [
        { player: "Dzeko", minute: 45 },
      ],
    },
    datetime: "2025-01-15T20:00:00",
    group: null,
  },
  {
    id: 2,
    home: { id: 3, name: "Beşiktaş" },
    away: { id: 4, name: "Trabzonspor" },
    state: "READY",
    score: { home: 0, away: 0 },
    scorers: { home: [], away: [] },
    datetime: "2025-01-15T19:00:00",
    group: null,
  },
  {
    id: 3,
    home: { id: 5, name: "Başakşehir" },
    away: { id: 6, name: "Adana Demirspor" },
    state: "ENDED",
    score: { home: 3, away: 3 },
    scorers: {
      home: [
        { player: "Oyuncu 1", minute: 12 },
        { player: "Oyuncu 1", minute: 55 },
        { player: "Oyuncu 2", minute: 78 },
      ],
      away: [
        { player: "Oyuncu A", minute: 30 },
        { player: "Oyuncu B", minute: 60 },
        { player: "Oyuncu B", minute: 88 },
      ],
    },
    datetime: "2025-01-14T20:00:00",
    group: null,
  },
  {
    id: 4,
    home: { id: 7, name: "Antalyaspor" },
    away: { id: 8, name: "Konyaspor" },
    state: "PAUSED",
    score: { home: 1, away: 0 },
    scorers: {
      home: [{ player: "Oyuncu X", minute: 35 }],
      away: [],
    },
    datetime: "2025-01-15T17:00:00",
    group: null,
  },
];

// ==========================================
// CUPS
// ==========================================
export const mockCups = [
  {
    id: 1,
    name: "Süper Lig 2024-25",
    type: "LEAGUE",
    teams: [1, 2, 3, 4, 5, 6, 7, 8],
    gameCount: 56,
  },
  {
    id: 2,
    name: "Türkiye Kupası",
    type: "ELIMINATION",
    teams: [1, 2, 3, 4, 5, 6, 7, 8],
    gameCount: 7,
  },
  {
    id: 3,
    name: "Şampiyonlar Ligi Grubu",
    type: "GROUP",
    teams: [1, 2, 3, 4, 5, 6, 7, 8],
    gameCount: 18,
  },
];

// ==========================================
// STANDINGS (LEAGUE)
// ==========================================
export const mockStandings = [
  { team: "Galatasaray", played: 11, won: 8, draw: 2, lost: 1, gf: 24, ga: 10, points: 18 },
  { team: "Fenerbahçe", played: 11, won: 7, draw: 3, lost: 1, gf: 20, ga: 8, points: 17 },
  { team: "Beşiktaş", played: 11, won: 6, draw: 2, lost: 3, gf: 18, ga: 12, points: 14 },
  { team: "Trabzonspor", played: 11, won: 5, draw: 3, lost: 3, gf: 15, ga: 11, points: 13 },
  { team: "Başakşehir", played: 11, won: 4, draw: 4, lost: 3, gf: 14, ga: 13, points: 12 },
  { team: "Adana Demirspor", played: 11, won: 3, draw: 3, lost: 5, gf: 12, ga: 16, points: 9 },
  { team: "Antalyaspor", played: 11, won: 2, draw: 2, lost: 7, gf: 9, ga: 20, points: 6 },
  { team: "Konyaspor", played: 11, won: 1, draw: 1, lost: 9, gf: 6, ga: 28, points: 3 },
];

// ==========================================
// GAMETREE DATA
// ==========================================

// GameTree for ELIMINATION tournament (Türkiye Kupası)
export const mockGameTreeElimination = {
  "Quarter-Final": [
    {
      game_id: 101,
      home: "Galatasaray",
      away: "Konyaspor",
      datetime: "2025-01-10 20:00",
      state: "ENDED",
      score: { home: 3, away: 0 }
    },
    {
      game_id: 102,
      home: "Fenerbahçe",
      away: "Antalyaspor",
      datetime: "2025-01-10 20:00",
      state: "ENDED",
      score: { home: 2, away: 1 }
    },
    {
      game_id: 103,
      home: "Beşiktaş",
      away: "Adana Demirspor",
      datetime: "2025-01-11 20:00",
      state: "ENDED",
      score: { home: 1, away: 0 }
    },
    {
      game_id: 104,
      home: "Trabzonspor",
      away: "Başakşehir",
      datetime: "2025-01-11 20:00",
      state: "ENDED",
      score: { home: 2, away: 1 }
    },
  ],
  "Semi-Final": [
    {
      game_id: 105,
      home: "Galatasaray",
      away: "Fenerbahçe",
      datetime: "2025-01-18 21:00",
      state: "RUNNING",
      score: { home: 1, away: 1 }
    },
    {
      game_id: 106,
      home: "Beşiktaş",
      away: "Trabzonspor",
      datetime: "2025-01-18 21:00",
      state: "READY",
      score: null
    },
  ],
  "Final": [
    {
      game_id: 107,
      home: "Winner of Game 105",
      away: "Winner of Game 106",
      datetime: "2025-01-25 21:00",
      state: "READY",
      score: null
    },
  ],
};

// GameTree for GROUP tournament (Şampiyonlar Ligi Grubu)
export const mockGameTreeGroup = {
  "Groups": {
    "A": [
      {
        game_id: 201,
        home: "Galatasaray",
        away: "Fenerbahçe",
        datetime: "2025-01-05 20:00",
        state: "ENDED",
        score: { home: 2, away: 1 }
      },
      {
        game_id: 202,
        home: "Galatasaray",
        away: "Beşiktaş",
        datetime: "2025-01-08 20:00",
        state: "ENDED",
        score: { home: 1, away: 1 }
      },
      {
        game_id: 203,
        home: "Fenerbahçe",
        away: "Beşiktaş",
        datetime: "2025-01-11 20:00",
        state: "ENDED",
        score: { home: 0, away: 2 }
      },
    ],
    "B": [
      {
        game_id: 204,
        home: "Trabzonspor",
        away: "Başakşehir",
        datetime: "2025-01-05 20:00",
        state: "ENDED",
        score: { home: 3, away: 1 }
      },
      {
        game_id: 205,
        home: "Trabzonspor",
        away: "Adana Demirspor",
        datetime: "2025-01-08 20:00",
        state: "ENDED",
        score: { home: 2, away: 0 }
      },
      {
        game_id: 206,
        home: "Başakşehir",
        away: "Adana Demirspor",
        datetime: "2025-01-11 20:00",
        state: "ENDED",
        score: { home: 1, away: 1 }
      },
    ],
  },
  "Playoffs": {
    "Semi-Final": [
      {
        game_id: 207,
        home: "Galatasaray",
        away: "Trabzonspor",
        datetime: "2025-01-18 21:00",
        state: "RUNNING",
        score: { home: 2, away: 1 }
      },
      {
        game_id: 208,
        home: "Beşiktaş",
        away: "Başakşehir",
        datetime: "2025-01-18 21:00",
        state: "READY",
        score: null
      },
    ],
    "Final": [
      {
        game_id: 209,
        home: "Winner of Game 207",
        away: "Winner of Game 208",
        datetime: "2025-01-25 21:00",
        state: "READY",
        score: null
      },
    ],
  },
};

// Group standings for GROUP tournament
export const mockGroupStandings = {
  "A": [
    { team: "Beşiktaş", played: 2, won: 1, draw: 1, lost: 0, gf: 3, ga: 1, points: 3 },
    { team: "Galatasaray", played: 2, won: 1, draw: 1, lost: 0, gf: 3, ga: 2, points: 3 },
    { team: "Fenerbahçe", played: 2, won: 0, draw: 0, lost: 2, gf: 1, ga: 4, points: 0 },
  ],
  "B": [
    { team: "Trabzonspor", played: 2, won: 2, draw: 0, lost: 0, gf: 5, ga: 1, points: 4 },
    { team: "Başakşehir", played: 2, won: 0, draw: 1, lost: 1, gf: 2, ga: 4, points: 1 },
    { team: "Adana Demirspor", played: 2, won: 0, draw: 1, lost: 1, gf: 1, ga: 3, points: 1 },
  ],
};

// ==========================================
// HELPERS
// ==========================================
export const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

let nextId = 100;
export const generateId = () => ++nextId;
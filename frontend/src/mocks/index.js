// src/mocks/index.js
// Backend hazır olana kadar kullanılacak mock veriler

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
// BRACKET (ELIMINATION)
// ==========================================
export const mockBracket = {
  "Quarter-Final": [
    { game_id: 101, home: "Galatasaray", away: "Konyaspor", state: "ENDED", score: { home: 3, away: 0 } },
    { game_id: 102, home: "Fenerbahçe", away: "Antalyaspor", state: "ENDED", score: { home: 2, away: 1 } },
    { game_id: 103, home: "Beşiktaş", away: "Adana Demirspor", state: "ENDED", score: { home: 1, away: 0 } },
    { game_id: 104, home: "Trabzonspor", away: "Başakşehir", state: "ENDED", score: { home: 2, away: 2 } },
  ],
  "Semi-Final": [
    { game_id: 105, home: "Galatasaray", away: "Fenerbahçe", state: "RUNNING", score: { home: 1, away: 1 } },
    { game_id: 106, home: "Beşiktaş", away: "Trabzonspor", state: "READY", score: null },
  ],
  "Final": [
    { game_id: 107, home: "Winner SF1", away: "Winner SF2", state: "READY", score: null },
  ],
};

// ==========================================
// HELPERS
// ==========================================
export const delay = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

let nextId = 100;
export const generateId = () => ++nextId;
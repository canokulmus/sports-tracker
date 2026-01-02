// src/services/api.js
// Mock API servisi - Backend hazır olunca WebSocket'e çevrilecek

import { 
  mockTeams, 
  mockGames, 
  mockCups, 
  mockStandings,
  mockBracket,
  delay, 
  generateId 
} from '../mocks';

// Lokal state (mock database gibi)
let teams = [...mockTeams];
let games = [...mockGames];
let cups = [...mockCups];

// ==========================================
// TEAM API
// ==========================================
export const teamApi = {
  getAll: async () => {
    await delay(300);
    return [...teams];
  },

  getById: async (id) => {
    await delay(200);
    return teams.find((t) => t.id === id) || null;
  },

  create: async (name) => {
    await delay(300);
    const newTeam = {
      id: generateId(),
      name,
      players: {},
    };
    teams.push(newTeam);
    return newTeam;
  },

  delete: async (id) => {
    await delay(200);
    teams = teams.filter((t) => t.id !== id);
    return { success: true };
  },

  addPlayer: async (teamId, playerName, playerNo) => {
    await delay(200);
    const team = teams.find((t) => t.id === teamId);
    if (team) {
      team.players[playerName] = { no: playerNo };
      return team;
    }
    throw new Error("Team not found");
  },

  removePlayer: async (teamId, playerName) => {
    await delay(200);
    const team = teams.find((t) => t.id === teamId);
    if (team && team.players[playerName]) {
      delete team.players[playerName];
      return team;
    }
    throw new Error("Player not found");
  },
};

// ==========================================
// GAME API
// ==========================================
export const gameApi = {
  getAll: async () => {
    await delay(300);
    return [...games];
  },

  getById: async (id) => {
    await delay(200);
    return games.find((g) => g.id === id) || null;
  },

  // Maç için takım oyuncularını getir
  getPlayersForGame: async (gameId) => {
    await delay(100);
    const game = games.find((g) => g.id === gameId);
    if (!game) return { home: [], away: [] };
    
    const homeTeam = teams.find((t) => t.id === game.home.id);
    const awayTeam = teams.find((t) => t.id === game.away.id);
    
    return {
      home: homeTeam ? Object.keys(homeTeam.players) : [],
      away: awayTeam ? Object.keys(awayTeam.players) : [],
    };
  },

  create: async (homeId, awayId) => {
    await delay(300);
    const home = teams.find((t) => t.id === homeId);
    const away = teams.find((t) => t.id === awayId);
    
    if (!home || !away) throw new Error("Team not found");

    const newGame = {
      id: generateId(),
      home: { id: home.id, name: home.name },
      away: { id: away.id, name: away.name },
      state: "READY",
      score: { home: 0, away: 0 },
      scorers: { home: [], away: [] },
      datetime: new Date().toISOString(),
      group: null,
    };
    games.push(newGame);
    return newGame;
  },

  start: async (id) => {
    await delay(200);
    const game = games.find((g) => g.id === id);
    if (game) {
      game.state = "RUNNING";
      return game;
    }
    throw new Error("Game not found");
  },

  pause: async (id) => {
    await delay(200);
    const game = games.find((g) => g.id === id);
    if (game) {
      game.state = "PAUSED";
      return game;
    }
    throw new Error("Game not found");
  },

  resume: async (id) => {
    await delay(200);
    const game = games.find((g) => g.id === id);
    if (game) {
      game.state = "RUNNING";
      return game;
    }
    throw new Error("Game not found");
  },

  end: async (id) => {
    await delay(200);
    const game = games.find((g) => g.id === id);
    if (game) {
      game.state = "ENDED";
      return game;
    }
    throw new Error("Game not found");
  },

  score: async (id, side, playerName, points = 1) => {
    await delay(100);
    const game = games.find((g) => g.id === id);
    if (game && game.state === "RUNNING") {
      game.score[side] += points;
      // Gol atan oyuncuyu ekle
      if (playerName) {
        if (!game.scorers) {
          game.scorers = { home: [], away: [] };
        }
        game.scorers[side].push({
          player: playerName,
          minute: Math.floor(Math.random() * 90) + 1, // Mock dakika
        });
      }
      return game;
    }
    throw new Error("Cannot score");
  },

  delete: async (id) => {
    await delay(200);
    games = games.filter((g) => g.id !== id);
    return { success: true };
  },
};

// ==========================================
// CUP API
// ==========================================
export const cupApi = {
  getAll: async () => {
    await delay(300);
    return [...cups];
  },

  getById: async (id) => {
    await delay(200);
    return cups.find((c) => c.id === id) || null;
  },

  getStandings: async (id) => {
    await delay(300);
    // Mock için sabit standings döndür
    return [...mockStandings];
  },

  getBracket: async (id) => {
    await delay(300);
    // Mock için sabit bracket döndür
    return { ...mockBracket };
  },

  create: async (name, type, teamIds) => {
    await delay(400);
    const newCup = {
      id: generateId(),
      name,
      type,
      teams: teamIds,
      gameCount: type === "LEAGUE" ? (teamIds.length * (teamIds.length - 1)) / 2 : teamIds.length - 1,
    };
    cups.push(newCup);
    return newCup;
  },

  delete: async (id) => {
    await delay(200);
    cups = cups.filter((c) => c.id !== id);
    return { success: true };
  },
};

// ==========================================
// LIVE GAMES (Canlı maçlar)
// ==========================================
export const liveApi = {
  getRunningGames: async () => {
    await delay(200);
    return games.filter((g) => g.state === "RUNNING" || g.state === "PAUSED");
  },
};
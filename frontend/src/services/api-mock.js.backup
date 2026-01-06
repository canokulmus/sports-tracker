// src/services/api.js
// Mock API servisi - Backend hazır olunca WebSocket'e çevrilecek

import {
  mockTeams,
  mockGames,
  mockCups,
  mockStandings,
  mockGameTreeElimination,
  mockGameTreeGroup,
  mockGroupStandings,
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

  setCustomField: async (teamId, key, value) => {
    await delay(200);
    const team = teams.find((t) => t.id === teamId);
    if (team) {
      team[key] = value;
      return team;
    }
    throw new Error("Team not found");
  },

  deleteCustomField: async (teamId, key) => {
    await delay(200);
    const team = teams.find((t) => t.id === teamId);
    if (team && team[key] !== undefined) {
      delete team[key];
      return team;
    }
    throw new Error("Field not found");
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
    const cup = cups.find((c) => c.id === id);

    if (!cup) {
      throw new Error("Cup not found");
    }

    // GROUP tournament için grup bazlı standings
    if (cup.type === 'GROUP') {
      return { ...mockGroupStandings };
    }

    // LEAGUE için normal standings
    return [...mockStandings];
  },

  getGameTree: async (id) => {
    await delay(300);
    const cup = cups.find((c) => c.id === id);

    if (!cup) {
      throw new Error("Cup not found");
    }

    // Only ELIMINATION and GROUP tournaments have GameTree
    if (cup.type === 'LEAGUE') {
      throw new Error("GameTree is not available for LEAGUE tournaments");
    }

    if (cup.type === 'ELIMINATION') {
      return { ...mockGameTreeElimination };
    }

    if (cup.type === 'GROUP') {
      return { ...mockGameTreeGroup };
    }

    throw new Error("Unknown cup type");
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

// ==========================================
// WATCH API (Observer Pattern - Mock)
// ==========================================
const watchedGames = new Set();
const watchCallbacks = new Map();

export const watchApi = {
  watch: async (gameId, callback) => {
    await delay(100);
    watchedGames.add(gameId);

    if (callback) {
      if (!watchCallbacks.has(gameId)) {
        watchCallbacks.set(gameId, []);
      }
      watchCallbacks.get(gameId).push(callback);
    }

    return { success: true, gameId };
  },

  unwatch: async (gameId) => {
    await delay(100);
    watchedGames.delete(gameId);
    watchCallbacks.delete(gameId);
    return { success: true, gameId };
  },

  getWatchedGames: async () => {
    await delay(100);
    return Array.from(watchedGames);
  },

  isWatching: async (gameId) => {
    await delay(50);
    return watchedGames.has(gameId);
  },

  notifyWatchers: (gameId, event) => {
    const callbacks = watchCallbacks.get(gameId);
    if (callbacks && callbacks.length > 0) {
      callbacks.forEach(cb => cb(event));
    }
  },
};

export function simulateGameUpdate(gameId, updateType = 'score') {
  const game = games.find((g) => g.id === gameId);

  // Check localStorage for watched games instead of internal Set
  const watchedGamesFromStorage = JSON.parse(localStorage.getItem('watchedGames') || '[]');

  if (!game) {
    console.log('[Simulate Update] Game not found:', gameId);
    return;
  }

  if (!watchedGamesFromStorage.includes(gameId)) {
    console.log('[Simulate Update] Game not being watched:', gameId);
    return;
  }

  if (game.state !== 'RUNNING' && game.state !== 'PAUSED') {
    console.log('[Simulate Update] Skipping - game not live:', gameId, 'State:', game.state);
    return;
  }

  const event = {
    gameId,
    type: updateType,
    timestamp: new Date().toISOString(),
    game: { ...game },
  };

  if (updateType === 'score' && game.state === 'RUNNING') {
    const side = Math.random() > 0.5 ? 'home' : 'away';
    game.score[side] += 1;
    event.side = side;
    event.score = { ...game.score };
    console.log('[Simulate Update] Score updated:', gameId, event.score);
  } else if (updateType === 'state') {
    event.oldState = game.state;
    event.newState = game.state === 'RUNNING' ? 'PAUSED' : 'RUNNING';
    game.state = event.newState;
    console.log('[Simulate Update] State changed:', gameId, event.oldState, '->', event.newState);
  } else {
    return;
  }

  watchApi.notifyWatchers(gameId, event);
  return event;
}
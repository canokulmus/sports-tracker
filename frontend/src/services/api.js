// src/services/api.js
// WebSocket API service for Sports Tracker
// Connects to backend server via WebSocket (ws://localhost:8888)

import wsClient from './websocket';

// Helper to map backend state names to frontend
const mapGameState = (backendState) => {
  // Backend and frontend use the same state names:
  // READY, RUNNING, PAUSED, ENDED
  return backendState;
};

// Helper to transform backend game to frontend format
const transformGame = (backendGame) => {
  return {
    id: backendGame.id,
    home: {
      id: backendGame.home_id || backendGame.id, // Backend doesn't return team IDs separately
      name: backendGame.home
    },
    away: {
      id: backendGame.away_id || backendGame.id,
      name: backendGame.away
    },
    state: mapGameState(backendGame.state),
    score: {
      home: backendGame.score.home,
      away: backendGame.score.away
    },
    scorers: backendGame.scorers || { home: [], away: [] },
    datetime: backendGame.datetime || new Date().toISOString(),
    group: backendGame.group || null
  };
};

// ==========================================
// TEAM API
// ==========================================
export const teamApi = {
  getAll: async () => {
    const response = await wsClient.sendCommand('GET_TEAMS');
    return response.teams || [];
  },

  getById: async (id) => {
    const response = await wsClient.sendCommand('GET_TEAMS');
    return response.teams.find(t => t.id === id) || null;
  },

  create: async (name) => {
    const response = await wsClient.sendCommand('CREATE_TEAM', { name });
    return {
      id: response.id,
      name,
      players: {}
    };
  },

  delete: async (id) => {
    await wsClient.sendCommand('DELETE', { id });
    return { success: true };
  },

  addPlayer: async (teamId, playerName, playerNo) => {
    await wsClient.sendCommand('ADD_PLAYER', {
      team_id: teamId,
      name: playerName,
      no: playerNo
    });
    return await teamApi.getById(teamId);
  },

  removePlayer: async (teamId, playerName) => {
    await wsClient.sendCommand('REMOVE_PLAYER', {
      team_id: teamId,
      name: playerName
    });
    return await teamApi.getById(teamId);
  },

  setCustomField: async (teamId, key, value) => {
    const updates = { [key]: value };
    await wsClient.sendCommand('UPDATE_TEAM', {
      id: teamId,
      ...updates
    });
    return await teamApi.getById(teamId);
  },

  deleteCustomField: async (teamId, key) => {
    // Backend doesn't have explicit delete field command
    // We'll set it to empty string or handle it differently
    console.warn('Delete custom field not implemented in backend');
    return await teamApi.getById(teamId);
  },
};

// ==========================================
// GAME API
// ==========================================
export const gameApi = {
  getAll: async () => {
    const response = await wsClient.sendCommand('GET_GAMES');
    return (response.games || []).map(transformGame);
  },

  getById: async (id) => {
    const response = await wsClient.sendCommand('GET_GAMES');
    const game = response.games.find(g => g.id === id);
    return game ? transformGame(game) : null;
  },

  getPlayersForGame: async (gameId) => {
    const game = await gameApi.getById(gameId);
    if (!game) return { home: [], away: [] };

    // Get players from teams
    const response = await wsClient.sendCommand('GET_PLAYERS', {
      team_id: game.home.id
    });
    const homePlayers = (response.players || []).map(p => p.name);

    const awayResponse = await wsClient.sendCommand('GET_PLAYERS', {
      team_id: game.away.id
    });
    const awayPlayers = (awayResponse.players || []).map(p => p.name);

    return {
      home: homePlayers,
      away: awayPlayers
    };
  },

  create: async (homeId, awayId) => {
    const response = await wsClient.sendCommand('CREATE_GAME', {
      home_id: homeId,
      away_id: awayId
    });

    // Fetch the created game to get full details
    return await gameApi.getById(response.id);
  },

  start: async (id) => {
    await wsClient.sendCommand('START', { id });
    return await gameApi.getById(id);
  },

  pause: async (id) => {
    await wsClient.sendCommand('PAUSE', { id });
    return await gameApi.getById(id);
  },

  resume: async (id) => {
    await wsClient.sendCommand('RESUME', { id });
    return await gameApi.getById(id);
  },

  end: async (id) => {
    await wsClient.sendCommand('END', { id });
    return await gameApi.getById(id);
  },

  score: async (id, side, playerName, points = 1) => {
    await wsClient.sendCommand('SCORE', {
      id,
      points,
      side: side.toUpperCase(),
      player: playerName
    });
    return await gameApi.getById(id);
  },

  delete: async (id) => {
    await wsClient.sendCommand('DELETE', { id });
    return { success: true };
  },
};

// ==========================================
// CUP API
// ==========================================
export const cupApi = {
  getAll: async () => {
    const response = await wsClient.sendCommand('GET_CUPS');
    return response.cups || [];
  },

  getById: async (id) => {
    const response = await wsClient.sendCommand('GET_CUPS');
    return response.cups.find(c => c.id === id) || null;
  },

  getStandings: async (id) => {
    const response = await wsClient.sendCommand('GET_STANDINGS', { id });
    return response.standings;
  },

  getGameTree: async (id) => {
    const response = await wsClient.sendCommand('GET_GAMETREE', { id });
    return response.gametree;
  },

  create: async (name, type, teamIds) => {
    const response = await wsClient.sendCommand('CREATE_CUP', {
      cup_type: type,
      team_ids: teamIds
    });

    return {
      id: response.id,
      name,
      type,
      teams: teamIds,
      gameCount: 0
    };
  },

  delete: async (id) => {
    await wsClient.sendCommand('DELETE', { id });
    return { success: true };
  },
};

// ==========================================
// LIVE GAMES (Canlı maçlar)
// ==========================================
export const liveApi = {
  getRunningGames: async () => {
    const response = await wsClient.sendCommand('GET_GAMES');
    const games = (response.games || []).map(transformGame);
    return games.filter(g => g.state === 'RUNNING' || g.state === 'PAUSED');
  },
};

// ==========================================
// WATCH API (Observer Pattern)
// ==========================================
export const watchApi = {
  watch: async (gameId, callback) => {
    await wsClient.sendCommand('WATCH', { id: gameId });

    // Register callback for notifications
    if (callback) {
      const unsubscribe = wsClient.onNotification((notification) => {
        if (notification.game_id === gameId) {
          callback({
            gameId: notification.game_id,
            type: 'update',
            game: transformGame({
              id: notification.game_id,
              home: notification.home,
              away: notification.away,
              state: notification.state,
              score: notification.score
            })
          });
        }
      });

      // Store unsubscribe function for later cleanup
      if (!watchApi._unsubscribers) {
        watchApi._unsubscribers = new Map();
      }
      watchApi._unsubscribers.set(gameId, unsubscribe);
    }

    return { success: true, gameId };
  },

  unwatch: async (gameId) => {
    // Unregister callback
    if (watchApi._unsubscribers?.has(gameId)) {
      const unsubscribe = watchApi._unsubscribers.get(gameId);
      unsubscribe();
      watchApi._unsubscribers.delete(gameId);
    }

    return { success: true, gameId };
  },

  getWatchedGames: async () => {
    // Get from localStorage (frontend manages watched games)
    const watched = JSON.parse(localStorage.getItem('watchedGames') || '[]');
    return watched;
  },

  isWatching: async (gameId) => {
    const watched = await watchApi.getWatchedGames();
    return watched.includes(gameId);
  },
};

// ==========================================
// WebSocket Connection Management
// ==========================================
export const initializeWebSocket = async () => {
  try {
    await wsClient.connect();
    console.log('✅ WebSocket connected to backend');
    return true;
  } catch (error) {
    console.error('❌ WebSocket connection failed:', error);
    return false;
  }
};

export const disconnectWebSocket = () => {
  wsClient.disconnect();
};

export const isWebSocketConnected = () => {
  return wsClient.isConnected();
};

// Register global notification handler
export const onGameNotification = (handler) => {
  return wsClient.onNotification(handler);
};

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
  // Parse timeline to add minute information to scorers
  const timeline = backendGame.timeline || [];
  const scorersWithMinutes = { home: [], away: [] };

  // Process timeline to extract goal events with minutes
  if (timeline.length > 0) {
    const goalsByPlayer = { home: {}, away: {} };

    timeline.forEach(([timeStr, teamType, playerName, points]) => {
      if (points > 0) {
        const side = teamType.toLowerCase() === 'home' ? 'home' : 'away';

        if (!goalsByPlayer[side][playerName]) {
          goalsByPlayer[side][playerName] = { goals: 0, minutes: [] };
        }

        goalsByPlayer[side][playerName].goals += points;
        goalsByPlayer[side][playerName].minutes.push(timeStr);
      }
    });

    // Convert to scorers format
    ['home', 'away'].forEach(side => {
      Object.entries(goalsByPlayer[side]).forEach(([playerName, data]) => {
        scorersWithMinutes[side].push({
          name: playerName,
          goals: data.goals,
          minutes: data.minutes // Array of time strings like "12:34.56"
        });
      });
    });
  }

  // Fallback to backend scorers if timeline is empty
  const finalScorers = timeline.length > 0
    ? scorersWithMinutes
    : backendGame.scorers || { home: [], away: [] };

  return {
    id: backendGame.id,
    home: {
      id: backendGame.home_id,
      name: backendGame.home
    },
    away: {
      id: backendGame.away_id,
      name: backendGame.away
    },
    state: mapGameState(backendGame.state),
    score: {
      home: backendGame.score.home,
      away: backendGame.score.away
    },
    scorers: finalScorers,
    timeline: timeline,
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

    // Check if teams are placeholders (no valid ID or name starts with "Winner of")
    const homeIsPlaceholder = !game.home.id || game.home.name?.startsWith('Winner of');
    const awayIsPlaceholder = !game.away.id || game.away.name?.startsWith('Winner of');

    // Return empty arrays for placeholder teams
    if (homeIsPlaceholder && awayIsPlaceholder) {
      return { home: [], away: [] };
    }

    let homePlayers = [];
    let awayPlayers = [];

    // Get players from home team if it's real
    if (!homeIsPlaceholder) {
      try {
        const response = await wsClient.sendCommand('GET_PLAYERS', {
          team_id: game.home.id
        });
        homePlayers = (response.players || []).map(p => p.name);
      } catch (err) {
        console.warn('Failed to load home team players:', err);
      }
    }

    // Get players from away team if it's real
    if (!awayIsPlaceholder) {
      try {
        const awayResponse = await wsClient.sendCommand('GET_PLAYERS', {
          team_id: game.away.id
        });
        awayPlayers = (awayResponse.players || []).map(p => p.name);
      } catch (err) {
        console.warn('Failed to load away team players:', err);
      }
    }

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

  getCupGames: async (id) => {
    const response = await wsClient.sendCommand('GET_CUP_GAMES', { id });
    const gameIds = response.game_ids || [];

    // Fetch full game details for each game ID
    const allGames = await gameApi.getAll();
    return allGames.filter(game => gameIds.includes(game.id));
  },

  create: async (name, type, teamIds, numGroups = 4, playoffTeams = 8) => {
    const payload = {
      name: name,
      cup_type: type,
      team_ids: teamIds
    };

    // Only add GROUP-specific parameters if type is GROUP
    if (type === 'GROUP') {
      payload.num_groups = numGroups;
      payload.playoff_teams = playoffTeams;
    }

    const response = await wsClient.sendCommand('CREATE_CUP', payload);

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
  watch: async (gameId) => {
    await wsClient.sendCommand('WATCH', { id: gameId });
    return { success: true, gameId };
  },

  unwatch: async (gameId) => {
    await wsClient.sendCommand('UNWATCH', { id: gameId });
    return { success: true, gameId };
  },

  getWatchedGames: async () => {
    const response = await wsClient.sendCommand('GET_WATCHED_GAMES');
    return (response.games || []).map(transformGame);
  },

  isWatching: async (gameId) => {
    const watched = await watchApi.getWatchedGames();
    return watched.some(game => game.id === gameId);
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

// ==========================================
// ERROR HANDLING
// ==========================================
export const setGlobalErrorHandler = (handler) => {
  wsClient.setErrorHandler(handler);
};

export const removeGlobalErrorHandler = () => {
  wsClient.removeErrorHandler();
};

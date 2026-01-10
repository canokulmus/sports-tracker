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
// AUTH API
// ==========================================
export const authApi = {
  login: async (username) => {
    const response = await wsClient.sendCommand('LOGIN', { username });
    return {
      username: response.username,
      message: response.message,
      watched_ids: response.watched_ids
    };
  },
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

  update: async (id, updates) => {
    await wsClient.sendCommand('UPDATE_TEAM', {
      id,
      ...updates
    });
    return await teamApi.getById(id);
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
    await wsClient.sendCommand('DELETE_CUSTOM_FIELD', {
      team_id: teamId,
      key: key
    });
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

  update: async (id, updates) => {
    await wsClient.sendCommand('UPDATE_GAME', {
      id,
      ...updates
    });
    return await gameApi.getById(id);
  },

  getStats: async (id) => {
    const response = await wsClient.sendCommand('GET_GAME_STATS', { id });
    return response.stats;
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

  create: async (arg1, arg2, arg3, arg4, arg5) => {
    let name, type, teamIds, numGroups, playoffTeams;

    if (typeof arg1 === 'object' && arg1 !== null && !Array.isArray(arg1)) {
      // Object style
      ({ name, type, teamIds, numGroups, playoffTeams } = arg1);
      // Handle property aliases
      type = type || arg1.cup_type || arg1.cupType;
      teamIds = teamIds || arg1.team_ids || arg1.teams;
      numGroups = numGroups || arg1.num_groups;
      playoffTeams = playoffTeams || arg1.playoff_teams;
    } else {
      // Positional style: create(name, type, teamIds, numGroups, playoffTeams)
      name = arg1;
      type = arg2;
      teamIds = arg3;
      numGroups = arg4;
      playoffTeams = arg5;
    }

    const response = await wsClient.sendCommand('CREATE_CUP', {
      name,
      cup_type: type,
      team_ids: teamIds,
      num_groups: numGroups,
      playoff_teams: playoffTeams
    });
    return response;
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
    return (response.games || []).map(transformGame);
  },

  delete: async (id) => {
    await wsClient.sendCommand('DELETE', { id });
    return { success: true };
  },

  generatePlayoffs: async (id) => {
    const response = await wsClient.sendCommand('GENERATE_PLAYOFFS', { id });
    return response;
  },
};

export const systemApi = {
  save: async () => {
    await wsClient.sendCommand('SAVE');
  },

  search: async (query) => {
    const response = await wsClient.sendCommand('SEARCH', { query });
    return response.results || [];
  },

  list: async () => {
    const response = await wsClient.sendCommand('LIST');
    return response.items || [];
  },

  listAttached: async () => {
    const response = await wsClient.sendCommand('LIST_ATTACHED');
    return response.items || [];
  },

  attach: async (id) => {
    await wsClient.sendCommand('ATTACH', { id });
  },

  detach: async (id) => {
    await wsClient.sendCommand('DETACH', { id });
  }
};

export const watchApi = {
  getWatchedGames: async () => {
    const response = await wsClient.sendCommand('GET_WATCHED_GAMES');
    return (response.games || []).map(transformGame);
  },

  getWatchedCups: async () => {
    const response = await wsClient.sendCommand('GET_WATCHED_CUPS');
    return response.cups || [];
  },

  watch: async (id) => {
    await wsClient.sendCommand('WATCH', { id });
  },

  unwatch: async (id) => {
    await wsClient.sendCommand('UNWATCH', { id });
  },

  watchCup: async (cupId) => {
    const response = await wsClient.sendCommand('WATCH', { id: cupId });
    return response;
  },

  unwatchCup: async (cupId) => {
    await wsClient.sendCommand('UNWATCH', { id: cupId });
  }
};

export const onGameNotification = (callback) => {
  return wsClient.onNotification(callback);
};

export const initializeWebSocket = async () => {
  return await wsClient.connect();
};

export const isWebSocketConnected = () => {
  return wsClient.isConnected();
};

export const setGlobalErrorHandler = (handler) => {
  wsClient.setErrorHandler(handler);
};

export const removeGlobalErrorHandler = () => {
  wsClient.setErrorHandler(null);
};
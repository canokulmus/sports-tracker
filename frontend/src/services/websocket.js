// WebSocket Client Service for Sports Tracker
// Connects to backend WebSocket server and manages real-time communication

class WebSocketClient {
  constructor() {
    this.ws = null;
    this.url = 'ws://localhost:8888';
    this.connected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 2000;

    // Message handlers
    this.messageHandlers = new Map();
    this.notificationHandlers = [];
    this.requestCallbacks = new Map();
    this.requestId = 0;

    // Global error handler
    this.errorHandler = null;
  }

  connect() {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected to server');
          this.connected = true;
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
          } catch (error) {
            console.error('[WebSocket] Failed to parse message:', error);
          }
        };

        this.ws.onerror = (error) => {
          console.error('[WebSocket] Error:', error);
          reject(error);
        };

        this.ws.onclose = () => {
          console.log('[WebSocket] Connection closed');
          this.connected = false;
          this.attemptReconnect();
        };
      } catch (error) {
        console.error('[WebSocket] Connection failed:', error);
        reject(error);
      }
    });
  }

  handleMessage(data) {
    // Handle notifications (real-time updates)
    if (data.type === 'NOTIFICATION') {
      this.notificationHandlers.forEach(handler => {
        try {
          handler(data);
        } catch (error) {
          console.error('[WebSocket] Notification handler error:', error);
        }
      });
      return;
    }

    // Handle INFO messages (welcome, etc.)
    if (data.type === 'INFO') {
      console.log('[WebSocket]', data.message);
      return;
    }

    // Handle command responses
    // Backend doesn't echo requestId, so we resolve the oldest pending request
    if (data.status) {
      if (this.requestCallbacks.size > 0) {
        const firstKey = this.requestCallbacks.keys().next().value;
        const { resolve, reject } = this.requestCallbacks.get(firstKey);
        this.requestCallbacks.delete(firstKey);

        if (data.status === 'OK') {
          resolve(data);
        } else if (data.status === 'ERROR') {
          const error = new Error(data.message || 'Unknown error');
          // Call global error handler if registered
          if (this.errorHandler) {
            this.errorHandler(error, data);
          }
          reject(error);
        }
      }
    }
  }

  sendCommand(command, params = {}) {
    return new Promise((resolve, reject) => {
      if (!this.connected) {
        const error = new Error('WebSocket not connected');
        if (this.errorHandler) {
          this.errorHandler(error, { command, params });
        }
        reject(error);
        return;
      }

      const requestId = ++this.requestId;
      const message = {
        ...params,
        command,
        requestId
      };

      // Store callback for response
      this.requestCallbacks.set(requestId, { resolve, reject });

      // Set timeout for request
      setTimeout(() => {
        if (this.requestCallbacks.has(requestId)) {
          this.requestCallbacks.delete(requestId);
          const error = new Error('Request timeout');
          if (this.errorHandler) {
            this.errorHandler(error, { command, params });
          }
          reject(error);
        }
      }, 10000);

      this.ws.send(JSON.stringify(message));
    });
  }

  onNotification(handler) {
    this.notificationHandlers.push(handler);
    return () => {
      const index = this.notificationHandlers.indexOf(handler);
      if (index > -1) {
        this.notificationHandlers.splice(index, 1);
      }
    };
  }

  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WebSocket] Max reconnection attempts reached');
      return;
    }

    this.reconnectAttempts++;
    console.log(`[WebSocket] Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    setTimeout(() => {
      this.connect().catch(error => {
        console.error('[WebSocket] Reconnection failed:', error);
      });
    }, this.reconnectDelay);
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.connected = false;
    }
  }

  isConnected() {
    return this.connected;
  }

  // Set global error handler
  setErrorHandler(handler) {
    this.errorHandler = handler;
  }

  // Remove error handler
  removeErrorHandler() {
    this.errorHandler = null;
  }
}

// Singleton instance
const wsClient = new WebSocketClient();

export default wsClient;

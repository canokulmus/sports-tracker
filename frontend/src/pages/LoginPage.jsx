import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Trophy, User, ArrowRight } from 'lucide-react';
import { useUser } from '../context/UserContext';
import { authApi } from '../services/api';
import colors from '../styles/colors';

export default function LoginPage() {
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const [isFocused, setIsFocused] = useState(false);
  const { login } = useUser();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!username.trim()) {
      setError('Please enter a username');
      return;
    }

    setIsLoading(true);
    setError('');

    try {
      await authApi.login(username.trim());
      login(username.trim());
      navigate('/');
    } catch (err) {
      setError(err.message || 'Login failed. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        background: colors.gradients.dark,
        padding: '20px',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <div
        style={{
          position: 'absolute',
          top: '10%',
          left: '10%',
          width: '300px',
          height: '300px',
          background: colors.gradients.neonPurple,
          borderRadius: '50%',
          opacity: '0.1',
          filter: 'blur(100px)',
          animation: 'float 8s ease-in-out infinite',
        }}
      />
      <div
        style={{
          position: 'absolute',
          bottom: '10%',
          right: '10%',
          width: '400px',
          height: '400px',
          background: colors.gradients.neonGreen,
          borderRadius: '50%',
          opacity: '0.1',
          filter: 'blur(100px)',
          animation: 'float 10s ease-in-out infinite reverse',
        }}
      />

      <div
        style={{
          width: '100%',
          maxWidth: '440px',
          position: 'relative',
          zIndex: 1,
        }}
      >
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            marginBottom: '40px',
            textAlign: 'center',
          }}
        >
          <div
            style={{
              width: '80px',
              height: '80px',
              background: colors.gradients.neon,
              borderRadius: '20px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '24px',
              boxShadow: `0 8px 32px ${colors.brand.primary}40`,
              animation: 'glow 2s ease-in-out infinite',
            }}
          >
            <Trophy size={40} color="#fff" strokeWidth={2.5} />
          </div>

          <h1
            style={{
              fontSize: '32px',
              fontWeight: '700',
              color: colors.text.primary,
              margin: '0 0 12px 0',
              letterSpacing: '-0.5px',
            }}
          >
            Sports Tracker
          </h1>

          <p
            style={{
              fontSize: '15px',
              color: colors.text.secondary,
              margin: 0,
              lineHeight: '1.6',
            }}
          >
            Track your games, manage tournaments,
            <br />
            and watch live scores in real-time
          </p>
        </div>

        <div
          style={{
            backgroundColor: colors.background.secondary,
            borderRadius: '16px',
            padding: '32px',
            border: `1px solid ${colors.ui.border}`,
            boxShadow: `0 20px 60px rgba(0, 0, 0, 0.5)`,
          }}
        >
          <form onSubmit={handleSubmit}>
            <div style={{ marginBottom: '24px' }}>
              <label
                htmlFor="username"
                style={{
                  display: 'block',
                  fontSize: '13px',
                  fontWeight: '600',
                  color: colors.text.secondary,
                  marginBottom: '10px',
                  textTransform: 'uppercase',
                  letterSpacing: '0.5px',
                }}
              >
                Username
              </label>

              <div
                style={{
                  position: 'relative',
                  display: 'flex',
                  alignItems: 'center',
                }}
              >
                <div
                  style={{
                    position: 'absolute',
                    left: '14px',
                    display: 'flex',
                    alignItems: 'center',
                    pointerEvents: 'none',
                  }}
                >
                  <User
                    size={18}
                    color={isFocused ? colors.brand.primary : colors.text.secondary}
                    style={{ transition: 'color 0.2s' }}
                  />
                </div>

                <input
                  id="username"
                  type="text"
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  onFocus={() => setIsFocused(true)}
                  onBlur={() => setIsFocused(false)}
                  placeholder="Enter your username"
                  disabled={isLoading}
                  autoFocus
                  style={{
                    width: '100%',
                    padding: '14px 14px 14px 44px',
                    fontSize: '15px',
                    backgroundColor: colors.background.tertiary,
                    color: colors.text.primary,
                    border: `2px solid ${isFocused ? colors.brand.primary : colors.ui.border}`,
                    borderRadius: '10px',
                    outline: 'none',
                    transition: 'all 0.2s ease',
                    boxShadow: isFocused ? `0 0 0 4px ${colors.brand.primary}15` : 'none',
                  }}
                />
              </div>
            </div>

            {error && (
              <div
                style={{
                  padding: '14px',
                  backgroundColor: `${colors.state.danger}10`,
                  border: `1px solid ${colors.state.danger}40`,
                  borderRadius: '10px',
                  marginBottom: '24px',
                  display: 'flex',
                  alignItems: 'start',
                  gap: '10px',
                }}
              >
                <div
                  style={{
                    width: '4px',
                    height: '100%',
                    backgroundColor: colors.state.danger,
                    borderRadius: '2px',
                    flexShrink: 0,
                  }}
                />
                <p
                  style={{
                    fontSize: '14px',
                    color: colors.state.danger,
                    margin: 0,
                    lineHeight: '1.5',
                  }}
                >
                  {error}
                </p>
              </div>
            )}

            <button
              type="submit"
              disabled={isLoading}
              className="login-button"
              style={{
                width: '100%',
                padding: '14px 24px',
                fontSize: '15px',
                fontWeight: '600',
                color: '#fff',
                background: isLoading ? colors.text.secondary : colors.gradients.neon,
                border: 'none',
                borderRadius: '10px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                transition: 'all 0.3s ease',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '10px',
                boxShadow: isLoading ? 'none' : `0 4px 20px ${colors.brand.primary}40`,
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <span style={{ position: 'relative', zIndex: 1 }}>
                {isLoading ? 'Signing in...' : 'Sign in'}
              </span>
              {!isLoading && (
                <ArrowRight
                  size={18}
                  style={{
                    position: 'relative',
                    zIndex: 1,
                    transition: 'transform 0.3s ease',
                  }}
                />
              )}
            </button>
          </form>
        </div>

        <p
          style={{
            textAlign: 'center',
            marginTop: '24px',
            fontSize: '13px',
            color: colors.text.muted,
          }}
        >
          Copyright © 2026 Sports Tracker. All rights reserved.
        </p>
        <p
          style={{
            textAlign: 'center',
            marginTop: '24px',
            fontSize: '13px',
            color: colors.text.muted,
          }}
        >
          Created by Can & Alp, for CENG445 Term Project
        </p>
      </div>

      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0) scale(1); }
          50% { transform: translateY(-20px) scale(1.1); }
        }

        @keyframes glow {
          0%, 100% {
            box-shadow: 0 8px 32px ${colors.brand.primary}40;
          }
          50% {
            box-shadow: 0 8px 48px ${colors.brand.primary}60;
          }
        }

        .login-button:hover:not(:disabled) {
          transform: translateY(-2px);
          box-shadow: 0 8px 30px ${colors.brand.primary}60 !important;
        }

        .login-button:hover:not(:disabled) svg {
          transform: translateX(4px);
        }

        .login-button:active:not(:disabled) {
          transform: translateY(0);
        }
      `}</style>
    </div>
  );
}

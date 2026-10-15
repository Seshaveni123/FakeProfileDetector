import React from 'react'

export class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props)
    this.state = { hasError: false, error: null }
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error }
  }

  componentDidCatch(error, errorInfo) {
    console.error('FakeGuard ErrorBoundary caught an error:', error, errorInfo)
  }

  handleReload = () => {
    this.setState({ hasError: false, error: null })
    window.location.reload()
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null })
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="app-wrapper" style={{ minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '24px' }}>
          <div className="glass-card" style={{ maxWidth: '640px', width: '100%', padding: '36px', textAlign: 'center', boxShadow: '0 20px 40px rgba(0,0,0,0.4)' }}>
            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🛡️</div>
            <h2 style={{ fontSize: '24px', fontWeight: 800, marginBottom: '8px', color: '#f8fafc' }}>
              FakeGuard AI Interface Notice
            </h2>
            <p style={{ color: 'var(--text-muted, #94a3b8)', marginBottom: '20px', lineHeight: 1.6, fontSize: '15px' }}>
              The application encountered an unexpected display issue while rendering. The underlying detection models and database services are unaffected.
            </p>
            <div style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid rgba(239, 68, 68, 0.3)', padding: '14px 18px', borderRadius: '8px', fontFamily: 'var(--font-mono, monospace)', fontSize: '13px', color: '#fca5a5', textAlign: 'left', marginBottom: '24px', overflowX: 'auto', whiteSpace: 'pre-wrap' }}>
              {this.state.error?.message || 'Unknown render error'}
            </div>
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center' }}>
              <button className="btn btn-primary" onClick={this.handleReload}>
                Reload Application
              </button>
              <button className="btn" style={{ background: 'rgba(255,255,255,0.08)', color: '#fff' }} onClick={this.handleReset}>
                Try Again
              </button>
            </div>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

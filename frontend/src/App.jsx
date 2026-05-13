import { useState, useEffect, useCallback, useRef } from 'react'

const API_BASE = 'http://localhost:8000'

// ===== HELPER COMPONENTS =====

function ConfidenceGauge({ value, color }) {
  const circumference = 2 * Math.PI * 42
  const offset = circumference - (value / 100) * circumference

  return (
    <div className="gauge-container">
      <div className="gauge-ring">
        <svg width="100" height="100" viewBox="0 0 100 100">
          <circle className="gauge-bg" cx="50" cy="50" r="42" />
          <circle
            className="gauge-fill"
            cx="50" cy="50" r="42"
            stroke={color}
            strokeDasharray={circumference}
            strokeDashoffset={offset}
          />
        </svg>
        <div className="gauge-percentage" style={{ color }}>
          {value}%
        </div>
      </div>
      <div className="metric-label">Confidence</div>
    </div>
  )
}

function Toast({ message, type, onClose }) {
  useEffect(() => {
    const timer = setTimeout(onClose, 4000)
    return () => clearTimeout(timer)
  }, [onClose])

  return (
    <div className={`toast toast-${type}`}>
      <span className="toast-mark">{type === 'success' ? 'OK' : '!'}</span>
      <span>{message}</span>
    </div>
  )
}

function cleanDisplayText(text) {
  return String(text || '').replace(/^[^\p{L}\p{N}]+/u, '').trim()
}

// ===== PLATFORM ICONS =====
function InstagramIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="2" y="2" width="20" height="20" rx="5" ry="5"/>
      <path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/>
      <line x1="17.5" y1="6.5" x2="17.51" y2="6.5"/>
    </svg>
  )
}

function TwitterIcon() {
  return (
    <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor">
      <path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/>
    </svg>
  )
}

function ShieldIcon() {
  return (
    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 3 5 6v5c0 4.5 2.8 8.5 7 10 4.2-1.5 7-5.5 7-10V6l-7-3Z" />
      <path d="M12 7v10" />
    </svg>
  )
}

function ModernVisualPanel({ platform }) {
  const platformName = platform === 'instagram' ? 'Instagram' : 'Twitter / X'

  return (
    <div className="modern-visual" aria-hidden="true">
      <div className="visual-copy">
        <span className="visual-kicker">Realtime profile intelligence</span>
        <h2>Clean signals. Clear decisions.</h2>
        <p>{platformName} account patterns are mapped into a compact risk view before you analyze.</p>
      </div>
      <div className="visual-device">
        <div className="visual-browser">
          <div className="visual-dots"><span /><span /><span /></div>
          <div className="visual-line wide" />
          <div className="visual-line" />
          <div className="visual-grid">
            <span /><span /><span /><span />
          </div>
          <div className="visual-chart">
            <span className="bar b1" />
            <span className="bar b2" />
            <span className="bar b3" />
            <span className="bar b4" />
          </div>
        </div>
      </div>
    </div>
  )
}

// ===== MAIN APP =====
export default function App() {
  const [activeTab, setActiveTab] = useState('home')
  const [platform, setPlatform] = useState('instagram')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [toasts, setToasts] = useState([])
  const [dashboard, setDashboard] = useState(null)
  const [history, setHistory] = useState(null)
  const [modelInfo, setModelInfo] = useState(null)
  const [bulkResults, setBulkResults] = useState(null)
  const fileInputRef = useRef(null)

  // Instagram form state
  const [instaForm, setInstaForm] = useState({
    username: '', followers_count: '', following_count: '',
    posts_count: '', account_age_days: '', bio_length: '',
    has_profile_pic: 1, is_private: 0, is_verified: 0,
    has_url_in_bio: 0, avg_likes: '', avg_comments: '',
  })

  // Twitter form state
  const [twitterForm, setTwitterForm] = useState({
    username: '', followers_count: '', following_count: '',
    tweets_count: '', account_age_days: '', bio_length: '',
    has_profile_pic: 1, is_verified: 0, has_url_in_bio: 0,
    listed_count: '', avg_retweets: '', mention_count: '', avg_favorites: '',
    reply_ratio: 0.2,
  })

  const addToast = useCallback((message, type = 'success') => {
    const id = Date.now()
    setToasts(prev => [...prev, { id, message, type }])
  }, [])

  const removeToast = useCallback((id) => {
    setToasts(prev => prev.filter(t => t.id !== id))
  }, [])

  const updateInstaForm = (field, value) => {
    setInstaForm(prev => ({ ...prev, [field]: value }))
  }

  const updateTwitterForm = (field, value) => {
    setTwitterForm(prev => ({ ...prev, [field]: value }))
  }

  // Load data when switching tabs
  useEffect(() => {
    if (activeTab === 'dashboard') fetchDashboard()
    if (activeTab === 'history') fetchHistory()
    if (activeTab === 'model') fetchModelInfo()
  }, [activeTab])

  // Reset result when switching platform
  useEffect(() => {
    setResult(null)
  }, [platform])

  const fetchDashboard = async () => {
    try {
      const res = await fetch(`${API_BASE}/dashboard`)
      const data = await res.json()
      setDashboard(data)
    } catch (err) {
      addToast('Failed to load dashboard', 'error')
    }
  }

  const fetchHistory = async () => {
    try {
      const res = await fetch(`${API_BASE}/history?limit=50`)
      const data = await res.json()
      setHistory(data)
    } catch (err) {
      addToast('Failed to load history', 'error')
    }
  }

  const fetchModelInfo = async () => {
    try {
      const res = await fetch(`${API_BASE}/model-info`)
      const data = await res.json()
      setModelInfo(data)
    } catch (err) {
      addToast('Failed to load model info', 'error')
    }
  }

  // ===== PREDICT =====
  const handlePredict = async (e) => {
    e.preventDefault()
    setLoading(true)
    setResult(null)

    try {
      let payload = { platform }

      if (platform === 'instagram') {
        payload = {
          ...payload,
          username: instaForm.username,
          followers_count: parseFloat(instaForm.followers_count) || 0,
          following_count: parseFloat(instaForm.following_count) || 0,
          posts_count: parseFloat(instaForm.posts_count) || 0,
          account_age_days: parseFloat(instaForm.account_age_days) || 0,
          bio_length: parseFloat(instaForm.bio_length) || 0,
          has_profile_pic: instaForm.has_profile_pic,
          is_private: instaForm.is_private,
          is_verified: instaForm.is_verified,
          has_url_in_bio: instaForm.has_url_in_bio,
          avg_likes: parseFloat(instaForm.avg_likes) || 0,
          avg_comments: parseFloat(instaForm.avg_comments) || 0,
        }
      } else {
        payload = {
          ...payload,
          username: twitterForm.username,
          follower_count_twitter: parseFloat(twitterForm.followers_count) || 0,
          retweet_count: parseFloat(twitterForm.avg_retweets) || 0,
          mention_count: parseFloat(twitterForm.mention_count) || 0,
          verified: twitterForm.is_verified ? 1 : 0,
          followers_count: parseFloat(twitterForm.followers_count) || 0,
          following_count: parseFloat(twitterForm.following_count) || 0,
          tweets_count: parseFloat(twitterForm.tweets_count) || 0,
          account_age_days: parseFloat(twitterForm.account_age_days) || 0,
          bio_length: parseFloat(twitterForm.bio_length) || 0,
          has_profile_pic: twitterForm.has_profile_pic,
          is_verified: twitterForm.is_verified,
          has_url_in_bio: twitterForm.has_url_in_bio,
          listed_count: parseFloat(twitterForm.listed_count) || 0,
          avg_retweets: parseFloat(twitterForm.avg_retweets) || 0,
          avg_favorites: parseFloat(twitterForm.avg_favorites) || 0,
          reply_ratio: parseFloat(twitterForm.reply_ratio),
        }
      }

      const res = await fetch(`${API_BASE}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })

      if (!res.ok) {
        const errData = await res.json()
        throw new Error(errData.detail || 'Prediction failed')
      }

      const data = await res.json()
      setResult(data)
      addToast(
        data.is_fake ? 'Fake profile detected' : 'Profile appears genuine',
        data.is_fake ? 'error' : 'success'
      )
    } catch (err) {
      addToast(err.message || 'Prediction failed. Is the backend running?', 'error')
    } finally {
      setLoading(false)
    }
  }

  // ===== BULK UPLOAD =====
  const handleBulkUpload = async (e) => {
    const file = e.target.files[0]
    if (!file) return

    setLoading(true)
    setBulkResults(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${API_BASE}/predict/bulk?platform=${platform}`, {
        method: 'POST',
        body: formData,
      })

      const data = await res.json()
      setBulkResults(data)
      addToast(`Processed ${data.total_profiles} ${platform} profiles!`)
    } catch (err) {
      addToast('Bulk upload failed.', 'error')
    } finally {
      setLoading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  // ===== FILL DEMO =====
  // Demo data pools — rotates on each click
  const demoIndexRef = useRef({ instaReal: 0, instaFake: 0, twitterReal: 0, twitterFake: 0 })

  const instaDemos = {
    real: [
      { username: 'sarah_travels', followers_count: '4520', following_count: '380', posts_count: '342', account_age_days: '1825', bio_length: '95', has_profile_pic: 1, is_private: 0, is_verified: 0, has_url_in_bio: 1, avg_likes: '185', avg_comments: '12' },
      { username: 'chef_priya', followers_count: '12800', following_count: '620', posts_count: '890', account_age_days: '2400', bio_length: '140', has_profile_pic: 1, is_private: 0, is_verified: 0, has_url_in_bio: 1, avg_likes: '430', avg_comments: '28' },
      { username: 'alex.photography', followers_count: '8400', following_count: '510', posts_count: '620', account_age_days: '1460', bio_length: '110', has_profile_pic: 1, is_private: 0, is_verified: 1, has_url_in_bio: 1, avg_likes: '320', avg_comments: '18' },
      { username: 'fitness_anna', followers_count: '22300', following_count: '290', posts_count: '1100', account_age_days: '3200', bio_length: '150', has_profile_pic: 1, is_private: 0, is_verified: 1, has_url_in_bio: 1, avg_likes: '890', avg_comments: '55' },
      { username: 'markdev_io', followers_count: '3100', following_count: '440', posts_count: '210', account_age_days: '1095', bio_length: '80', has_profile_pic: 1, is_private: 0, is_verified: 0, has_url_in_bio: 1, avg_likes: '95', avg_comments: '8' },
    ],
    fake: [
      { username: 'follow4follow_bot', followers_count: '15', following_count: '6200', posts_count: '2', account_age_days: '8', bio_length: '0', has_profile_pic: 0, is_private: 0, is_verified: 0, has_url_in_bio: 1, avg_likes: '0', avg_comments: '0' },
      { username: 'free_iphone_2024', followers_count: '42', following_count: '7500', posts_count: '0', account_age_days: '3', bio_length: '12', has_profile_pic: 0, is_private: 0, is_verified: 0, has_url_in_bio: 1, avg_likes: '0', avg_comments: '0' },
      { username: 'xyz123_gains', followers_count: '8', following_count: '4800', posts_count: '1', account_age_days: '12', bio_length: '5', has_profile_pic: 0, is_private: 0, is_verified: 0, has_url_in_bio: 1, avg_likes: '1', avg_comments: '0' },
      { username: 'clickhere_money', followers_count: '28', following_count: '5100', posts_count: '3', account_age_days: '6', bio_length: '0', has_profile_pic: 1, is_private: 0, is_verified: 0, has_url_in_bio: 1, avg_likes: '0', avg_comments: '0' },
      { username: 'legit_giveaway99', followers_count: '5', following_count: '9800', posts_count: '0', account_age_days: '2', bio_length: '8', has_profile_pic: 0, is_private: 0, is_verified: 0, has_url_in_bio: 1, avg_likes: '0', avg_comments: '0' },
    ]
  }

  const twitterDemos = {
    real: [
      { username: 'techwriter_mike', followers_count: '15000', following_count: '450', tweets_count: '8500', account_age_days: '2920', bio_length: '110', has_profile_pic: 1, is_verified: 1, has_url_in_bio: 1, listed_count: '45', avg_retweets: '8', mention_count: '1', avg_favorites: '25', reply_ratio: 0.25 },
      { username: 'datascience_guru', followers_count: '42000', following_count: '820', tweets_count: '12000', account_age_days: '3650', bio_length: '155', has_profile_pic: 1, is_verified: 1, has_url_in_bio: 1, listed_count: '120', avg_retweets: '35', mention_count: '3', avg_favorites: '90', reply_ratio: 0.18 },
      { username: 'uxdesigner_sam', followers_count: '5600', following_count: '340', tweets_count: '4200', account_age_days: '1825', bio_length: '95', has_profile_pic: 1, is_verified: 0, has_url_in_bio: 1, listed_count: '22', avg_retweets: '5', mention_count: '2', avg_favorites: '18', reply_ratio: 0.30 },
      { username: 'openai_fan', followers_count: '9800', following_count: '560', tweets_count: '6100', account_age_days: '2555', bio_length: '120', has_profile_pic: 1, is_verified: 0, has_url_in_bio: 1, listed_count: '38', avg_retweets: '12', mention_count: '1', avg_favorites: '42', reply_ratio: 0.22 },
      { username: 'react_dev_lina', followers_count: '18500', following_count: '410', tweets_count: '9200', account_age_days: '3100', bio_length: '130', has_profile_pic: 1, is_verified: 1, has_url_in_bio: 1, listed_count: '65', avg_retweets: '20', mention_count: '2', avg_favorites: '55', reply_ratio: 0.15 },
    ],
    fake: [
      { username: 'xbot_spam_2024', followers_count: '12', following_count: '4800', tweets_count: '3', account_age_days: '5', bio_length: '0', has_profile_pic: 0, is_verified: 0, has_url_in_bio: 1, listed_count: '0', avg_retweets: '90', mention_count: '5', avg_favorites: '0', reply_ratio: 0.85 },
      { username: 'crypto_pump_x', followers_count: '35', following_count: '6200', tweets_count: '8', account_age_days: '4', bio_length: '10', has_profile_pic: 0, is_verified: 0, has_url_in_bio: 1, listed_count: '0', avg_retweets: '150', mention_count: '8', avg_favorites: '0', reply_ratio: 0.92 },
      { username: 'win_big_now', followers_count: '6', following_count: '5500', tweets_count: '1', account_age_days: '2', bio_length: '0', has_profile_pic: 0, is_verified: 0, has_url_in_bio: 1, listed_count: '0', avg_retweets: '0', mention_count: '12', avg_favorites: '0', reply_ratio: 0.95 },
      { username: 'retweet_king88', followers_count: '20', following_count: '7100', tweets_count: '5', account_age_days: '7', bio_length: '4', has_profile_pic: 1, is_verified: 0, has_url_in_bio: 1, listed_count: '0', avg_retweets: '200', mention_count: '6', avg_favorites: '1', reply_ratio: 0.88 },
      { username: 'elon_giveaway_x', followers_count: '2', following_count: '8900', tweets_count: '0', account_age_days: '1', bio_length: '0', has_profile_pic: 0, is_verified: 0, has_url_in_bio: 1, listed_count: '0', avg_retweets: '0', mention_count: '15', avg_favorites: '0', reply_ratio: 0.99 },
    ]
  }

  const fillDemo = (type) => {
    if (platform === 'instagram') {
      const key = type === 'real' ? 'instaReal' : 'instaFake'
      const pool = instaDemos[type]
      const idx = demoIndexRef.current[key] % pool.length
      setInstaForm({ ...pool[idx] })
      demoIndexRef.current[key] = idx + 1
    } else {
      const key = type === 'real' ? 'twitterReal' : 'twitterFake'
      const pool = twitterDemos[type]
      const idx = demoIndexRef.current[key] % pool.length
      setTwitterForm({ ...pool[idx] })
      demoIndexRef.current[key] = idx + 1
    }
    setResult(null)
    addToast(`Loaded ${type} ${platform} demo data`)
  }

  // ===== RENDER TABS =====
  const tabs = [
    { id: 'home', label: 'Home', icon: '' },
    { id: 'detect', label: 'Detect', icon: '' },
    { id: 'bulk', label: 'Bulk Check', icon: '' },
    { id: 'dashboard', label: 'Dashboard', icon: '' },
    { id: 'history', label: 'History', icon: '' },
    { id: 'model', label: 'Model Info', icon: '' },
  ]

  return (
    <div className="app-wrapper">
      {/* Global animated contour background — visible on ALL pages */}
      <div className="bg-grid" />
      <svg className="global-bg-svg" viewBox="0 0 1440 900" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <path d="M-100 200C200 50 420 180 580 320s350 240 560 60 380-180 900-80" />
        <path d="M-100 240C210 90 430 210 596 348s342 212 552 46 380-166 900-66" />
        <path d="M-100 280C220 130 440 240 612 376s334 184 544 32 380-152 900-52" />
        <path d="M-100 320C230 170 450 270 628 404s326 156 536 18 380-138 900-38" />
        <path d="M-100 360C240 210 460 300 644 432s318 128 528  4 380-124 900-24" />
        <path d="M-100 400C250 250 470 330 660 460s310 100 520 -10 380-110 900-10" />
        <path d="M-100 440C260 290 480 360 676 488s302  72 512 -24 380-96  900  4" />
        <path d="M-100 480C270 330 490 390 692 516s294  44 504 -38 380-82  900 18" />
        <ellipse cx="220" cy="560" rx="200" ry="140" />
        <ellipse cx="220" cy="560" rx="148" ry="100" />
        <ellipse cx="220" cy="560" rx="96"  ry="62" />
        <ellipse cx="1180" cy="280" rx="260" ry="140" />
        <ellipse cx="1180" cy="280" rx="200" ry="104" />
        <ellipse cx="1180" cy="280" rx="140" ry="68" />
        <ellipse cx="740"  cy="620" rx="170" ry="100" />
        <ellipse cx="740"  cy="620" rx="118" ry="66" />
      </svg>

      <div className="main-content">
        {/* Header */}
        <header className={`header ${activeTab === 'home' ? 'header-home' : ''}`} id="app-header">
          <div className="logo">
            <div className="logo-icon"><ShieldIcon /></div>
            <div className="logo-text">
              <h1>FakeGuard AI</h1>
              <p>Platform-Aware Profile Detection</p>
            </div>
          </div>
          <nav className="nav-tabs" id="main-nav">
            {tabs.map(tab => (
              <button
                key={tab.id}
                id={`tab-${tab.id}`}
                className={`nav-tab ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                <span className="tab-icon">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </nav>
        </header>

        {/* Content */}
        <main>
          {activeTab === 'home' && (
            <HomeTab
              setActiveTab={setActiveTab}
              platform={platform}
              setPlatform={setPlatform}
            />
          )}
          {activeTab === 'detect' && (
            <DetectTab
              platform={platform} setPlatform={setPlatform}
              instaForm={instaForm} updateInstaForm={updateInstaForm}
              twitterForm={twitterForm} updateTwitterForm={updateTwitterForm}
              handlePredict={handlePredict} loading={loading}
              result={result} fillDemo={fillDemo}
            />
          )}
          {activeTab === 'bulk' && (
            <BulkTab
              platform={platform} setPlatform={setPlatform}
              handleBulkUpload={handleBulkUpload} loading={loading}
              bulkResults={bulkResults} fileInputRef={fileInputRef}
            />
          )}
          {activeTab === 'dashboard' && <DashboardTab dashboard={dashboard} />}
          {activeTab === 'history' && <HistoryTab history={history} />}
          {activeTab === 'model' && <ModelTab modelInfo={modelInfo} />}
        </main>

        <footer className="footer">
          <p>FakeGuard AI — Platform-Aware Fake Profile Detection with DevOps & Cloud</p>
        </footer>
      </div>

      {/* Toasts */}
      <div className="toast-container">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            message={toast.message}
            type={toast.type}
            onClose={() => removeToast(toast.id)}
          />
        ))}
      </div>
    </div>
  )
}

// ===== PLATFORM SELECTOR =====
function PlatformSelector({ platform, setPlatform }) {
  return (
    <div className="platform-selector">
      <button
        id="select-instagram"
        className={`platform-btn ${platform === 'instagram' ? 'active instagram' : ''}`}
        onClick={() => setPlatform('instagram')}
      >
        <InstagramIcon />
        <span>Instagram</span>
      </button>
      <button
        id="select-twitter"
        className={`platform-btn ${platform === 'twitter' ? 'active twitter' : ''}`}
        onClick={() => setPlatform('twitter')}
      >
        <TwitterIcon />
        <span>Twitter / X</span>
      </button>
    </div>
  )
}

// ===== HOME TAB =====
function HomeTab({ setActiveTab, platform, setPlatform }) {
  const startDetect = (p = platform) => { setPlatform(p); setActiveTab('detect') }

  const features = [
    { tag: 'AI ENGINE', title: 'ML-Powered Detection', desc: 'Random Forest + XGBoost models trained on 10K+ real profiles with 95%+ accuracy.' },
    { tag: 'REAL-TIME', title: 'Instant Risk Scoring', desc: 'Sub-second predictions with explainable AI — know exactly why a profile was flagged.' },
    { tag: 'DUAL PLATFORM', title: 'Instagram & Twitter/X', desc: 'Platform-specific signal analysis tuned separately for each social network.' },
    { tag: 'BULK SCAN', title: 'Batch Processing', desc: 'Upload CSV files to scan hundreds of profiles simultaneously with full result export.' },
    { tag: 'ANALYTICS', title: 'Live Dashboard', desc: 'Track scan history, fake-rate trends, and feature importance across both platforms.' },
    { tag: 'OPEN SOURCE', title: 'DevOps Native', desc: 'Dockerized, CI/CD-ready, monitored with Prometheus & Grafana. Cloud-deployable.' },
  ]

  return (
    <div className="home-page">
      {/* Contour hero — full viewport */}
      <section className="contour-hero" aria-labelledby="home-title">
        <div className="contour-shadow contour-shadow-left" />
        <div className="contour-shadow contour-shadow-right" />

        <svg className="contour-lines contour-lines-a" viewBox="0 0 1200 640" preserveAspectRatio="none" aria-hidden="true">
          <path d="M-80 180C110 40 240 120 320 250s210 180 320 30 280-120 650-30" />
          <path d="M-80 208C120 72 246 140 333 270s203 152 310 28 280-104 650-18" />
          <path d="M-80 236C132 104 252 160 346 290s196 124 300 26 280-88 650-6" />
          <path d="M-80 264C144 136 258 180 359 310s189 96 290 24 280-72 650 6" />
          <path d="M-80 292C156 168 264 200 372 330s182 68 280 22 280-56 650 18" />
          <path d="M-80 320C168 200 270 220 385 350s175 40 270 20 280-40 650 30" />
          <path d="M-80 348C180 232 276 240 398 370s168 12 260 18 280-24 650 42" />
          <path d="M-80 376C192 264 282 260 411 390s161-16 250 16 280-8 650 54" />
          <path d="M-80 404C204 296 288 280 424 410s154-44 240 14 280 8 650 66" />
          <path d="M-80 432C216 328 294 300 437 430s147-72 230 12 280 24 650 78" />
        </svg>
        <svg className="contour-lines contour-lines-b" viewBox="0 0 1200 640" preserveAspectRatio="none" aria-hidden="true">
          <ellipse cx="170" cy="425" rx="170" ry="120" />
          <ellipse cx="170" cy="425" rx="128" ry="88" />
          <ellipse cx="170" cy="425" rx="88"  ry="58" />
          <ellipse cx="1000" cy="235" rx="230" ry="120" />
          <ellipse cx="1000" cy="235" rx="184" ry="92" />
          <ellipse cx="1000" cy="235" rx="132" ry="64" />
          <ellipse cx="650" cy="455" rx="150" ry="92" />
          <ellipse cx="650" cy="455" rx="104" ry="60" />
        </svg>

        {/* Top bar */}
        <div className="contour-topbar">
          <button className="contour-logo" onClick={() => setActiveTab('home')}>-FAKEGUARD</button>
          <nav className="contour-nav" aria-label="Home navigation">
            <button className="active" onClick={() => setActiveTab('home')}>Home</button>
            <button onClick={() => startDetect('instagram')}>Detect</button>
            <button onClick={() => setActiveTab('bulk')}>Bulk Check</button>
            <button onClick={() => setActiveTab('dashboard')}>Dashboard</button>
            <button onClick={() => setActiveTab('history')}>History</button>
            <button onClick={() => setActiveTab('model')}>Model Info</button>
          </nav>
        </div>

        {/* Hero copy */}
        <div className="contour-copy">
          <p className="contour-kicker">PROFILE SIGNAL ANALYSIS</p>
          <h2 id="home-title">FAKE<br />PROFILE<br />DETECTOR</h2>
          <p>Check Instagram and Twitter/X account patterns with a focused AI workflow for suspicious profile detection, risk scoring, and review history.</p>
          <div className="contour-actions">
            <button className="contour-read" onClick={() => startDetect('instagram')}>Start Scan</button>
            <button className="contour-link" onClick={() => startDetect('twitter')}>Twitter / X →</button>
          </div>
        </div>

        {/* Floating profile card illustration — right side */}
        <div className="hero-visual" aria-hidden="true">
          <div className="hero-card hero-card-1">
            <div className="hc-avatar"><svg viewBox="0 0 40 40"><circle cx="20" cy="16" r="9" fill="#bbb"/><ellipse cx="20" cy="36" rx="14" ry="10" fill="#bbb"/></svg></div>
            <div className="hc-lines"><div/><div/><div/></div>
            <div className="hc-bar"><div className="hc-bar-fill hc-bar-green"/></div>
            <div className="hc-badge hc-badge-real">REAL</div>
          </div>
          <div className="hero-card hero-card-2">
            <div className="hc-avatar hc-avatar-warn"><svg viewBox="0 0 40 40"><circle cx="20" cy="16" r="9" fill="#ccc"/><ellipse cx="20" cy="36" rx="14" ry="10" fill="#ccc"/></svg></div>
            <div className="hc-lines"><div/><div/><div/></div>
            <div className="hc-bar"><div className="hc-bar-fill hc-bar-red"/></div>
            <div className="hc-badge hc-badge-fake">FAKE</div>
          </div>
          <div className="hero-card hero-card-3">
            <div className="hc-gauge"><svg viewBox="0 0 60 60"><circle cx="30" cy="30" r="24" fill="none" stroke="#e0e0da" strokeWidth="4"/><circle cx="30" cy="30" r="24" fill="none" stroke="#111" strokeWidth="4" strokeDasharray="100 52" strokeLinecap="round" transform="rotate(-90 30 30)"/><text x="30" y="34" textAnchor="middle" fontSize="13" fontWeight="900" fill="#111">95%</text></svg></div>
            <div className="hc-label">ACCURACY</div>
          </div>
        </div>

        {/* Animated stat pills */}
        <div className="hero-stats">
          <div className="hero-stat"><span className="hero-stat-num">95%+</span><span>Accuracy</span></div>
          <div className="hero-stat"><span className="hero-stat-num">10K+</span><span>Profiles Trained</span></div>
          <div className="hero-stat"><span className="hero-stat-num">&lt;1s</span><span>Detection Time</span></div>
        </div>

        <div className="contour-footer-note">ML-COLLAGE</div>
      </section>

      {/* Side labels */}
      <aside className="home-side-label home-side-left">29 PROFILE CHECKS</aside>
      <aside className="home-side-label home-side-right">FAKEGUARD</aside>

      {/* Below-fold: feature grid + platform cards */}
      <div className="home-below">
        {/* Feature grid */}
        <section className="home-features" aria-label="Features">
          <div className="home-feat-header">
            <span className="home-feat-tag">CAPABILITIES</span>
            <h3>Everything you need to catch fakes</h3>
          </div>
          <div className="home-feat-grid">
            {features.map((f, i) => (
              <div key={i} className="home-feat-card" style={{ animationDelay: `${i * 80}ms` }}>
                <span className="home-feat-tag-sm">{f.tag}</span>
                <strong>{f.title}</strong>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Platform CTA cards */}
        <section className="home-platform-cta" aria-label="Platform selection">
          <button className="home-cta-card home-cta-insta" onClick={() => startDetect('instagram')}>
            <div className="home-cta-icon"><InstagramIcon /></div>
            <div>
              <div className="home-cta-title">Analyze Instagram</div>
              <div className="home-cta-desc">Followers, posts, engagement & 9 more signals</div>
            </div>
            <span className="home-cta-arrow">→</span>
          </button>
          <button className="home-cta-card home-cta-twitter" onClick={() => startDetect('twitter')}>
            <div className="home-cta-icon"><TwitterIcon /></div>
            <div>
              <div className="home-cta-title">Analyze Twitter / X</div>
              <div className="home-cta-desc">Tweets, retweet ratio, reply patterns & more</div>
            </div>
            <span className="home-cta-arrow">→</span>
          </button>
          <button className="home-cta-card home-cta-bulk" onClick={() => setActiveTab('bulk')}>
            <div className="home-cta-icon" style={{ fontSize: '22px', fontWeight: 900 }}>CSV</div>
            <div>
              <div className="home-cta-title">Bulk CSV Upload</div>
              <div className="home-cta-desc">Process hundreds of profiles at once</div>
            </div>
            <span className="home-cta-arrow">→</span>
          </button>
        </section>
      </div>
    </div>
  )
}

// ===== DETECT TAB =====
function DetectTab({ platform, setPlatform, instaForm, updateInstaForm,
  twitterForm, updateTwitterForm, handlePredict, loading, result, fillDemo }) {
  return (
    <div className="inner-page">
      <div className="inner-page-header">
        <div className="inner-page-title">Detect Fake Profile</div>
        <div className="inner-page-sub">Analyze Instagram or Twitter/X account signals with AI</div>
      </div>
      <ModernVisualPanel platform={platform} />

      {/* Platform selector */}
      <div className="section">
        <div className="section-title">Select Platform</div>
        <PlatformSelector platform={platform} setPlatform={setPlatform} />
      </div>

      {/* Demo buttons */}
      <div className="section" style={{ display: 'flex', gap: '12px', flexWrap: 'wrap' }}>
        <button id="demo-real" className="btn btn-outline" onClick={() => fillDemo('real')}>
          Load Real {platform === 'instagram' ? 'Instagram' : 'Twitter'} Demo
        </button>
        <button id="demo-fake" className="btn btn-outline" onClick={() => fillDemo('fake')}>
          Load Fake {platform === 'instagram' ? 'Instagram' : 'Twitter'} Demo
        </button>
      </div>

      <form onSubmit={handlePredict}>
        {platform === 'instagram' ? (
          <InstagramForm form={instaForm} updateForm={updateInstaForm} />
        ) : (
          <TwitterForm form={twitterForm} updateForm={updateTwitterForm} />
        )}

        {/* Submit */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: '24px' }}>
          <button
            id="btn-analyze"
            type="submit"
            className={`btn btn-primary btn-lg ${platform === 'instagram' ? 'btn-insta' : 'btn-twitter'}`}
            disabled={loading}
          >
            {loading ? (
              <><div className="spinner" /> Analyzing...</>
            ) : (
              <>Analyze {platform === 'instagram' ? 'Instagram' : 'Twitter'} Profile</>
            )}
          </button>
        </div>
      </form>

      {/* Result */}
      {result && <ResultCard result={result} />}
    </div>
  )
}

// ===== INSTAGRAM FORM =====
function InstagramForm({ form, updateForm }) {
  return (
    <>
      <div className="glass-card section">
        <div className="card-header">
          <div className="card-title"><InstagramIcon /> Instagram Profile</div>
          <div className="card-subtitle">Enter Instagram profile information</div>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label"><span className="label-icon">📛</span> Username</label>
              <input id="input-username" className="form-input" type="text" placeholder="e.g., sarah_travels"
                value={form.username} onChange={e => updateForm('username', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">👥</span> Followers</label>
              <input id="input-followers" className="form-input" type="number" placeholder="e.g., 4500"
                value={form.followers_count} onChange={e => updateForm('followers_count', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">➡️</span> Following</label>
              <input id="input-following" className="form-input" type="number" placeholder="e.g., 380"
                value={form.following_count} onChange={e => updateForm('following_count', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">📸</span> Total Posts</label>
              <input id="input-posts" className="form-input" type="number" placeholder="e.g., 342"
                value={form.posts_count} onChange={e => updateForm('posts_count', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">📅</span> Account Age (days)</label>
              <input id="input-age" className="form-input" type="number" placeholder="e.g., 730"
                value={form.account_age_days} onChange={e => updateForm('account_age_days', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">📝</span> Bio Length (chars)</label>
              <input id="input-bio" className="form-input" type="number" placeholder="e.g., 80"
                value={form.bio_length} onChange={e => updateForm('bio_length', e.target.value)} required min="0" />
            </div>
          </div>
        </div>
      </div>

      <div className="glass-card section">
        <div className="card-header">
          <div className="card-title">Engagement & Settings</div>
          <div className="card-subtitle">Activity and engagement metrics</div>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label"><span className="label-icon">❤️</span> Avg Likes/Post</label>
              <input id="input-likes" className="form-input" type="number" placeholder="e.g., 120"
                value={form.avg_likes} onChange={e => updateForm('avg_likes', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">💬</span> Avg Comments/Post</label>
              <input id="input-comments" className="form-input" type="number" placeholder="e.g., 8"
                value={form.avg_comments} onChange={e => updateForm('avg_comments', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">🖼️</span> Profile Picture</label>
              <div className="toggle-group">
                <button type="button" id="toggle-pic" className={`toggle ${form.has_profile_pic ? 'active' : ''}`}
                  onClick={() => updateForm('has_profile_pic', form.has_profile_pic ? 0 : 1)} />
                <span className="toggle-label">{form.has_profile_pic ? 'Yes' : 'No'}</span>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">🔒</span> Private Account</label>
              <div className="toggle-group">
                <button type="button" id="toggle-private" className={`toggle ${form.is_private ? 'active' : ''}`}
                  onClick={() => updateForm('is_private', form.is_private ? 0 : 1)} />
                <span className="toggle-label">{form.is_private ? 'Yes' : 'No'}</span>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">✔️</span> Verified</label>
              <div className="toggle-group">
                <button type="button" id="toggle-verified" className={`toggle ${form.is_verified ? 'active' : ''}`}
                  onClick={() => updateForm('is_verified', form.is_verified ? 0 : 1)} />
                <span className="toggle-label">{form.is_verified ? 'Yes' : 'No'}</span>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">🔗</span> URL in Bio</label>
              <div className="toggle-group">
                <button type="button" id="toggle-url" className={`toggle ${form.has_url_in_bio ? 'active' : ''}`}
                  onClick={() => updateForm('has_url_in_bio', form.has_url_in_bio ? 0 : 1)} />
                <span className="toggle-label">{form.has_url_in_bio ? 'Yes' : 'No'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

// ===== TWITTER FORM =====
function TwitterForm({ form, updateForm }) {
  return (
    <>
      <div className="glass-card section">
        <div className="card-header">
          <div className="card-title"><TwitterIcon /> Twitter / X Profile</div>
          <div className="card-subtitle">Enter Twitter profile information</div>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label"><span className="label-icon">📛</span> Username</label>
              <input id="input-username" className="form-input" type="text" placeholder="e.g., techwriter_mike"
                value={form.username} onChange={e => updateForm('username', e.target.value)} />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">👥</span> Followers</label>
              <input id="input-followers" className="form-input" type="number" placeholder="e.g., 3200"
                value={form.followers_count} onChange={e => updateForm('followers_count', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">➡️</span> Following</label>
              <input id="input-following" className="form-input" type="number" placeholder="e.g., 450"
                value={form.following_count} onChange={e => updateForm('following_count', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">🐦</span> Total Tweets</label>
              <input id="input-tweets" className="form-input" type="number" placeholder="e.g., 8500"
                value={form.tweets_count} onChange={e => updateForm('tweets_count', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">📅</span> Account Age (days)</label>
              <input id="input-age" className="form-input" type="number" placeholder="e.g., 2920"
                value={form.account_age_days} onChange={e => updateForm('account_age_days', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">📝</span> Bio Length (chars)</label>
              <input id="input-bio" className="form-input" type="number" placeholder="e.g., 110"
                value={form.bio_length} onChange={e => updateForm('bio_length', e.target.value)} required min="0" />
            </div>
          </div>
        </div>
      </div>

      <div className="glass-card section">
        <div className="card-header">
          <div className="card-title">Engagement & Settings</div>
          <div className="card-subtitle">Tweet engagement and account details</div>
        </div>
        <div className="card-body">
          <div className="form-grid">
            <div className="form-group">
              <label className="form-label"><span className="label-icon">🔄</span> Avg Retweets</label>
              <input id="input-retweets" className="form-input" type="number" placeholder="e.g., 8"
                value={form.avg_retweets} onChange={e => updateForm('avg_retweets', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">⭐</span> Avg Favorites</label>
              <input id="input-favorites" className="form-input" type="number" placeholder="e.g., 25"
                value={form.avg_favorites} onChange={e => updateForm('avg_favorites', e.target.value)} required min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">📋</span> Listed Count</label>
              <input id="input-listed" className="form-input" type="number" placeholder="e.g., 45"
                value={form.listed_count} onChange={e => updateForm('listed_count', e.target.value)} min="0" />
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">💬</span> Mention Count</label>
              <input id="input-mentions" className="form-input" type="number" placeholder="e.g., 2"
                value={form.mention_count} onChange={e => updateForm('mention_count', e.target.value)} required min="0" />
            </div>
            <div className="form-group slider-group">
              <div className="slider-header">
                <label className="form-label"><span className="label-icon">💬</span> Reply Ratio</label>
                <span className="slider-value">{form.reply_ratio}</span>
              </div>
              <input id="slider-reply" className="form-slider" type="range" min="0" max="1" step="0.01"
                value={form.reply_ratio} onChange={e => updateForm('reply_ratio', parseFloat(e.target.value))} />
              <div className="form-hint">0 = no replies ← → 1 = all replies</div>
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">🖼️</span> Profile Picture</label>
              <div className="toggle-group">
                <button type="button" id="toggle-pic-tw" className={`toggle ${form.has_profile_pic ? 'active' : ''}`}
                  onClick={() => updateForm('has_profile_pic', form.has_profile_pic ? 0 : 1)} />
                <span className="toggle-label">{form.has_profile_pic ? 'Yes' : 'No'}</span>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">✔️</span> Verified</label>
              <div className="toggle-group">
                <button type="button" id="toggle-verified-tw" className={`toggle ${form.is_verified ? 'active' : ''}`}
                  onClick={() => updateForm('is_verified', form.is_verified ? 0 : 1)} />
                <span className="toggle-label">{form.is_verified ? 'Yes' : 'No'}</span>
              </div>
            </div>
            <div className="form-group">
              <label className="form-label"><span className="label-icon">🔗</span> URL in Bio</label>
              <div className="toggle-group">
                <button type="button" id="toggle-url-tw" className={`toggle ${form.has_url_in_bio ? 'active' : ''}`}
                  onClick={() => updateForm('has_url_in_bio', form.has_url_in_bio ? 0 : 1)} />
                <span className="toggle-label">{form.has_url_in_bio ? 'Yes' : 'No'}</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  )
}

// ===== RESULT CARD =====
function ResultCard({ result }) {
  const isFake = result.is_fake === 1
  const probPercent = Math.round(result.probability * 100)
  const accentColor = isFake ? '#d32f2f' : '#11845b'
  const maxImportance = result.feature_importance
    ? Math.max(...Object.values(result.feature_importance))
    : 1

  return (
    <div className="result-container">
      <div className={`result-card ${isFake ? 'result-fake' : 'result-real'}`}>
        {/* Colored accent strip */}
        <div className="result-accent" style={{ background: accentColor }} />

        {/* Header banner */}
        <div className="result-banner">
          <div className="result-icon-wrap" style={{ '--rc': accentColor }}>
            <div className="result-icon">{isFake ? '✕' : '✓'}</div>
          </div>
          <div className="result-info">
            <div className="result-verdict-tag" style={{ color: accentColor }}>
              {isFake ? 'FAKE DETECTED' : 'GENUINE PROFILE'}
            </div>
            <div className="result-title">{result.label}</div>
            <div className="result-subtitle">
              <span className={`platform-tag ${result.platform}`}>
                {result.platform === 'instagram' ? 'Instagram' : 'Twitter / X'}
              </span>
              <span>{isFake
                ? 'This profile shows characteristics of a fake/bot account'
                : 'This profile appears to be a genuine user'}</span>
            </div>
          </div>
        </div>

        <div className="result-body">
          {/* Metrics row */}
          <div className="result-metrics">
            <div className="metric-card metric-card-accent" style={{ '--mc': accentColor }}>
              <ConfidenceGauge value={probPercent} color={accentColor} />
            </div>
            <div className="metric-card">
              <div className="metric-value" style={{ color: accentColor }}>
                {result.label.split(' ')[0]}
              </div>
              <div className="metric-label">Prediction</div>
            </div>
            <div className="metric-card">
              <span className={`risk-badge risk-${result.risk_level}`}>
                {result.risk_level} Risk
              </span>
              <div className="metric-label" style={{ marginTop: '12px' }}>Risk Level</div>
            </div>
          </div>

          {/* Probability bar */}
          <div className="prob-section">
            <div className="prob-header">
              <span className="prob-label">Fake Probability</span>
              <span className="prob-value" style={{ color: accentColor }}>{probPercent}%</span>
            </div>
            <div className="confidence-bar">
              <div
                className={`confidence-bar-fill ${probPercent >= 80 ? 'high' : probPercent >= 50 ? 'medium' : 'low'}`}
                style={{ width: `${probPercent}%` }}
              />
            </div>
          </div>

          {/* Explanations */}
          <div className="explanation-section">
            <div className="explanation-title">
              <span className="explanation-icon">💡</span> AI Explanation
            </div>
            <ul className="explanation-list">
              {result.explanation.map((exp, i) => (
                <li key={i} className="explanation-item">
                  <span className="exp-num">{i + 1}</span>
                  {cleanDisplayText(exp)}
                </li>
              ))}
            </ul>
          </div>

          {/* Feature Importance */}
          {result.feature_importance && Object.keys(result.feature_importance).length > 0 && (
            <div className="feature-importance">
              <div className="explanation-title">
                <span className="explanation-icon">📊</span> Feature Importance
              </div>
              <div className="feature-bar-container">
                {Object.entries(result.feature_importance).slice(0, 8).map(([name, value]) => (
                  <div key={name} className="feature-bar-row">
                    <span className="feature-bar-label">{name}</span>
                    <div className="feature-bar-track">
                      <div className="feature-bar-fill" style={{ width: `${(value / maxImportance) * 100}%` }} />
                    </div>
                    <span className="feature-bar-value">{(value * 100).toFixed(1)}%</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// ===== BULK TAB =====
function BulkTab({ platform, setPlatform, handleBulkUpload, loading, bulkResults, fileInputRef }) {
  return (
    <div className="inner-page">
      <div className="inner-page-header">
        <div className="inner-page-title">Bulk Profile Check</div>
        <div className="inner-page-sub">Upload a CSV to scan hundreds of profiles at once</div>
      </div>
      <div className="section">
        <PlatformSelector platform={platform} setPlatform={setPlatform} />
      </div>

      <div className="glass-card section">
        <div className="card-body">
          <div className="upload-zone" onClick={() => fileInputRef.current?.click()}>
            <div className="upload-zone-icon">CSV</div>
            <div className="upload-zone-text">
              {loading ? 'Processing...' : `Click to upload ${platform} CSV file`}
            </div>
            <div className="upload-zone-hint">
              Upload a CSV with {platform === 'instagram' ? 'Instagram' : 'Twitter'} profile columns
            </div>
            <input ref={fileInputRef} id="bulk-upload-input" className="upload-input"
              type="file" accept=".csv" onChange={handleBulkUpload} />
          </div>
        </div>
      </div>

      {/* Bulk Results */}
      {bulkResults && (
        <div className="result-container">
          <div className="bulk-summary">
            <div className="stat-card">
              <div className="stat-icon blue">T</div>
              <div className="stat-value">{bulkResults.total_profiles}</div>
              <div className="stat-label">Total</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon red">F</div>
              <div className="stat-value">{bulkResults.fake_count}</div>
              <div className="stat-label">Fake</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon green">R</div>
              <div className="stat-value">{bulkResults.real_count}</div>
              <div className="stat-label">Real</div>
            </div>
          </div>

          <div className="glass-card" style={{ marginTop: '24px' }}>
            <div className="card-header"><div className="card-title">Results</div></div>
            <div className="card-body">
              <div className="history-table-container">
                <table className="history-table">
                  <thead>
                    <tr><th>Username</th><th>Prediction</th><th>Probability</th><th>Risk</th></tr>
                  </thead>
                  <tbody>
                    {bulkResults.results.map((r, i) => (
                      <tr key={i}>
                        <td>{r.username || '-'}</td>
                        <td>
                          {r.error ? (
                            <span className="badge badge-fake">Error</span>
                          ) : (
                            <span className={`badge ${r.is_fake ? 'badge-fake' : 'badge-real'}`}>{r.label}</span>
                          )}
                        </td>
                        <td>{r.probability ? `${(r.probability * 100).toFixed(1)}%` : '-'}</td>
                        <td>{r.risk_level && <span className={`risk-badge risk-${r.risk_level}`}>{r.risk_level}</span>}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

// ===== DASHBOARD TAB =====
function DashboardTab({ dashboard }) {
  if (!dashboard) {
    return (
      <div className="inner-page">
        <div className="empty-state">
          <div className="empty-state-icon animate-pulse">...</div>
          <div className="empty-state-text">Loading dashboard...</div>
        </div>
      </div>
    )
  }

  if (dashboard.total_scans === 0) {
    return (
      <div className="inner-page">
        <div className="empty-state">
          <div className="empty-state-icon">...</div>
          <div className="empty-state-text">No data yet</div>
          <div className="empty-state-hint">Analyze some profiles to see dashboard analytics</div>
        </div>
      </div>
    )
  }

  const pb = dashboard.platform_breakdown || {}
  const insta = pb.instagram || { total: 0, fake: 0, real: 0 }
  const tw = pb.twitter || { total: 0, fake: 0, real: 0 }

  return (
    <div className="inner-page">
      <div className="inner-page-header">
        <div className="inner-page-title">Analytics Dashboard</div>
        <div className="inner-page-sub">Overview of all scanned profiles and detection statistics</div>
      </div>

      {/* Stats cards */}
      <div className="dashboard-grid section">
        <div className="stat-card">
          <div className="stat-icon blue">A</div>
          <div className="stat-value">{dashboard.total_scans}</div>
          <div className="stat-label">Total Scans</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon red">F</div>
          <div className="stat-value">{dashboard.fake_count}</div>
          <div className="stat-label">Fake Detected</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon green">R</div>
          <div className="stat-value">{dashboard.real_count}</div>
          <div className="stat-label">Real Profiles</div>
        </div>
        <div className="stat-card">
          <div className="stat-icon purple">P</div>
          <div className="stat-value">{dashboard.fake_percentage}%</div>
          <div className="stat-label">Fake Rate</div>
        </div>
      </div>

      {/* Platform breakdown */}
      <div className="glass-card section">
        <div className="card-header">
          <div className="card-title">Platform Breakdown</div>
        </div>
        <div className="card-body">
          <div className="platform-stats-grid">
            <div className="platform-stat-card instagram-bg">
              <div className="platform-stat-header"><InstagramIcon /> Instagram</div>
              <div className="platform-stat-body">
                <div><span className="stat-num">{insta.total}</span> scanned</div>
                <div><span className="stat-num fake-num">{insta.fake}</span> fake</div>
                <div><span className="stat-num real-num">{insta.real}</span> real</div>
              </div>
            </div>
            <div className="platform-stat-card twitter-bg">
              <div className="platform-stat-header"><TwitterIcon /> Twitter / X</div>
              <div className="platform-stat-body">
                <div><span className="stat-num">{tw.total}</span> scanned</div>
                <div><span className="stat-num fake-num">{tw.fake}</span> fake</div>
                <div><span className="stat-num real-num">{tw.real}</span> real</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Fake vs Real bar */}
      <div className="glass-card section">
        <div className="card-header"><div className="card-title">Fake vs Real Distribution</div></div>
        <div className="card-body">
          <div style={{ display: 'flex', height: '40px', borderRadius: 'var(--radius-sm)', overflow: 'hidden', marginBottom: '12px' }}>
            <div style={{
              width: `${dashboard.fake_percentage}%`,
              background: 'linear-gradient(90deg, #ef4444, #ec4899)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '12px', fontWeight: 700,
              minWidth: dashboard.fake_percentage > 5 ? 'auto' : '0px',
              transition: 'width 0.8s ease-out'
            }}>
              {dashboard.fake_percentage > 10 && `${dashboard.fake_percentage}% Fake`}
            </div>
            <div style={{
              flex: 1,
              background: 'linear-gradient(90deg, #10b981, #06b6d4)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: '12px', fontWeight: 700, transition: 'width 0.8s ease-out'
            }}>
              {(100 - dashboard.fake_percentage) > 10 && `${(100 - dashboard.fake_percentage).toFixed(1)}% Real`}
            </div>
          </div>
        </div>
      </div>

      {/* Risk Distribution */}
      <div className="glass-card section">
        <div className="card-header"><div className="card-title">Risk Distribution</div></div>
        <div className="card-body">
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
            {Object.entries(dashboard.risk_distribution).map(([level, count]) => (
              <div key={level} style={{ textAlign: 'center', padding: '16px', background: 'var(--bg-glass)', borderRadius: 'var(--radius-md)', border: '1px solid var(--border-subtle)' }}>
                <div style={{
                  fontFamily: 'var(--font-mono)', fontSize: '24px', fontWeight: 800,
                  color: level === 'critical' ? '#ef4444' : level === 'high' ? '#f97316' : level === 'medium' ? '#f59e0b' : '#10b981'
                }}>
                  {count}
                </div>
                <div className="metric-label" style={{ textTransform: 'capitalize' }}>{level}</div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

// ===== HISTORY TAB =====
function HistoryTab({ history }) {
  if (!history) {
    return (<div className="inner-page"><div className="empty-state"><div className="empty-state-icon animate-pulse">...</div><div className="empty-state-text">Loading history...</div></div></div>)
  }
  if (history.predictions.length === 0) {
    return (<div className="inner-page"><div className="empty-state"><div className="empty-state-icon">...</div><div className="empty-state-text">No predictions yet</div><div className="empty-state-hint">Analyze profiles to build history</div></div></div>)
  }

  return (
    <div className="inner-page">
      <div className="inner-page-header">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
          <div>
            <div className="inner-page-title">Prediction History</div>
            <div className="inner-page-sub">{history.total} total predictions recorded</div>
          </div>
        </div>
      </div>
      <div className="glass-card">
        <div className="card-body" style={{ padding: '0' }}>
          <div className="history-table-container">
            <table className="history-table" id="history-table">
              <thead>
                <tr>
                  <th>#</th><th>Platform</th><th>Username</th><th>Followers</th>
                  <th>Following</th><th>Prediction</th><th>Probability</th><th>Risk</th><th>Time</th>
                </tr>
              </thead>
              <tbody>
                {history.predictions.map((p) => (
                  <tr key={p.id}>
                    <td style={{ color: 'var(--text-muted)' }}>{p.id}</td>
                    <td>
                      <span className={`platform-tag ${p.platform}`}>
                        {p.platform}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{p.username || '-'}</td>
                    <td>{p.followers_count?.toLocaleString()}</td>
                    <td>{p.following_count?.toLocaleString()}</td>
                    <td>
                      <span className={`badge ${p.prediction === 1 ? 'badge-fake' : 'badge-real'}`}>
                        {p.prediction === 1 ? 'Fake' : 'Real'}
                      </span>
                    </td>
                    <td><span style={{ fontFamily: 'var(--font-mono)' }}>{(p.probability * 100).toFixed(1)}%</span></td>
                    <td><span className={`risk-badge risk-${p.risk_level}`}>{p.risk_level}</span></td>
                    <td style={{ color: 'var(--text-muted)', fontSize: '12px' }}>{new Date(p.timestamp).toLocaleDateString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  )
}

// ===== MODEL TAB =====
function ModelTab({ modelInfo }) {
  if (!modelInfo) {
    return (<div className="inner-page"><div className="empty-state"><div className="empty-state-icon animate-pulse">...</div><div className="empty-state-text">Loading model info...</div></div></div>)
  }

  return (
    <div className="inner-page">
      <div className="inner-page-header">
        <div className="inner-page-title">Model Information</div>
        <div className="inner-page-sub">ML model details, training metrics and feature importance</div>
      </div>

      {Object.entries(modelInfo).map(([platformKey, info]) => {
        const bestResult = info.training_results?.[info.model_name]
        const maxImp = info.feature_importance
          ? Math.max(...Object.values(info.feature_importance))
          : 1

        return (
          <div key={platformKey} className="model-platform-section">
            <div className={`model-platform-header ${platformKey}`}>
              {platformKey === 'instagram' ? <><InstagramIcon /> Instagram Model</> : <><TwitterIcon /> Twitter Model</>}
            </div>

            <div className="model-info-grid">
              {/* Model details */}
              <div className="glass-card">
                <div className="card-header"><div className="card-title">⚙️ Model Details</div></div>
                <div className="card-body">
                  <div className="model-metric-row">
                    <span className="model-metric-name">Algorithm</span>
                    <span className="model-metric-value">{info.model_name}</span>
                  </div>
                  <div className="model-metric-row">
                    <span className="model-metric-name">Training Samples</span>
                    <span className="model-metric-value">{info.training_samples?.toLocaleString()}</span>
                  </div>
                  <div className="model-metric-row">
                    <span className="model-metric-name">Test Samples</span>
                    <span className="model-metric-value">{info.test_samples?.toLocaleString()}</span>
                  </div>
                  <div className="model-metric-row">
                    <span className="model-metric-name">Features</span>
                    <span className="model-metric-value">{info.feature_columns?.length}</span>
                  </div>
                </div>
              </div>

              {/* Performance metrics */}
              <div className="glass-card">
                <div className="card-header"><div className="card-title">Performance</div></div>
                <div className="card-body">
                  {bestResult && <>
                    <div className="model-metric-row">
                      <span className="model-metric-name">Accuracy</span>
                      <span className="model-metric-value">{(bestResult.accuracy * 100).toFixed(1)}%</span>
                    </div>
                    <div className="model-metric-row">
                      <span className="model-metric-name">Precision</span>
                      <span className="model-metric-value">{(bestResult.precision * 100).toFixed(1)}%</span>
                    </div>
                    <div className="model-metric-row">
                      <span className="model-metric-name">Recall</span>
                      <span className="model-metric-value">{(bestResult.recall * 100).toFixed(1)}%</span>
                    </div>
                    <div className="model-metric-row">
                      <span className="model-metric-name">F1 Score</span>
                      <span className="model-metric-value">{(bestResult.f1_score * 100).toFixed(1)}%</span>
                    </div>
                    <div className="model-metric-row">
                      <span className="model-metric-name">AUC-ROC</span>
                      <span className="model-metric-value">{(bestResult.auc_roc * 100).toFixed(1)}%</span>
                    </div>
                  </>}
                </div>
              </div>
            </div>

            {/* Feature Importance */}
            {info.feature_importance && Object.keys(info.feature_importance).length > 0 && (
              <div className="glass-card" style={{ marginTop: '16px' }}>
                <div className="card-header"><div className="card-title">Feature Importance</div></div>
                <div className="card-body">
                  <div className="feature-bar-container">
                    {Object.entries(info.feature_importance).map(([name, value]) => (
                      <div key={name} className="feature-bar-row">
                        <span className="feature-bar-label">{name}</span>
                        <div className="feature-bar-track">
                          <div className="feature-bar-fill" style={{ width: `${(value / maxImp) * 100}%` }} />
                        </div>
                        <span className="feature-bar-value">{(value * 100).toFixed(1)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        )
      })}
    </div>
  )
}

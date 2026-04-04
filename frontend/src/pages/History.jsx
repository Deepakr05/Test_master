import { useState, useEffect } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import axios from 'axios'

function timeAgo(iso) {
  if (!iso) return ''
  const diff = (Date.now() - new Date(iso)) / 1000
  if (diff < 60)    return 'just now'
  if (diff < 3600)  return `${Math.floor(diff/60)}m ago`
  if (diff < 86400) return `${Math.floor(diff/3600)}h ago`
  return `${Math.floor(diff/86400)}d ago`
}

function modelBadge(provider) {
  const map = { openai: 'model-openai', anthropic: 'model-anthropic', google: 'model-google' }
  return map[provider] || 'model-openai'
}
function modelShort(model) {
  if (!model) return '—'
  if (model.includes('gpt-4o')) return 'GPT-4o'
  if (model.includes('gpt-4'))  return 'GPT-4'
  if (model.includes('claude')) return 'Claude'
  if (model.includes('gemini')) return 'Gemini'
  return model.split('-')[0]
}

const FILTERS = ['all','week','month','starred']

export default function History() {
  const navigate = useNavigate()
  const [params] = useSearchParams()

  const [records,   setRecords]   = useState([])
  const [loading,   setLoading]   = useState(true)
  const [query,     setQuery]     = useState(params.get('q') || '')
  const [filter,    setFilter]    = useState('all')
  const [selected,  setSelected]  = useState(null)
  const [preview,   setPreview]   = useState(null)
  const [previewLoading, setPreviewLoading] = useState(false)
  const [toast,     setToast]     = useState(null)

  useEffect(() => { fetchHistory() }, [filter])

  async function fetchHistory() {
    setLoading(true)
    try {
      const r = await axios.get('/api/history', { params: { q: query, filter } })
      setRecords(r.data.data || [])
    } finally {
      setLoading(false)
    }
  }

  async function loadPreview(id) {
    setSelected(id)
    setPreviewLoading(true)
    setPreview(null)
    try {
      const r = await axios.get(`/api/history/${id}`)
      setPreview(r.data.data)
    } finally {
      setPreviewLoading(false)
    }
  }

  function handleSearch(e) {
    e.preventDefault()
    fetchHistory()
  }

  function handleExportCSV() {
    const rows = [
      ['ID','Jira ID','Title','Model','Status','Test Cases','Generated At'],
      ...records.map(r => [r.id, r.jira_id, r.jira_title, r.llm_model, r.status, r.test_case_count, r.generated_at])
    ]
    const csv = rows.map(r => r.map(c => `"${c}"`).join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'testmaster-history.csv'; a.click()
  }

  function copyPreviewMarkdown() {
    if (!preview) return
    navigator.clipboard.writeText(preview.content?.markdown || '')
    showToast('Copied to clipboard!', 'success')
  }

  function showToast(msg, type = 'info') {
    setToast({ msg, type })
    setTimeout(() => setToast(null), 3000)
  }

  return (
    <div className="fade-in">
      <div className="page-header">
        <div>
          <h1 className="page-title">History</h1>
          <p className="page-subtitle">All generated test plans</p>
        </div>
        <button className="btn btn-outline" onClick={handleExportCSV}>
          ⬇ Export CSV
        </button>
      </div>

      {/* Search + Filters */}
      <div style={{ display: 'flex', gap: 12, marginBottom: 16, alignItems: 'center' }}>
        <form onSubmit={handleSearch} style={{ flex: 1 }}>
          <div className="search-bar">
            <span className="search-icon">🔍</span>
            <input
              placeholder="Search by Jira ID or title..."
              value={query}
              onChange={e => setQuery(e.target.value)}
            />
          </div>
        </form>
        <div className="filter-tabs">
          {FILTERS.map(f => (
            <button
              key={f}
              className={`filter-tab ${filter === f ? 'active' : ''}`}
              onClick={() => setFilter(f)}
            >
              {f === 'week' ? 'This Week' : f === 'month' ? 'This Month' : f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {/* Main Panel */}
      <div style={{ display: 'grid', gridTemplateColumns: selected ? '1fr 360px' : '1fr', gap: 16, alignItems: 'start' }}>

        {/* Table */}
        <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th>Jira ID</th>
                <th>Issue Title</th>
                <th>Model</th>
                <th>Test Cases</th>
                <th>Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {loading && (
                <tr><td colSpan={6} style={{ textAlign: 'center', padding: '40px 0' }}>
                  <div className="spinner" style={{ margin: '0 auto' }} />
                </td></tr>
              )}
              {!loading && records.length === 0 && (
                <tr><td colSpan={6} style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '40px 0' }}>
                  No test plans found.
                </td></tr>
              )}
              {records.map(r => (
                <tr
                  key={r.id}
                  onClick={() => loadPreview(r.id)}
                  style={{ background: selected === r.id ? 'rgba(0,229,204,0.04)' : undefined }}
                >
                  <td><span className="badge badge-cyan">{r.jira_id}</span></td>
                  <td style={{ maxWidth: 240, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                    {r.jira_title || r.title}
                  </td>
                  <td>
                    <span className={`model-badge ${modelBadge(r.llm_provider)}`}>
                      {modelShort(r.llm_model)}
                    </span>
                  </td>
                  <td style={{ color: 'var(--text-muted)' }}>{r.test_case_count}</td>
                  <td style={{ color: 'var(--text-muted)', fontSize: 12 }}>{timeAgo(r.generated_at)}</td>
                  <td>
                    <button
                      className="btn btn-ghost"
                      style={{ padding: '4px 10px', fontSize: 12 }}
                      onClick={e => { e.stopPropagation(); navigate(`/plan/${r.id}`) }}
                    >
                      View →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Preview Panel */}
        {selected && (
          <div className="card slide-in" style={{ position: 'sticky', top: 20, maxHeight: '80vh', display: 'flex', flexDirection: 'column' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
              <div style={{ fontWeight: 700, fontSize: 13 }}>Test Plan Preview</div>
              <button className="btn btn-ghost" style={{ padding: '2px 8px', fontSize: 18 }} onClick={() => setSelected(null)}>×</button>
            </div>

            {previewLoading && <div className="spinner" style={{ margin: '32px auto' }} />}

            {preview && !previewLoading && (
              <>
                <div style={{ fontSize: 11, color: 'var(--text-muted)', marginBottom: 6 }}>
                  {preview.jira_id} • {modelShort(preview.llm_model)} • {preview.test_case_count} test cases
                </div>
                <div style={{ fontWeight: 600, fontSize: 14, color: 'var(--cyan)', marginBottom: 10 }}>
                  {preview.jira_title}
                </div>
                <div style={{
                  flex: 1,
                  overflowY: 'auto',
                  background: 'var(--bg)',
                  borderRadius: 'var(--radius)',
                  padding: '12px 14px',
                  fontSize: 12,
                  lineHeight: 1.7,
                  color: 'var(--text-muted)',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  maxHeight: 300,
                  marginBottom: 14,
                }}>
                  {(preview.content?.markdown || '').slice(0, 1000)}
                  {preview.content?.markdown?.length > 1000 ? '\n\n[...truncated for preview]' : ''}
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  <button className="btn btn-outline" style={{ flex: 1, justifyContent: 'center' }} onClick={copyPreviewMarkdown}>
                    📋 Copy
                  </button>
                  <button
                    className="btn btn-primary"
                    style={{ flex: 1, justifyContent: 'center' }}
                    onClick={() => navigate(`/plan/${preview.id}`)}
                  >
                    Open →
                  </button>
                </div>
              </>
            )}
          </div>
        )}
      </div>

      {toast && (
        <div className={`toast toast-${toast.type}`}>
          {toast.type === 'success' ? '✅' : 'ℹ️'} {toast.msg}
        </div>
      )}
    </div>
  )
}

import { useEffect, useState } from 'react'
import { checkHealth, sendMessage } from './api/client'

/**
 * PUBLIC_INTERFACE
 * Main App component for AI Copilot
 */
export default function App() {
  const [health, setHealth] = useState<string>('unknown')
  const [input, setInput] = useState('')
  const [reply, setReply] = useState<string>('')

  useEffect(() => {
    checkHealth()
      .then((d) => setHealth(JSON.stringify(d)))
      .catch((e) => setHealth(`error: ${e.message}`))
  }, [])

  const onSend = async () => {
    const text = input.trim()
    if (!text) return
    setReply('...')
    try {
      const r = await sendMessage(text)
      setReply(r)
    } catch (e: any) {
      setReply(`Error: ${e.message}`)
    }
  }

  return (
    <div style={{ fontFamily: 'system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial', background: '#f9fafb', minHeight: '100vh' }}>
      <header style={{ background: '#ffffff', borderBottom: '1px solid #e5e7eb', padding: '12px 20px', position: 'sticky', top: 0 }}>
        <strong>AI Copilot</strong> <span style={{ color: '#6b7280' }}>Vite + React</span>
      </header>
      <main style={{ maxWidth: 900, margin: '0 auto', padding: 16 }}>
        <section style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 16, marginBottom: 16 }}>
          <div style={{ fontWeight: 600, marginBottom: 8 }}>Health</div>
          <pre style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{health}</pre>
        </section>

        <section style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 12, padding: 16 }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              style={{ flex: 1, padding: '10px 12px', borderRadius: 8, border: '1px solid #e5e7eb' }}
            />
            <button onClick={onSend} style={{ background: '#2563EB', color: '#fff', border: 'none', borderRadius: 8, padding: '10px 16px' }}>
              Send
            </button>
          </div>
          {!!reply && (
            <div style={{ marginTop: 12, color: '#111827' }}>
              <div style={{ fontSize: 12, color: '#6b7280' }}>Assistant:</div>
              <div>{reply}</div>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

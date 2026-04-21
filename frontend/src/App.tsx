import { useState } from 'react'
import type { FormEvent } from 'react'
import chroma from 'chroma-js'
import { guess } from '../api/sdk.gen';
import { client } from '../api/client.gen';

const scale = chroma.scale(['#ff0000', '#ffff00', '#00ff00']).domain([0, 0.5, 1]).mode('lch');

client.setConfig({
  baseUrl: import.meta.env.VITE_API_URL,
})

function App() {
  const [input, setInput] = useState('')
  const [result, setResult] = useState<number | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const [attempts, setAttempts] = useState<Map<string, number>>(new Map())
  const [hasResponded, setHasResponded] = useState(false)

  const percentFmt = new Intl.NumberFormat(undefined, { style: 'percent', maximumFractionDigits: 0 })

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const trimmed = input.trim()
    if (!trimmed) return
    setSubmitting(true)
    setResult(null)
    setHasResponded(false)

    try {
      const { data, error } = await guess({
        query: {
          q: trimmed
        }
      })

      setInput('')
      setHasResponded(true)

      if (error) {
        setResult(null)
        return
      }

      setResult(data.similarity)
      setAttempts((prev) => {
        const next = new Map(prev)
        next.set(data.word, data.similarity)
        if (data.found) {
          alert(`Congrats! You found the word after ${next.size} attempts`);
        }
        return next
      })

    } catch {
      setResult(null)
      setHasResponded(true)
    } finally {
      setSubmitting(false)
    }
  }

  const sortedAttempts = Array.from(attempts.entries())
    .map(([g, s]) => ({ guess: g, score: s }))
    .sort((a, b) => b.score - a.score)

  return (
    <div className='min-h-dvh grid place-items-center px-4'>
      <div className='w-full max-w-3xl'>
        <h1 className='text-4xl font-semibold text-center mb-6'>Guess the secret word</h1>
        <form onSubmit={onSubmit} className='flex flex-col sm:flex-row gap-3'>
          <input
            className='w-full text-2xl px-5 py-4 rounded-lg bg-zinc-900 border border-zinc-800 focus:outline-none focus:ring-2 focus:ring-indigo-500'
            type='text'
            placeholder='Type your guess...'
            value={input}
            onChange={(e) => setInput(e.target.value)}
            aria-label='Guess input'
          />
          <button className='shrink-0 text-lg px-5 py-3 rounded-lg bg-indigo-600 text-white hover:bg-indigo-500 disabled:opacity-50' type='submit' disabled={submitting} aria-label='Submit guess'>
            {submitting ? 'Submitting…' : 'Submit'}
          </button>
        </form>
        {hasResponded && (
          <div className='mt-4 text-lg text-center' aria-live='polite'>
            {result === null ? 'Unknown word' : percentFmt.format(result)}
          </div>
        )}
        {sortedAttempts.length > 0 && (
          <div className='mt-6'>
            <h2 className='text-xl font-medium mb-2'>Attempts</h2>
            <ul className='space-y-2'>
              {sortedAttempts.map((a, idx) => (
                <li key={idx} className='flex items-center justify-between rounded-md border border-zinc-800 bg-zinc-900 px-4 py-2'>
                  <span className='truncate'>{a.guess}</span>
                  <span className='ml-4 font-mono tabular-nums' style={{ color: scale(a.score).hex() }}>{percentFmt.format(a.score)}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

export default App

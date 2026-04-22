import { useEffect, useMemo, useState } from 'react'
import type { FormEvent } from 'react'
import {
  forceCollide,
  forceManyBody,
  forceSimulation,
  forceX,
  forceY,
} from 'd3-force'
import { interpolateLab } from 'd3-interpolate'
import { confetti } from '@tsparticles/confetti'
import { guess, similar } from '../api/sdk.gen'
import { client } from '../api/client.gen'

client.setConfig({
  baseUrl: import.meta.env.VITE_API_URL,
})

type WordData = {
  word: string
  sim: number
  ghost: boolean
  x: number
  y: number
}

const normalize = (sim: number) => Math.max(0, sim)
const toCandelas = (sim: number) => Math.round(Math.pow(normalize(sim), 1.3) * 100)
const toRadius = (sim: number, vp: { w: number; h: number }) => {
  const minR = 40
  const maxR = Math.min(vp.w, vp.h) / 2 - 40
  return minR + (1 - normalize(sim)) * (maxR - minR)
}
const hash = (word: string) => {
  let h = 0
  for (let i = 0; i < word.length; i++) h = (h * 31 + word.charCodeAt(i)) | 0
  return Math.abs(h)
}
const toAngle = (word: string) => ((hash(word) % 360) * Math.PI) / 180

const warmColor = interpolateLab('#e8e6df', '#f5c96b')

function Word({
  word,
  score,
  x,
  y,
  ghost,
}: {
  word: string
  score: number
  x: number
  y: number
  ghost: boolean
}) {
  return (
    <div
      className="absolute -translate-x-1/2 -translate-y-1/2 font-serif font-normal whitespace-nowrap pointer-events-none"
      style={{
        left: x,
        top: y,
        fontSize: 14 + normalize(score) * 18,
        color: ghost ? 'var(--color-ghost)' : warmColor(score),
      }}
    >
      <span
        className="inline-block animate-float [text-shadow:0_0_18px_rgba(245,201,107,0.25)]"
        style={{
          animationDelay: `-${hash(word) % 6}s`,
        }}
      >
        {word}
        <span className="font-mono text-[9px] tracking-[0.15em] text-ink-faint ml-1.5 align-middle">
          {toCandelas(score)}
        </span>
      </span>
    </div>
  )
}

function useForceLayout(words: Omit<WordData, 'x' | 'y'>[]): WordData[] {
  const [positions, setPositions] = useState<Map<string, { x: number; y: number }>>(new Map())

  useEffect(() => {
    if (words.length === 0) return

    const viewport = {
      w: window.innerWidth,
      h: window.innerHeight,
      cx: window.innerWidth / 2,
      cy: window.innerHeight / 2,
    }
    const nodes = words.map((w) => {
      const angle = toAngle(w.word)
      const radius = toRadius(w.sim, viewport)
      return {
        word: w.word,
        ghost: w.ghost,
        anchorX: viewport.cx + Math.cos(angle) * radius,
        anchorY: viewport.cy + Math.sin(angle) * radius,
        radius: Math.max(28, w.word.length * 4 + normalize(w.sim) * 10),
        x: viewport.cx + Math.cos(angle) * radius,
        y: viewport.cy + Math.sin(angle) * radius,
      }
    })

    const sim = forceSimulation(nodes)
      .force('charge', forceManyBody<(typeof nodes)[number]>().strength(-200).distanceMax(150))
      .force('x', forceX<(typeof nodes)[number]>((d) => d.anchorX).strength(0.18))
      .force('y', forceY<(typeof nodes)[number]>((d) => d.anchorY).strength(0.18))
      .force('collide', forceCollide<(typeof nodes)[number]>((d) => d.radius).strength(0.9))
      .alphaDecay(0.02)
      .velocityDecay(0.35)
      .on('tick', () => {
        setPositions(new Map(nodes.map((n) => [n.word, { x: n.x, y: n.y }])))
      })

    return () => {
      sim.stop()
    }
  }, [words])

  return words.map((w) => ({
    ...w,
    x: positions.get(w.word)?.x ?? 0,
    y: positions.get(w.word)?.y ?? 0,
  }))
}

function App() {
  const [input, setInput] = useState('')
  const [target, setTarget] = useState<string | null>(null)
  const [rawWords, setRawWords] = useState<Omit<WordData, 'x' | 'y'>[]>([])

  const guessed = useMemo(() => new Set(rawWords.map((w) => w.word)), [rawWords])
  const words = useForceLayout(rawWords)
  const revealed = target !== null

  const addWord = (word: string, sim: number, ghost = false) => {
    setRawWords((prev) =>
      prev.some((w) => w.word === word) ? prev : [...prev, { word, sim, ghost }],
    )
  }

  const onSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const trimmed = input.trim().toLowerCase()
    if (!trimmed || revealed || guessed.has(trimmed)) {
      setInput('')
      return
    }

    const { data, error } = await guess({ query: { q: trimmed } })
    setInput('')
    if (error || !data) return

    const w = data.word.toLowerCase()
    if (guessed.has(w)) return

    if (!data.found) {
      addWord(w, data.similarity)
      return
    }

    if (target !== null) return
    setTarget(w)
    confetti({
      count: 140,
      position: { x: 50, y: 50 },
      spread: 120,
      startVelocity: 45,
      ticks: 200,
      colors: ['#f5c96b', '#ffb347', '#e8e6df', '#fff4d6', '#c9985a'],
      shapes: ['square', 'circle'],
      scalar: 1,
      zIndex: 50,
    })

    setTimeout(async () => {
        const { data: simData } = await similar({ query: { q: w } })
        if (!simData) return
        simData.words
          .filter((sw) => !guessed.has(sw.word.toLowerCase()))
          .sort((a, b) => b.similarity - a.similarity)
          .slice(0, 60)
          .forEach((g, i) => {
            setTimeout(() => addWord(g.word.toLowerCase(), g.similarity, true), 400 + i * 200)
          })
    }, 600)
  }

  return (
    <main className='relative h-dvh bg-bg-deep'>
      <div className="absolute top-0 left-0 right-0 px-7 py-[22px] flex justify-between items-baseline z-10">
        <div className="font-serif font-light text-[28px] tracking-[0.02em] text-ink">
          kandela<em className="italic font-normal text-flame">.</em>
        </div>
        <a href="https://github.com/kabukki/kandela" target="_blank" rel="noopener noreferrer">
          <svg className='size-4 fill-ink-dim' role="img" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><title>GitHub</title><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
        </a>
        {/* <div className="font-mono text-[11px] tracking-[0.18em] uppercase text-ink-dim text-right">
          day 001 · <span className="text-flame">{tries}</span> tries
        </div> */}
      </div>

      {/* <div className="fixed inset-0 z-[1] overflow-hidden"> */}
        <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-[140px] h-[140px] flex items-center justify-center">
          <div className="absolute -inset-20 bg-[radial-gradient(circle,var(--color-flame-soft)_0%,transparent_65%)] animate-breathe" />
          <div
            className={`size-[14px] rounded-full bg-flame shadow-[0_0_24px_var(--color-flame-glow),0_0_48px_var(--color-flame-soft),0_0_80px_rgba(245,201,107,0.08)] animate-pulse-star`}
          />
          <div
            className={
              revealed && target
                ? 'absolute top-[calc(50%+40px)] font-serif italic font-normal text-4xl tracking-[0.04em] text-flame opacity-100 transition-opacity duration-400'
                : 'absolute top-[calc(50%+36px)] font-mono text-[13px] tracking-[0.4em] text-flame opacity-70 transition-opacity duration-400'
            }
          >
            {revealed && target ? target : '? ? ?'}
          </div>
        </div>

        {words.map((w) => (
          <Word key={w.word} word={w.word} score={w.sim} x={w.x} y={w.y} ghost={w.ghost} />
        ))}
      {/* </div> */}

      <div className="absolute bottom-0 left-0 right-0 px-7 pt-5 pb-7 z-10 bg-gradient-to-t from-bg-deep from-40% to-transparent">
        <form
          onSubmit={onSubmit}
          className="max-w-[560px] mx-auto flex items-center"
        >
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="type your guess..."
            autoComplete="off"
            autoFocus
            disabled={revealed}
            aria-label="Guess input"
            className="flex-1 bg-transparent border-none outline-none text-center text-ink font-serif text-[22px] font-normal py-1 placeholder:text-ink-faint placeholder:italic"
          />
        </form>
      </div>
    </main>
  )
}

export default App

import { useState, useCallback, useRef } from 'react'
import { useAuthStore } from '../store/authStore'

export function useChatStream() {
  const [streaming, setStreaming] = useState(false)
  const abortRef = useRef<AbortController | null>(null)
  const { token } = useAuthStore()

  const startStream = useCallback(
    (url: string, body: Record<string, any>, onToken: (t: string) => void, onDone: (sources: any[]) => void, onError: (e: string) => void) => {
      setStreaming(true)
      const controller = new AbortController()
      abortRef.current = controller

      fetch(url, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
        signal: controller.signal,
      })
        .then(async (response) => {
          const reader = response.body?.getReader()
          if (!reader) throw new Error('No reader')

          const decoder = new TextDecoder()
          let buffer = ''

          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            buffer += decoder.decode(value, { stream: true })
            const lines = buffer.split('\n')
            buffer = lines.pop() || ''

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6)
                if (data === '[DONE]') {
                  setStreaming(false)
                  return
                }
                try {
                  const parsed = JSON.parse(data)
                  if (parsed.token) {
                    onToken(parsed.token)
                  } else if (parsed.sources) {
                    onDone(parsed.sources)
                  } else if (parsed.error) {
                    onError(parsed.error)
                  } else if (parsed.status === 'no_answer') {
                    onToken(parsed.answer)
                    onDone([])
                  }
                } catch {}
              }
            }
          }
          setStreaming(false)
        })
        .catch((err) => {
          if (err.name !== 'AbortError') {
            onError(err.message)
          }
          setStreaming(false)
        })
    },
    [token]
  )

  const stopStream = useCallback(() => {
    abortRef.current?.abort()
    setStreaming(false)
  }, [])

  return { streaming, startStream, stopStream }
}

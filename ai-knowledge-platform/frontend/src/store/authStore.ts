import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface AuthState {
  token: string | null
  username: string | null
  role: string | null
  userId: string | null
  setAuth: (token: string, username: string, role: string, userId: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      username: null,
      role: null,
      userId: null,
      setAuth: (token, username, role, userId) =>
        set({ token, username, role, userId }),
      logout: () =>
        set({ token: null, username: null, role: null, userId: null }),
    }),
    { name: 'akp-auth' }
  )
)

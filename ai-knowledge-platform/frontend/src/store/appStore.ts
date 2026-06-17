import { create } from 'zustand'

interface AppState {
  collapsed: boolean
  setCollapsed: (collapsed: boolean) => void
}

export const useAppStore = create<AppState>((set) => ({
  collapsed: false,
  setCollapsed: (collapsed) => set({ collapsed }),
}))

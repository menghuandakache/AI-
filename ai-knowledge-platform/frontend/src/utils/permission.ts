export function isAdmin(role: string | null): boolean {
  return role === 'admin' || role === 'knowledge_admin'
}

export function canEdit(role: string | null): boolean {
  return isAdmin(role)
}

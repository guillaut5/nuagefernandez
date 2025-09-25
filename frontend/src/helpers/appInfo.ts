export const APP_INFO = __APP_INFO__

export function formatAppInfoLine() {
  const { name, version, commit } = APP_INFO
  return `${name} v${version}${commit ? ` (${commit})` : ''}`
}

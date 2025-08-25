/** Format “il y a 30 s / 40 min / 3 h / 2 j”, sinon date ex: “20 mars 25” */
export function formatWhen(iso: string): string {
  const now = new Date()
  const then = new Date(iso)
  const diffMs = now.getTime() - then.getTime()

  // bornes
  const sec = Math.floor(diffMs / 1000)
  const min = Math.floor(sec / 60)
  const hour = Math.floor(min / 60)
  const day = Math.floor(hour / 24)

  if (sec < 60) return `il y a ${sec}s`
  if (min < 60) return `il y a ${min} min`
  if (hour < 24) return `il y a ${hour} h`
  if (day < 7) return `il y a ${day} j`

  // Au-delà de 7 jours → date courte en FR (ex: 20 mars 25)
  return new Intl.DateTimeFormat('fr-FR', {
    day: '2-digit',
    month: 'long',
    year: '2-digit',
  }).format(then)
}

import { getBackendBaseUrl } from "@/lib/auth"

const palettes = [
  { background: "#0f766e", darkStroke: "#0f172a", lightStroke: "#ecfeff", accent: "#99f6e4" },
  { background: "#0284c7", darkStroke: "#082f49", lightStroke: "#e0f2fe", accent: "#bae6fd" },
  { background: "#7c3aed", darkStroke: "#2e1065", lightStroke: "#f3e8ff", accent: "#ddd6fe" },
  { background: "#ea580c", darkStroke: "#431407", lightStroke: "#ffedd5", accent: "#fdba74" },
  { background: "#be123c", darkStroke: "#4c0519", lightStroke: "#ffe4e6", accent: "#fda4af" },
  { background: "#4f46e5", darkStroke: "#1e1b4b", lightStroke: "#e0e7ff", accent: "#c7d2fe" },
] as const

function hashString(value: string) {
  let hash = 2166136261

  for (let index = 0; index < value.length; index += 1) {
    hash ^= value.charCodeAt(index)
    hash = Math.imul(hash, 16777619)
  }

  return hash >>> 0
}

function escapeSvgText(value: string) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;")
}

function formatCssUrl(value: string) {
  return `url("${value.replaceAll('"', '\\"')}")`
}

export function createClassCoverDataUrl(seed: string, title: string) {
  const hash = hashString(seed)
  const palette = palettes[hash % palettes.length]
  const width = 1600
  const height = 900
  const columns = 6
  const rows = 4
  const cellWidth = width / columns
  const cellHeight = height / rows
  const radius = Math.min(cellWidth, cellHeight) * 0.38
  const circleMarkup: string[] = []

  for (let row = 0; row < rows; row += 1) {
    for (let column = 0; column < columns; column += 1) {
      const opacitySeed = hashString(`${seed}:${row}:${column}`)
      const opacity = (((opacitySeed % 12) + 2) / 100).toFixed(2)
      const stroke =
        opacitySeed % 3 === 0 ? palette.lightStroke : opacitySeed % 2 === 0 ? palette.accent : palette.darkStroke

      circleMarkup.push(
        `<circle cx="${(column + 0.5) * cellWidth}" cy="${(row + 0.5) * cellHeight}" r="${radius}" fill="none" stroke="${stroke}" stroke-width="${Math.max(16, radius * 0.22)}" opacity="${opacity}" />`
      )
    }
  }

  const titleText = escapeSvgText(title.trim() || "Untitled class")
  const initials = escapeSvgText(
    title
      .trim()
      .split(/\s+/)
      .slice(0, 2)
      .map((part) => part[0]?.toUpperCase() ?? "")
      .join("") || "CL"
  )

  const svg = `
    <svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${height}" viewBox="0 0 ${width} ${height}" fill="none">
      <rect width="${width}" height="${height}" fill="${palette.background}" />
      <rect width="${width}" height="${height}" fill="url(#glow)" opacity="0.55" />
      ${circleMarkup.join("")}
      <circle cx="${width - 180}" cy="${170}" r="120" fill="${palette.accent}" opacity="0.18" />
      <circle cx="${220}" cy="${height - 120}" r="96" fill="${palette.lightStroke}" opacity="0.14" />
      <text x="110" y="190" fill="${palette.lightStroke}" font-family="Georgia, 'Times New Roman', serif" font-size="104" font-weight="700" opacity="0.92">${initials}</text>
      <text x="110" y="${height - 120}" fill="${palette.lightStroke}" font-family="Georgia, 'Times New Roman', serif" font-size="64" font-weight="700">${titleText}</text>
      <text x="110" y="${height - 68}" fill="${palette.lightStroke}" font-family="'Trebuchet MS', sans-serif" font-size="28" letter-spacing="6" opacity="0.74">LECTURER WORKSPACE</text>
      <defs>
        <radialGradient id="glow" cx="0" cy="0" r="1" gradientTransform="translate(${width} 0) rotate(135) scale(${width * 0.75} ${height})">
          <stop offset="0" stop-color="${palette.lightStroke}" />
          <stop offset="1" stop-color="${palette.background}" stop-opacity="0" />
        </radialGradient>
      </defs>
    </svg>
  `.trim()

  return `data:image/svg+xml;charset=UTF-8,${encodeURIComponent(svg)}`
}

export function resolveClassImageUrl(imageUrl?: string | null) {
  if (!imageUrl) {
    return null
  }

  if (
    imageUrl.startsWith("http://") ||
    imageUrl.startsWith("https://") ||
    imageUrl.startsWith("data:") ||
    imageUrl.startsWith("blob:")
  ) {
    return imageUrl
  }

  try {
    return new URL(imageUrl, `${getBackendBaseUrl()}/`).toString()
  } catch {
    return imageUrl
  }
}

export function getClassCoverBackgroundImage({
  seed,
  title,
  imageUrl,
}: {
  seed: string
  title: string
  imageUrl?: string | null
}) {
  const fallbackUrl = createClassCoverDataUrl(seed, title)
  const resolvedImageUrl = resolveClassImageUrl(imageUrl)

  return resolvedImageUrl
    ? `${formatCssUrl(resolvedImageUrl)}, ${formatCssUrl(fallbackUrl)}`
    : formatCssUrl(fallbackUrl)
}

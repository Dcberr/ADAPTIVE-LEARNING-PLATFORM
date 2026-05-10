"use client"

import { useMemo, useState } from "react"

type ExternalAvatarProps = {
  src?: string | null
  alt: string
  className: string
  fallback: React.ReactNode
}

export default function ExternalAvatar({
  src,
  alt,
  className,
  fallback,
}: ExternalAvatarProps) {
  const normalizedSrc = useMemo(() => src?.trim() || null, [src])
  const [failedSrc, setFailedSrc] = useState<string | null>(null)
  const hasError = normalizedSrc !== null && failedSrc === normalizedSrc

  if (!normalizedSrc || hasError) {
    return <>{fallback}</>
  }

  return (
    // Some Google-hosted profile images fail when the browser sends a referrer.
    // Rendering without a referrer keeps the direct URL usable in the page as well.
    // eslint-disable-next-line @next/next/no-img-element
    <img
      src={normalizedSrc}
      alt={alt}
      className={className}
      referrerPolicy="no-referrer"
      onError={() => setFailedSrc(normalizedSrc)}
    />
  )
}

export type FixedTagOption = {
  label: string
  slug: string
}

export const FIXED_TAG_OPTIONS: FixedTagOption[] = [
  { label: "Array", slug: "array" },
  { label: "String", slug: "string" },
  { label: "Math", slug: "math" },
  { label: "Simulation", slug: "simulation" },
  { label: "Counting", slug: "counting" },
  { label: "Matrix", slug: "matrix" },
  { label: "Prefix Sum", slug: "prefix-sum" },
  { label: "Two Pointers", slug: "two-pointers" },
  { label: "Recursion", slug: "recursion" },
]

const FIXED_TAG_SLUGS = new Set(FIXED_TAG_OPTIONS.map((option) => option.slug))

export function normalizeFixedTagSlugs(tags?: string[] | null) {
  if (!tags?.length) {
    return []
  }

  const deduped = new Set(
    tags.map((tag) => tag.trim()).filter((tag) => tag.length > 0 && FIXED_TAG_SLUGS.has(tag))
  )

  return FIXED_TAG_OPTIONS.map((option) => option.slug).filter((slug) => deduped.has(slug))
}

export function getFixedTagOption(slug: string) {
  return FIXED_TAG_OPTIONS.find((option) => option.slug === slug) ?? null
}

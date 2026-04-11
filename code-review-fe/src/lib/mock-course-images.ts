export const mockCourseImageUrls: Record<string, string> = {
  "ai-digital-economy":
    "https://images.unsplash.com/photo-1655393001768-d946c97d6fd1?auto=format&fit=crop&w=1080&q=80",
  "fintech-blockchain":
    "https://images.unsplash.com/photo-1649359569078-c445b3c6a116?auto=format&fit=crop&w=1080&q=80",
  "design-thinking":
    "https://images.unsplash.com/photo-1562939651-9359f291c988?auto=format&fit=crop&w=1080&q=80",
  "algorithmic-trading":
    "https://images.unsplash.com/photo-1766218326892-4b261b02a03f?auto=format&fit=crop&w=1080&q=80",
  "marketing-analytics":
    "https://images.unsplash.com/photo-1599658880436-c61792e70672?auto=format&fit=crop&w=1080&q=80",
  "sustainable-business":
    "https://images.unsplash.com/photo-1741118843309-bbfe149f7b9e?auto=format&fit=crop&w=1080&q=80",
}

export function getMockCourseImageUrl(imageKey?: string | null) {
  if (!imageKey) {
    return null
  }

  return mockCourseImageUrls[imageKey] ?? null
}

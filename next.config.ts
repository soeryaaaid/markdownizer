import type { NextConfig } from "next"

const nextConfig: NextConfig = {
  experimental: {
    proxyClientMaxBodySize: "100MB",
  },
}

export default nextConfig

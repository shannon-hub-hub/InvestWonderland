/** @type {import('next').NextConfig} */
const apiInternal = process.env.API_URL || 'http://127.0.0.1:8000';

const isProd = process.env.NODE_ENV === 'production';

const nextConfig = {
  // Standalone is for Docker/production only — do not use during `next dev`
  ...(isProd ? { output: 'standalone' } : {}),
  async rewrites() {
    return [
      { source: '/api/v1/:path*', destination: `${apiInternal}/api/v1/:path*` },
      { source: '/api/health', destination: `${apiInternal}/health` },
      { source: '/health', destination: `${apiInternal}/health` },
      { source: '/api/docs', destination: `${apiInternal}/api/docs` },
      { source: '/api/redoc', destination: `${apiInternal}/api/redoc` },
      { source: '/api/openapi.json', destination: `${apiInternal}/api/openapi.json` },
      { source: '/openapi.json', destination: `${apiInternal}/api/openapi.json` },
    ];
  },
};

module.exports = nextConfig;

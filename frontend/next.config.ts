import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Image de production minimale (voir frontend/Dockerfile) : ne copie que
  // les fichiers réellement nécessaires au runtime, sans node_modules complet.
  output: "standalone",
};

export default nextConfig;

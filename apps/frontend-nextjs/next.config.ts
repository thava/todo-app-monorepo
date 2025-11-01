import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  transpilePackages: ['@todo-app/database', '@todo-app/shared'],
};

export default nextConfig;

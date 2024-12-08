/** @type {import('next').NextConfig} */
const nextConfig = {
    logging: {
        fetches: {
            fullUrl: true,
        },
    },
    images: {
        remotePatterns: [
          {
            protocol: 'https',
            hostname: 'avatars.githubusercontent.com',
            port: '',
            pathname: '/u/**',
          },
          {
              protocol: 'https',
              hostname: 'lh3.googleusercontent.com',
              port: '',
              pathname: '/a/**',
          },
        ],
      },
};

export default nextConfig;

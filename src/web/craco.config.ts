import path from 'path';
import CracoAlias from 'craco-alias';
import CompressionPlugin from 'compression-webpack-plugin';
import { CracoConfig } from '@craco/craco';

const cracoConfig: CracoConfig = {
  webpack: {
    configure: (webpackConfig, { env, paths }) => {
      // Add CompressionPlugin for production builds
      if (env === 'production') {
        if (!webpackConfig.plugins) {
          webpackConfig.plugins = [];
        }
        webpackConfig.plugins.push(
          new CompressionPlugin({
            filename: '[path][base].gz',
            algorithm: 'gzip',
            test: /\.(js|css|html|svg)$/,
            threshold: 10240, // Only compress assets larger than 10KB
            minRatio: 0.8,
          })
        );
      }

      // Configure optimization settings for better performance
      if (!webpackConfig.optimization) {
        webpackConfig.optimization = {};
      }

      webpackConfig.optimization.runtimeChunk = 'single';
      
      // Set up code splitting for vendor modules
      if (!webpackConfig.optimization.splitChunks) {
        webpackConfig.optimization.splitChunks = {
          chunks: 'all',
          name: false,
        };
      }

      webpackConfig.optimization.splitChunks = {
        ...webpackConfig.optimization.splitChunks,
        cacheGroups: {
          vendor: {
            name: 'vendors',
            test: /[\\/]node_modules[\\/]/,
            chunks: 'all',
            priority: 10,
          },
          common: {
            name: 'common',
            minChunks: 2,
            chunks: 'async',
            priority: 5,
            reuseExistingChunk: true,
            enforce: true,
          },
        },
      };

      // Configure source maps based on environment
      if (env === 'production') {
        // Use source-map for production to help with debugging while still being optimized
        webpackConfig.devtool = 'source-map';
      } else {
        // Use eval-cheap-module-source-map for development for fast builds
        webpackConfig.devtool = 'eval-cheap-module-source-map';
      }

      return webpackConfig;
    },
    plugins: {
      add: [
        ...(process.env.NODE_ENV === 'production'
          ? [
              new CompressionPlugin({
                filename: '[path][base].gz',
                algorithm: 'gzip',
                test: /\.(js|css|html|svg)$/,
                threshold: 10240,
                minRatio: 0.8,
              }),
            ]
          : []),
      ],
    },
  },
  babel: {
    presets: [
      '@babel/preset-env',
      '@babel/preset-react',
      '@babel/preset-typescript',
    ],
    plugins: [
      '@babel/plugin-proposal-optional-chaining',
      '@babel/plugin-proposal-nullish-coalescing-operator',
      '@babel/plugin-transform-runtime',
    ],
  },
  typescript: {
    enableTypeChecking: true,
  },
  eslint: {
    enable: true,
    mode: 'extends',
    configure: {
      extends: [
        'react-app',
        'react-app/jest',
        'plugin:@typescript-eslint/recommended',
        'plugin:prettier/recommended',
      ],
      rules: {
        '@typescript-eslint/explicit-function-return-type': 'off',
        '@typescript-eslint/explicit-module-boundary-types': 'off',
        'react/react-in-jsx-scope': 'off',
      },
    },
  },
  jest: {
    configure: {
      moduleNameMapper: {
        '^@components/(.*)$': '<rootDir>/src/components/$1',
        '^@pages/(.*)$': '<rootDir>/src/pages/$1',
        '^@layouts/(.*)$': '<rootDir>/src/layouts/$1',
        '^@hooks/(.*)$': '<rootDir>/src/hooks/$1',
        '^@store/(.*)$': '<rootDir>/src/store/$1',
        '^@api/(.*)$': '<rootDir>/src/api/$1',
        '^@utils/(.*)$': '<rootDir>/src/utils/$1',
        '^@types/(.*)$': '<rootDir>/src/types/$1',
        '^@config/(.*)$': '<rootDir>/src/config/$1',
        '^@assets/(.*)$': '<rootDir>/src/assets/$1',
        '^@responsive/(.*)$': '<rootDir>/src/responsive/$1',
        '^@context/(.*)$': '<rootDir>/src/context/$1',
      },
      setupFilesAfterEnv: ['<rootDir>/src/setupTests.ts'],
      testEnvironment: 'jsdom',
    },
  },
  plugins: [
    {
      plugin: CracoAlias,
      options: {
        source: 'tsconfig',
        baseUrl: 'src',
        tsConfigPath: './tsconfig.json',
      },
    },
  ],
  devServer: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false,
        pathRewrite: {
          '^/api': '',
        },
      },
    },
  },
};

export default cracoConfig;
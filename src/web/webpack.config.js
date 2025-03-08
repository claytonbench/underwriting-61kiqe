/**
 * Webpack 5.88+ configuration for the loan management system frontend application
 * This configuration supports both development and production environments
 * with appropriate optimizations for each.
 */

const path = require('path'); // v18.16.0
const webpack = require('webpack'); // v5.88.0
const HtmlWebpackPlugin = require('html-webpack-plugin'); // v5.5.3
const CompressionPlugin = require('compression-webpack-plugin'); // v10.0.0
const TerserPlugin = require('terser-webpack-plugin'); // v5.3.9
const MiniCssExtractPlugin = require('mini-css-extract-plugin'); // v2.7.6
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin'); // v5.0.1
const ReactRefreshWebpackPlugin = require('@pmmmwh/react-refresh-webpack-plugin'); // v0.5.10

module.exports = (env, argv) => {
  // Determine if we're in development or production mode
  const isDev = argv.mode !== 'production';
  
  return {
    // Entry points for the application and vendor libraries for code splitting
    entry: {
      main: './src/index.tsx',
      vendor: [
        'react', 
        'react-dom', 
        'react-router-dom', 
        '@mui/material', 
        'redux', 
        'react-redux', 
        'formik'
      ]
    },
    
    // Output configuration with content hashing for production builds
    output: {
      path: path.resolve(__dirname, 'build'),
      filename: isDev 
        ? 'static/js/[name].js' 
        : 'static/js/[name].[contenthash:8].js',
      chunkFilename: isDev 
        ? 'static/js/[name].chunk.js' 
        : 'static/js/[name].[contenthash:8].chunk.js',
      publicPath: '/',
      clean: true, // Clean the output directory before emit
    },
    
    // Module rules for handling different file types
    module: {
      rules: [
        // TypeScript/JavaScript processing with Babel
        {
          test: /\.(ts|tsx|js|jsx)$/,
          exclude: /node_modules/,
          use: {
            loader: 'babel-loader',
            options: {
              cacheDirectory: true,
              plugins: [
                // Enable React Fast Refresh in development
                isDev && require.resolve('react-refresh/babel'),
              ].filter(Boolean),
            },
          },
        },
        
        // CSS processing with extraction for production
        {
          test: /\.css$/,
          use: [
            // Use style-loader in development for HMR support
            // Use MiniCssExtractPlugin.loader in production for file extraction
            isDev ? 'style-loader' : MiniCssExtractPlugin.loader,
            'css-loader',
            'postcss-loader',
          ],
        },
        
        // Image processing with asset modules
        {
          test: /\.(png|jpg|jpeg|gif|svg)$/,
          type: 'asset', // Automatically chooses between asset/resource and asset/inline
          parser: {
            dataUrlCondition: {
              maxSize: 10000, // 10kb - inline if smaller
            },
          },
          generator: {
            filename: 'static/media/[name].[hash:8].[ext]',
          },
        },
        
        // Font processing with asset/resource
        {
          test: /\.(woff|woff2|eot|ttf|otf)$/,
          type: 'asset/resource', // Always emits separate file
          generator: {
            filename: 'static/fonts/[name].[hash:8].[ext]',
          },
        },
      ],
    },
    
    // Build optimization configuration
    optimization: {
      // Code splitting configuration
      splitChunks: {
        chunks: 'all', // Split all chunks
        name: false, // Prevent changing chunk names
        cacheGroups: {
          // Create a vendors chunk for node_modules code
          vendor: {
            test: /node_modules/,
            name: 'vendors',
            chunks: 'all',
          },
        },
      },
      runtimeChunk: 'single', // Create a single runtime chunk
      minimize: !isDev, // Only minimize in production
      minimizer: [
        new TerserPlugin({
          // JavaScript minification
          terserOptions: {
            compress: true,
            mangle: true,
            output: {
              comments: false, // Remove comments
            },
          },
          extractComments: false, // Don't extract comments to separate file
        }),
        new CssMinimizerPlugin({
          // CSS minification
          minimizerOptions: {
            preset: [
              'default',
              {
                discardComments: { removeAll: true }, // Remove all comments
              },
            ],
          },
        }),
      ],
    },
    
    // Development server configuration
    devServer: {
      static: {
        directory: path.join(__dirname, 'public'), // Serve content from public directory
      },
      port: 3000,
      hot: true, // Enable hot module replacement
      historyApiFallback: true, // Redirect 404s to index.html for SPA routing
      proxy: {
        // Proxy API requests to backend server
        '/api': {
          target: 'http://localhost:8000',
          changeOrigin: true,
          secure: false,
          pathRewrite: {
            '^/api': '', // Remove /api prefix when forwarding
          },
        },
      },
    },
    
    // Webpack plugins configuration
    plugins: [
      // Common plugins used in both development and production
      new HtmlWebpackPlugin({
        template: 'public/index.html',
        favicon: 'public/favicon.ico',
        minify: !isDev ? {
          removeComments: true,
          collapseWhitespace: true,
          removeRedundantAttributes: true,
          useShortDoctype: true,
          removeEmptyAttributes: true,
          removeStyleLinkTypeAttributes: true,
          keepClosingSlash: true,
          minifyJS: true,
          minifyCSS: true,
          minifyURLs: true,
        } : false,
      }),
      new webpack.DefinePlugin({
        __DEV__: isDev,
        'process.env.NODE_ENV': JSON.stringify(isDev ? 'development' : 'production'),
      }),
      
      // Development-only plugins
      ...(isDev ? [
        new webpack.HotModuleReplacementPlugin(), // Enable HMR
        new ReactRefreshWebpackPlugin(), // React Fast Refresh
      ] : []),
      
      // Production-only plugins
      ...(!isDev ? [
        new MiniCssExtractPlugin({
          // Extract CSS into separate files
          filename: 'static/css/[name].[contenthash:8].css',
          chunkFilename: 'static/css/[name].[contenthash:8].chunk.css',
        }),
        new CompressionPlugin({
          // Compress assets with gzip
          algorithm: 'gzip',
          test: /\.(js|css|html|svg)$/,
          threshold: 10240, // 10kb
          minRatio: 0.8, // Only compress if compression ratio is better than 0.8
        }),
      ] : []),
    ],
    
    // Module resolution configuration
    resolve: {
      extensions: ['.tsx', '.ts', '.js', '.jsx', '.json'], // File extensions to resolve
      alias: {
        // Path aliases that match tsconfig paths
        '@components': path.resolve(__dirname, 'src/components'),
        '@pages': path.resolve(__dirname, 'src/pages'),
        '@layouts': path.resolve(__dirname, 'src/layouts'),
        '@hooks': path.resolve(__dirname, 'src/hooks'),
        '@store': path.resolve(__dirname, 'src/store'),
        '@api': path.resolve(__dirname, 'src/api'),
        '@utils': path.resolve(__dirname, 'src/utils'),
        '@types': path.resolve(__dirname, 'src/types'),
        '@config': path.resolve(__dirname, 'src/config'),
        '@assets': path.resolve(__dirname, 'src/assets'),
        '@responsive': path.resolve(__dirname, 'src/responsive'),
        '@context': path.resolve(__dirname, 'src/context'),
      },
    },
    
    // Performance hints configuration
    performance: {
      hints: isDev ? false : 'warning', // Disable in development, show warnings in production
      maxAssetSize: 512000, // 500kb
      maxEntrypointSize: 512000, // 500kb
    },
    
    // Source map configuration
    devtool: isDev ? 'eval-source-map' : 'source-map',
  };
};
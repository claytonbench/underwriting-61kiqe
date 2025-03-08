module.exports = {
  presets: [
    [
      '@babel/preset-env',
      {
        useBuiltIns: 'usage',
        corejs: 3,
        targets: {
          browsers: [
            'defaults',
            'not IE 11',
            '>0.2%',
            'not dead',
            'not op_mini all'
          ]
        }
      }
    ],
    [
      '@babel/preset-react',
      {
        runtime: 'automatic' // Uses the new JSX transform from React 17+
      }
    ],
    [
      '@babel/preset-typescript',
      {
        isTSX: true,
        allExtensions: true
      }
    ]
  ],
  plugins: [
    '@babel/plugin-proposal-optional-chaining',
    '@babel/plugin-proposal-nullish-coalescing-operator',
    [
      '@babel/plugin-transform-runtime',
      {
        regenerator: true,
        corejs: 3
      }
    ]
  ],
  env: {
    test: {
      presets: [
        [
          '@babel/preset-env',
          {
            targets: {
              node: 'current'
            }
          }
        ]
      ],
      plugins: ['babel-plugin-dynamic-import-node']
    },
    production: {
      plugins: [
        ['transform-react-remove-prop-types', { removeImport: true }],
        '@babel/plugin-transform-react-constant-elements',
        '@babel/plugin-transform-react-inline-elements'
      ]
    }
  }
};
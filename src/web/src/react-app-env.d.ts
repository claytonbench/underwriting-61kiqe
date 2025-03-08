/// <reference types="react-scripts" />

// Declare module definitions for SVG files with React component support
declare module '*.svg' {
  import * as React from 'react';
  export const ReactComponent: React.FunctionComponent<React.SVGProps<SVGSVGElement>>;
  const src: string;
  export default src;
}

// Declare module definitions for various image formats
declare module '*.png' {
  const src: string;
  export default src;
}

declare module '*.jpg' {
  const src: string;
  export default src;
}

declare module '*.jpeg' {
  const src: string;
  export default src;
}

declare module '*.gif' {
  const src: string;
  export default src;
}

declare module '*.bmp' {
  const src: string;
  export default src;
}

// Declare module definitions for CSS files
declare module '*.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

// Declare module definitions for SCSS files
declare module '*.scss' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

// Declare module definitions for CSS modules
declare module '*.module.css' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

// Declare module definitions for SCSS modules
declare module '*.module.scss' {
  const classes: { readonly [key: string]: string };
  export default classes;
}

// Extend the NodeJS ProcessEnv interface to include our environment variables
declare namespace NodeJS {
  interface ProcessEnv {
    readonly NODE_ENV: 'development' | 'production' | 'test';
    readonly PUBLIC_URL: string;
    // Loan management system specific environment variables
    readonly REACT_APP_API_URL: string;
    readonly REACT_APP_AUTH0_DOMAIN: string;
    readonly REACT_APP_AUTH0_CLIENT_ID: string;
    readonly REACT_APP_AUTH0_AUDIENCE: string;
    readonly REACT_APP_DOCUSIGN_INTEGRATION_KEY: string;
    readonly REACT_APP_S3_DOCUMENT_BUCKET: string;
  }
}
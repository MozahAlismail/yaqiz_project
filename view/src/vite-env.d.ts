/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_URL: string;
}

interface ImportMeta {
  readonly env: ImportMetaEnv;
}

// Global type declarations for browser environment
// This makes NodeJS.Timeout compatible with browser timer APIs
declare namespace NodeJS {
  type Timeout = ReturnType<typeof setTimeout>;
}

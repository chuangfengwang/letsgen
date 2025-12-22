/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare module 'element-plus' {
  import type { App, Plugin } from 'vue'
  
  const ElementPlus: Plugin
  
  export default ElementPlus
}

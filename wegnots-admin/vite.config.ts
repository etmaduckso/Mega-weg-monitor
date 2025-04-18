import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Permite acesso a partir de qualquer endereço IP
    port: 5173,      // Porta padrão do Vite
    strictPort: true, // Garante que o servidor use especificamente esta porta
    cors: true       // Habilita CORS para permitir requisições de outros domínios
  },
})

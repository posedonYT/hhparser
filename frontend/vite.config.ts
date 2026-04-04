import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

const apiProxyTarget = process.env.API_PROXY_TARGET ?? 'http://localhost:8000';

function makeProxyOptions(target: string) {
  return {
    target,
    changeOrigin: true,
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    configure: (proxy: any) => {
      proxy.on('error', (_err: Error, _req: unknown, res: any) => {
        if (res && typeof res.writeHead === 'function' && !res.headersSent) {
          res.writeHead(503, { 'Content-Type': 'application/json' });
          res.end(
            JSON.stringify({
              detail: 'Backend сервис временно недоступен. Проверьте статус контейнера.'
            })
          );
        }
      });
    }
  };
}

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': makeProxyOptions(apiProxyTarget)
    }
  },
  preview: {
    proxy: {
      '/api': makeProxyOptions(apiProxyTarget)
    }
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts'
  }
});

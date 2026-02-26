import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import path from 'path';
import eslint from 'vite-plugin-eslint2';
import { viteStaticCopy } from 'vite-plugin-static-copy';
import svgLoader from 'vite-svg-loader';

const applicationNameShort = 'feewaiver';
const port = process.env.PORT ? parseInt(process.env.PORT) : 5173;
const host = process.env.HOST || '0.0.0.0';

export default defineConfig(({ command }) => ({
    base: `/static/${applicationNameShort}_vue/`,
    server: {
        host: host,
        port: port,
        strictPort: true,
        open: false,
        headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers':
                'Origin, X-Requested-With, Content-Type, Accept',
        },
        hmr: {
            protocol: 'ws',
            host: 'localhost',
            port: port,
        },
    },
    plugins: [
        vue(),
        eslint(),
        svgLoader({
            defaultImport: 'url',
        }),
        viteStaticCopy({
            targets: [
                { src: 'src/assets/*.png', dest: 'src' },
                {
                    src: 'node_modules/@fortawesome/fontawesome-free/webfonts',
                    dest: 'node_modules/@fortawesome/fontawesome-free/',
                },
            ],
        }),
    ],
    resolve: {
        alias: {
            '@': path.resolve(__dirname, './src'),
            '@vue-utils': path.resolve(__dirname, 'src/utils/vue'),
            '@common-utils': path.resolve(__dirname, 'src/components/common/'),
            '@assets': path.resolve(__dirname, 'src/assets'),
        },
    },
    esbuild: command === 'build' ? {
        drop: ['console', 'debugger'],
        minify: true,
    } : {},
    build: {
        manifest: 'manifest.json',
        commonjsOptions: { transformMixedEsModules: true },
        outDir: path.resolve(
            __dirname,
            `../../static/${applicationNameShort}_vue`
        ),
        sourcemap: false,
        rollupOptions: {
            input: {
                main: path.resolve(__dirname, 'src/main.js'),
            },
        },
        emptyOutDir: true,
    },
}));

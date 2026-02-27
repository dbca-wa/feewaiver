import pluginVue from 'eslint-plugin-vue';
import configPrettier from 'eslint-config-prettier';
import pluginPrettier from 'eslint-plugin-prettier';

export default [
    {
        ignores: ['dist/**', 'node_modules/**'],
    },
    ...pluginVue.configs['flat/recommended'],
    {
        plugins: {
            prettier: pluginPrettier,
        },
        rules: {
            ...configPrettier.rules,
            'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
            'vue/multi-word-component-names': 'off',
            'prettier/prettier': 'warn',
        },
        languageOptions: {
            globals: {
                window: 'readonly',
                document: 'readonly',
                console: 'readonly',
                process: 'readonly',
                $: 'readonly',
                jQuery: 'readonly',
            },
        },
    },
];

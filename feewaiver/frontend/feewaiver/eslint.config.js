import pluginVue from 'eslint-plugin-vue';

export default [
    {
        ignores: ['dist/**', 'node_modules/**'],
    },
    ...pluginVue.configs['flat/recommended'],
    {
        rules: {
            'no-debugger': process.env.NODE_ENV === 'production' ? 'error' : 'off',
            'vue/multi-word-component-names': 'off',
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

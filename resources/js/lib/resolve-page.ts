import type { ComponentType } from 'react';

type PageModule = { default: ComponentType };
const pages = import.meta.glob<PageModule>([
    '../pages/**/*.tsx',
    '../../../Modules/*/resources/js/pages/**/*.tsx',
]);

export async function resolvePage(name: string): Promise<ComponentType> {
    const parts = name.split('::');
    const key = parts.length === 2
        ? `../../../Modules/${parts[0]}/resources/js/pages/${parts[1]}.tsx`
        : `../pages/${name}.tsx`;
    const load = pages[key];
    if (!load) throw new Error(`Halaman Inertia tidak ditemukan: ${name}`);
    return (await load()).default;
}

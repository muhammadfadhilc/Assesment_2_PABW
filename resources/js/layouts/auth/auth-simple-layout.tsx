import { Link } from '@inertiajs/react';
import { Recycle } from 'lucide-react';
import type { PropsWithChildren } from 'react';
export default function AuthSimpleLayout({ children, title, description }: PropsWithChildren<{ name?: string; title?: string; description?: string }>) {
    return <div className="rh flex min-h-screen flex-col items-center justify-center bg-slate-50 p-6 text-slate-800"><div className="w-full max-w-md"><Link href="/" className="mb-8 flex items-center justify-center gap-3 text-2xl font-bold"><Recycle size={32} className="text-emerald-700"/>RecycleHub</Link><section className="rh-card"><h1 className="text-center text-2xl font-bold">{title}</h1><p className="mt-2 mb-7 text-center text-sm text-slate-500">{description}</p>{children}</section><p className="mt-6 text-center text-sm text-slate-500">Bank sampah kampus · SDG 12</p></div></div>;
}

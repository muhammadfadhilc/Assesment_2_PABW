import { Link, usePage } from '@inertiajs/react';
import { Recycle, LayoutDashboard, Library, PackageCheck, UserRound, LogOut } from 'lucide-react';
import type { ReactNode } from 'react';
import { useSharedProps } from '@/hooks/use-shared-props';
import type { BreadcrumbItem } from '@/types';

export default function AppLayout({ children }: { children: ReactNode; breadcrumbs?: BreadcrumbItem[] }) {
    const { user, isAdmin } = useSharedProps();
    const { url } = usePage();
    const menu = [
        { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { href: '/katalog', label: 'Katalog', icon: Library },
        { href: '/setoran', label: 'Setoran', icon: PackageCheck },
        { href: '/profil', label: 'Profil', icon: UserRound },
    ];
    return <div className="rh min-h-screen bg-slate-50 text-slate-800">
        <header className="border-b border-slate-200 bg-white">
            <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4 px-5 py-5 md:px-8">
                <Link href="/dashboard" className="flex items-center gap-3"><span className="rounded-xl bg-emerald-700 p-2.5 text-white"><Recycle size={25}/></span><div><p className="text-xl font-bold tracking-tight">RecycleHub</p><p className="text-sm text-slate-500">Bank sampah kampus</p></div></Link>
                <div className="flex items-center gap-4"><div className="text-right"><p className="font-semibold">{user.name}</p><p className="text-sm text-emerald-700">{isAdmin ? 'Admin' : 'Nasabah'}</p></div><Link href="/logout" method="post" as="button" className="rh-secondary flex items-center gap-2"><LogOut size={17}/><span>Logout</span></Link></div>
            </div>
            <nav aria-label="Navigasi utama" className="mx-auto flex max-w-7xl gap-1 overflow-x-auto px-5 md:px-8">{menu.map(({ href, label, icon: Icon }) => <Link key={href} href={href} aria-current={url.startsWith(href) ? 'page' : undefined} className={'flex shrink-0 items-center gap-2 border-b-2 px-4 py-3 text-sm font-semibold ' + (url.startsWith(href) ? 'border-emerald-700 text-emerald-800' : 'border-transparent text-slate-500 hover:text-emerald-700')}><Icon size={17}/>{label}</Link>)}</nav>
        </header>
        <main className="mx-auto max-w-7xl space-y-6 px-5 py-8 md:px-8 md:py-10">{children}</main>
        <footer className="mx-auto mt-8 flex max-w-7xl flex-wrap justify-between gap-2 border-t border-slate-200 px-5 py-6 text-sm text-slate-500 md:px-8"><span>RecycleHub · Simulasi pembelajaran dengan data fiktif</span><span>SDG 12 · Konsumsi dan produksi yang bertanggung jawab</span></footer>
    </div>;
}

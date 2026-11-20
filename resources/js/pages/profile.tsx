import { Head, Link } from '@inertiajs/react';
import AppLayout from '@/layouts/app-layout';
import { useSharedProps } from '@/hooks/use-shared-props';
import { PageTitle } from '@/components/recycle-ui';
export default function Profile() {
    const { user, isAdmin } = useSharedProps();
    return <AppLayout><Head title="Profil"/><PageTitle eyebrow="Akun saya" title="Profil pengguna" description="Identitas akun aktif di RecycleHub."/><section className="rh-card max-w-xl"><dl className="space-y-5">{[['Nama', user.name], ['Email', user.email], ['Role', isAdmin ? 'Admin' : 'Nasabah']].map(([label, value]) => <div key={label}><dt className="text-sm text-slate-500">{label}</dt><dd className="mt-1 font-semibold">{value}</dd></div>)}</dl><Link className="rh-secondary mt-6 inline-block" href="/settings/profile">Edit profil</Link></section></AppLayout>;
}

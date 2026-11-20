import { Head, Link } from '@inertiajs/react';
import { Library, Clock3, Scale, PackageCheck, Recycle } from 'lucide-react';
import AppLayout from '@/layouts/app-layout';
import { useSharedProps } from '@/hooks/use-shared-props';
import { PageTitle, Badge, angka, rupiah, tanggal, type Setoran } from '@/components/recycle-ui';
type Props = { totalKatalog: number; totalSetoran: number; totalMenunggu: number; beratDiverifikasi: string; items: Setoran[] };
export default function Dashboard({ totalKatalog, totalSetoran, totalMenunggu, beratDiverifikasi, items }: Props) {
    const { user, isAdmin } = useSharedProps();
    const cards = [
        { label: 'Jenis sampah', value: totalKatalog, icon: Library },
        { label: isAdmin ? 'Seluruh setoran' : 'Setoran saya', value: totalSetoran, icon: PackageCheck },
        { label: 'Menunggu keputusan', value: totalMenunggu, icon: Clock3 },
        { label: 'Berat diverifikasi', value: angka(beratDiverifikasi) + ' kg', icon: Scale },
    ];
    return <AppLayout><Head title="Dashboard"/><PageTitle eyebrow={isAdmin ? 'Ringkasan admin' : 'Ringkasan nasabah'} title={'Halo, ' + user.name.split(' ')[0] + '.'} description={isAdmin ? 'Pantau pemilahan sampah dan tinjau setoran yang masuk.' : 'Catat setoran terpilah Anda dan pantau hasil verifikasinya.'}><Link className="rh-primary" href={isAdmin ? '/setoran' : '/setoran/create'}>{isAdmin ? 'Tinjau setoran' : 'Buat setoran'}</Link></PageTitle>
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">{cards.map(({ label, value, icon: Icon }) => <section key={label} className="rh-card"><Icon size={22} className="mb-5 text-emerald-700"/><p className="text-sm text-slate-500">{label}</p><p className="mt-1 text-3xl font-bold">{value}</p></section>)}</div>
        <section className="flex items-start gap-4 rounded-2xl bg-emerald-900 p-6 text-white"><Recycle className="shrink-0" size={30}/><div><h2 className="text-lg font-semibold">Sampah terpilah, dampak terukur.</h2><p className="mt-1 text-emerald-100">Sebanyak {angka(beratDiverifikasi)} kg sampah {isAdmin ? 'kampus' : 'dari setoran Anda'} telah diverifikasi. Ringkasan SDG 12 hanya menghitung setoran yang berstatus Diverifikasi.</p></div></section>
        <section className="rh-card"><div className="mb-5 flex items-center justify-between"><h2 className="text-xl font-bold">{isAdmin ? 'Daftar setoran' : 'Setoran milik saya'}</h2><Link href="/setoran" className="font-semibold text-emerald-700">Kelola setoran</Link></div><div className="overflow-x-auto"><table className="rh-table"><thead><tr><th>Jenis sampah</th>{isAdmin && <th>Nasabah</th>}<th>Tanggal</th><th>Berat</th><th>Estimasi nilai</th><th>Status</th></tr></thead><tbody>{items.map(item => <tr key={item.id}><td>{item.jenis_sampah.nama_jenis}</td>{isAdmin && <td>{item.user.name}</td>}<td>{tanggal(item.tanggal_setor)}</td><td>{angka(item.berat_kg)} kg</td><td>{rupiah(item.total_nilai)}</td><td><Badge status={item.status}/></td></tr>)}</tbody></table>{!items.length && <p className="py-10 text-center text-slate-500">Belum ada setoran. Mulai dengan memilih jenis sampah di katalog.</p>}</div></section>
    </AppLayout>;
}

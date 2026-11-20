import { Head } from '@inertiajs/react';
import { useState, type FormEvent } from 'react';
import AppLayout from '@/layouts/app-layout';
import { useSharedProps } from '@/hooks/use-shared-props';
import { http, type ValidationErrors } from '@/lib/http';
import { Field, Notice, PageTitle, failure, rupiah, type Katalog } from '@/components/recycle-ui';

type Props = { items: Katalog[]; filters?: { q?: string; kategori?: string }; openForm?: boolean; editing?: Katalog };
export default function KatalogPage({ items: initial, filters = {}, openForm = false, editing }: Props) {
    const { isAdmin } = useSharedProps();
    const [items, setItems] = useState(initial);
    const [q, setQ] = useState(filters.q ?? '');
    const [kategori, setKategori] = useState(filters.kategori ?? '');
    const [formOpen, setFormOpen] = useState(openForm);
    const [edit, setEdit] = useState<Katalog | undefined>(editing);
    const [busy, setBusy] = useState(false);
    const [notice, setNotice] = useState('');
    const [error, setError] = useState('');
    const [errors, setErrors] = useState<ValidationErrors>({});
    async function refresh() {
        const result = await http<{ items: Katalog[] }>('/katalog?' + new URLSearchParams({ q, kategori }));
        setItems(result.items);
    }
    function handleError(e: unknown) { const f = failure(e); setError(f.message); setErrors(f.errors); }
    async function search(e: FormEvent) {
        e.preventDefault(); setBusy(true); setError(''); setErrors({});
        try { await refresh(); } catch (e) { handleError(e); } finally { setBusy(false); }
    }
    async function save(e: FormEvent<HTMLFormElement>) {
        e.preventDefault(); setBusy(true); setError(''); setErrors({}); setNotice('');
        const body = new FormData(e.currentTarget);
        if (edit) body.set('_method', 'PUT');
        try {
            const result = await http<{ message: string }>('/katalog' + (edit ? '/' + edit.id : ''), { method: 'POST', body });
            await refresh(); setFormOpen(false); setEdit(undefined); setNotice(result.message);
        } catch (e) { handleError(e); } finally { setBusy(false); }
    }
    async function remove(item: Katalog) {
        if (!window.confirm('Hapus jenis sampah ' + item.nama_jenis + '?')) return;
        setBusy(true); setError(''); setErrors({}); setNotice('');
        try { const r = await http<{ message: string }>('/katalog/' + item.id, { method: 'DELETE' }); await refresh(); setNotice(r.message); }
        catch (e) { handleError(e); } finally { setBusy(false); }
    }
    return <AppLayout><Head title="Katalog"/><PageTitle eyebrow="Pemilahan sampah" title="Katalog jenis sampah" description="Temukan jenis sampah yang diterima dan harga estimasi per kilogram.">{isAdmin && <button disabled={busy} className="rh-primary" onClick={() => { setEdit(undefined); setFormOpen(true); setErrors({}); setError(''); }}>Tambah jenis sampah</button>}</PageTitle>
        <Notice text={notice}/><Notice text={error} error/>{errors.katalog && <Notice text={errors.katalog.join(' ')} error/>}
        {formOpen && isAdmin && <section className="rh-card"><h2 className="mb-5 text-xl font-bold">{edit ? 'Edit jenis sampah' : 'Jenis sampah baru'}</h2><form key={edit?.id ?? 'new'} onSubmit={save} className="grid gap-5 sm:grid-cols-2"><fieldset disabled={busy} className="contents">
            <Field name="kode_jenis" label="Kode jenis *" errors={errors}><input className="rh-input" id="kode_jenis" name="kode_jenis" defaultValue={edit?.kode_jenis} placeholder="K001"/></Field>
            <Field name="nama_jenis" label="Nama jenis *" errors={errors}><input className="rh-input" id="nama_jenis" name="nama_jenis" defaultValue={edit?.nama_jenis} placeholder="Kertas HVS"/></Field>
            <Field name="kategori" label="Kategori *" errors={errors}><select className="rh-input" id="kategori" name="kategori" defaultValue={edit?.kategori ?? ''}><option value="">Pilih kategori</option>{['Kertas', 'Plastik', 'Logam'].map(c => <option key={c}>{c}</option>)}</select></Field>
            <Field name="harga_per_kg" label="Harga per kg (Rp) *" errors={errors}><input className="rh-input" id="harga_per_kg" name="harga_per_kg" type="number" step="0.01" defaultValue={edit?.harga_per_kg}/></Field>
            <div className="sm:col-span-2"><Field name="deskripsi" label="Deskripsi" errors={errors}><textarea className="rh-input" id="deskripsi" name="deskripsi" rows={3} defaultValue={edit?.deskripsi ?? ''}/></Field></div>
            <div className="flex gap-3 sm:col-span-2"><button className="rh-primary" type="submit">{busy ? 'Menyimpan…' : 'Simpan katalog'}</button><button type="button" className="rh-secondary" onClick={() => setFormOpen(false)}>Batal</button></div>
        </fieldset></form></section>}
        <section className="rh-card"><form onSubmit={search} className="mb-6 flex flex-wrap items-end gap-3"><div className="min-w-48 flex-1"><label htmlFor="search" className="mb-2 block text-sm font-semibold">Cari kode atau nama</label><input id="search" className="rh-input" placeholder="Contoh: K001 atau Kertas" value={q} onChange={e => setQ(e.target.value)}/></div><div><label htmlFor="filter" className="mb-2 block text-sm font-semibold">Kategori</label><select id="filter" className="rh-input" value={kategori} onChange={e => setKategori(e.target.value)}><option value="">Semua kategori</option>{['Kertas', 'Plastik', 'Logam'].map(c => <option key={c}>{c}</option>)}</select></div><button className="rh-primary" disabled={busy}>{busy ? 'Memuat…' : 'Terapkan'}</button></form>
        <div className="overflow-x-auto"><table className="rh-table"><thead><tr><th>Kode</th><th>Jenis sampah</th><th>Kategori</th><th>Harga / kg</th><th>Deskripsi</th>{isAdmin && <th>Aksi</th>}</tr></thead><tbody>{items.map(item => <tr key={item.id}><td className="font-mono text-sm">{item.kode_jenis}</td><td className="font-semibold">{item.nama_jenis}</td><td>{item.kategori}</td><td className="whitespace-nowrap">{rupiah(item.harga_per_kg)}</td><td className="min-w-48 text-slate-500">{item.deskripsi ?? '—'}</td>{isAdmin && <td><div className="flex gap-2"><button disabled={busy} className="rh-secondary" onClick={() => { setEdit(item); setFormOpen(true); setErrors({}); }}>Edit</button><button disabled={busy} className="rh-danger" onClick={() => remove(item)}>Hapus</button></div></td>}</tr>)}</tbody></table>{!items.length && <p className="py-12 text-center text-slate-500">Tidak ada jenis sampah yang sesuai pencarian.</p>}</div></section>
    </AppLayout>;
}

import { Head } from '@inertiajs/react';
import { useState, type FormEvent } from 'react';
import AppLayout from '@/layouts/app-layout';
import { useSharedProps } from '@/hooks/use-shared-props';
import { http, type ValidationErrors } from '@/lib/http';
import { Field, Notice, PageTitle, Badge, failure, rupiah, angka, tanggal, type Katalog, type Setoran } from '@/components/recycle-ui';
type Props = { items: Setoran[]; katalog: Katalog[]; openForm?: boolean; editing?: Setoran; detail?: Setoran };
export default function SetoranPage({ items: initial, katalog, openForm = false, editing, detail: initialDetail }: Props) {
    const { user, isAdmin } = useSharedProps();
    const [items, setItems] = useState(initial);
    const [formOpen, setFormOpen] = useState(openForm);
    const [edit, setEdit] = useState<Setoran | undefined>(editing);
    const [detail, setDetail] = useState<Setoran | undefined>(initialDetail);
    const [busy, setBusy] = useState(false);
    const [notice, setNotice] = useState('');
    const [error, setError] = useState('');
    const [errors, setErrors] = useState<ValidationErrors>({});
    const [jenis, setJenis] = useState(String(editing?.jenis_sampah_id ?? ''));
    const [berat, setBerat] = useState(editing?.berat_kg ?? '');
    const selected = katalog.find(k => String(k.id) === jenis);
    function handleError(e: unknown) { const f = failure(e); setError(f.message); setErrors(f.errors); }
    function replace(item: Setoran) { setItems(current => [item, ...current.filter(i => i.id !== item.id)].sort((a,b) => b.id - a.id)); if (detail?.id === item.id) setDetail(item); }
    async function reload() {
        setBusy(true); setError(''); setErrors({});
        try { const r = await http<{ items: Setoran[] }>('/setoran'); setItems(r.items); } catch (e) { handleError(e); } finally { setBusy(false); }
    }
    async function load(item: Setoran, mode: 'detail' | 'edit') {
        setBusy(true); setError(''); setErrors({});
        try {
            const r = await http<{ item: Setoran }>('/setoran/' + item.id + (mode === 'edit' ? '/edit' : ''));
            if (mode === 'detail') { setDetail(r.item); }
            else { setEdit(r.item); setJenis(String(r.item.jenis_sampah_id)); setBerat(r.item.berat_kg); setFormOpen(true); setDetail(undefined); }
        } catch (e) { handleError(e); } finally { setBusy(false); }
    }
    async function save(e: FormEvent<HTMLFormElement>) {
        e.preventDefault(); setBusy(true); setError(''); setErrors({}); setNotice('');
        const body = new FormData(e.currentTarget);
        if (edit) body.set('_method', 'PUT');
        try {
            const r = await http<{ item: Setoran; message: string }>('/setoran' + (edit ? '/' + edit.id : ''), { method: 'POST', body });
            replace(r.item); setFormOpen(false); setEdit(undefined); setNotice(r.message);
        } catch (e) { handleError(e); } finally { setBusy(false); }
    }
    async function decide(item: Setoran, status: 'Diverifikasi' | 'Ditolak') {
        if (!window.confirm('Tetapkan setoran #' + item.id + ' menjadi ' + status + '? Keputusan ini final.')) return;
        setBusy(true); setError(''); setErrors({}); setNotice('');
        const body = new FormData(); body.set('_method', 'PATCH'); body.set('status', status);
        try { const r = await http<{ item: Setoran; message: string }>('/setoran/' + item.id + '/keputusan', { method: 'POST', body }); replace(r.item); setNotice(r.message); }
        catch (e) { handleError(e); } finally { setBusy(false); }
    }
    async function remove(item: Setoran) {
        if (!window.confirm('Hapus setoran #' + item.id + ' beserta foto buktinya?')) return;
        setBusy(true); setError(''); setErrors({}); setNotice('');
        try {
            const r = await http<{ message: string }>('/setoran/' + item.id, { method: 'DELETE' });
            setItems(current => current.filter(i => i.id !== item.id));
            if (detail?.id === item.id) setDetail(undefined);
            if (edit?.id === item.id) { setEdit(undefined); setFormOpen(false); }
            setNotice(r.message);
        } catch (e) { handleError(e); } finally { setBusy(false); }
    }
    return <AppLayout><Head title="Setoran"/><PageTitle eyebrow={isAdmin ? 'Verifikasi bank sampah' : 'Kontribusi saya'} title={isAdmin ? 'Seluruh setoran' : 'Setoran sampah saya'} description={isAdmin ? 'Tinjau bukti, verifikasi setoran, atau tetapkan penolakan. Setiap keputusan bersifat final.' : 'Kelola setoran Anda selama berstatus Menunggu. Harga dan nilai dihitung oleh server.'}>{!isAdmin && <button disabled={busy} className="rh-primary" onClick={() => { setEdit(undefined); setJenis(''); setBerat(''); setFormOpen(true); setErrors({}); setError(''); setDetail(undefined); }}>Buat setoran</button>}</PageTitle>
        <Notice text={notice}/><Notice text={error} error/>{errors.status && <Notice text={errors.status.join(' ')} error/>}
        {formOpen && !isAdmin && <section className="rh-card"><h2 className="mb-5 text-xl font-bold">{edit ? 'Edit setoran #' + edit.id : 'Setoran baru'}</h2>{!katalog.length && <Notice text="Katalog masih kosong. Hubungi admin untuk menambahkan jenis sampah." error/>}<form key={edit?.id ?? 'new'} onSubmit={save} className="grid gap-5 sm:grid-cols-2"><fieldset disabled={busy} className="contents">
            <Field name="jenis_sampah_id" label="Jenis sampah *" errors={errors}><select id="jenis_sampah_id" name="jenis_sampah_id" className="rh-input" value={jenis} onChange={e => setJenis(e.target.value)}><option value="">Pilih dari katalog</option>{katalog.map(k => <option key={k.id} value={k.id}>{k.kode_jenis} · {k.nama_jenis} ({rupiah(k.harga_per_kg)}/kg)</option>)}</select></Field>
            <Field name="berat_kg" label="Berat (kg) *" errors={errors}><input id="berat_kg" name="berat_kg" type="number" step="0.01" className="rh-input" placeholder="2.50" value={berat} onChange={e => setBerat(e.target.value)}/></Field>
            <Field name="tanggal_setor" label="Tanggal setor *" errors={errors}><input id="tanggal_setor" name="tanggal_setor" type="date" className="rh-input" defaultValue={edit?.tanggal_setor.slice(0,10) ?? new Date().toLocaleDateString('en-CA')}/></Field>
            <Field name="foto_bukti" label="Foto bukti (opsional)" errors={errors}><input id="foto_bukti" name="foto_bukti" type="file" accept=".jpg,.jpeg,.png" className="rh-input"/><p className="text-sm text-slate-500">JPG/JPEG/PNG, maksimal 2 MB. {edit?.foto_bukti ? 'Tanpa foto baru, bukti lama tetap disimpan.' : ''}</p>{edit?.foto_url && <a href={edit.foto_url} target="_blank" rel="noreferrer" className="text-sm font-semibold text-emerald-700">Lihat Bukti lama</a>}</Field>
            <div className="sm:col-span-2"><Field name="catatan" label="Catatan setoran *" errors={errors}><textarea id="catatan" name="catatan" rows={3} className="rh-input" defaultValue={edit?.catatan} placeholder="Kondisi sampah, cara pemilahan, atau keterangan lain."/></Field></div>
            <div className="rounded-xl bg-emerald-50 p-4 sm:col-span-2"><p className="text-sm text-emerald-800">Estimasi nilai</p><p className="mt-1 text-2xl font-bold text-emerald-900">{rupiah(Number(berat || 0) * Number(selected?.harga_per_kg ?? 0))}</p><p className="mt-1 text-sm text-emerald-800">Nilai akhir dihitung server menggunakan harga katalog saat disimpan.</p></div>
            <div className="flex gap-3 sm:col-span-2"><button type="submit" className="rh-primary" disabled={!katalog.length}>{busy ? 'Menyimpan…' : 'Simpan setoran'}</button><button type="button" className="rh-secondary" onClick={() => setFormOpen(false)}>Batal</button></div>
        </fieldset></form></section>}
        {detail && <section className="rh-card"><div className="mb-5 flex items-center justify-between"><h2 className="text-xl font-bold">Detail setoran #{detail.id}</h2><button className="rh-secondary" onClick={() => setDetail(undefined)}>Tutup</button></div><dl className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">{[['Nasabah', detail.user.name], ['Jenis sampah', detail.jenis_sampah.kode_jenis + ' · ' + detail.jenis_sampah.nama_jenis], ['Kategori', detail.jenis_sampah.kategori], ['Tanggal', tanggal(detail.tanggal_setor)], ['Berat', angka(detail.berat_kg) + ' kg'], ['Harga saat setor', rupiah(detail.harga_saat_setor)], ['Total nilai', rupiah(detail.total_nilai)]].map(([label, value]) => <div key={label}><dt className="text-sm text-slate-500">{label}</dt><dd className="mt-1 font-semibold">{value}</dd></div>)}<div><dt className="mb-1 text-sm text-slate-500">Status</dt><dd><Badge status={detail.status}/></dd></div><div><dt className="mb-1 text-sm text-slate-500">Foto bukti</dt><dd>{detail.foto_url ? <a className="font-semibold text-emerald-700" target="_blank" rel="noreferrer" href={detail.foto_url}>Lihat Bukti</a> : 'Tidak ada foto'}</dd></div><div className="sm:col-span-2"><dt className="text-sm text-slate-500">Catatan</dt><dd className="mt-1 whitespace-pre-wrap">{detail.catatan}</dd></div></dl></section>}
        <section className="rh-card"><div className="mb-5 flex flex-wrap items-center justify-between gap-3"><h2 className="text-xl font-bold">Daftar transaksi <span className="text-base font-normal text-slate-500">({items.length})</span></h2><button className="rh-secondary" disabled={busy} onClick={reload}>{busy ? 'Memuat…' : 'Perbarui daftar'}</button></div><div className="overflow-x-auto"><table className="rh-table"><thead><tr><th>ID / Tanggal</th><th>Jenis sampah</th>{isAdmin && <th>Nasabah</th>}<th>Berat</th><th>Total nilai</th><th>Status</th><th>Aksi</th></tr></thead><tbody>{items.map(item => {
            const canEdit = !isAdmin && item.user_id === user.id && item.status === 'Menunggu';
            return <tr key={item.id}><td className="whitespace-nowrap"><span className="font-semibold">#{item.id}</span><p className="mt-1 text-sm text-slate-500">{tanggal(item.tanggal_setor)}</p></td><td className="font-semibold">{item.jenis_sampah.nama_jenis}</td>{isAdmin && <td>{item.user.name}</td>}<td className="whitespace-nowrap">{angka(item.berat_kg)} kg</td><td className="whitespace-nowrap">{rupiah(item.total_nilai)}</td><td><Badge status={item.status}/></td><td><div className="flex min-w-40 flex-wrap gap-2"><button disabled={busy} className="rh-secondary" onClick={() => load(item, 'detail')}>Detail</button>{item.foto_url && <a className="rh-secondary" href={item.foto_url} target="_blank" rel="noreferrer">Lihat Bukti</a>}{canEdit && <button disabled={busy} className="rh-secondary" onClick={() => load(item, 'edit')}>Edit</button>}{isAdmin && item.status === 'Menunggu' && <><button className="rh-primary" disabled={busy} onClick={() => decide(item, 'Diverifikasi')}>Verifikasi</button><button className="rh-danger" disabled={busy} onClick={() => decide(item, 'Ditolak')}>Tolak</button></>}{(isAdmin || canEdit) && <button className="rh-danger" disabled={busy} onClick={() => remove(item)}>Hapus</button>}</div></td></tr>;
        })}</tbody></table>{!items.length && <p className="py-12 text-center text-slate-500">Belum ada setoran {isAdmin ? 'yang masuk' : 'milik Anda'}.</p>}</div></section>
    </AppLayout>;
}

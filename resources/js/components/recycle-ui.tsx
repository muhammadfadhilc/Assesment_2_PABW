import type { ReactNode } from 'react';
import type { ValidationErrors } from '@/lib/http';
import { HttpError } from '@/lib/http';
export type Katalog = { id: number; kode_jenis: string; nama_jenis: string; kategori: string; harga_per_kg: string; deskripsi: string | null };
export type Setoran = { id: number; user_id: number; jenis_sampah_id: number; berat_kg: string; tanggal_setor: string; catatan: string; status: 'Menunggu' | 'Diverifikasi' | 'Ditolak'; harga_saat_setor: string; total_nilai: string; foto_bukti: string | null; foto_url: string | null; user: { id: number; name: string }; jenis_sampah: Katalog };
export const rupiah = (value: string | number) => new Intl.NumberFormat('id-ID', { style: 'currency', currency: 'IDR', minimumFractionDigits: 2 }).format(Number(value));
export const angka = (value: string | number) => new Intl.NumberFormat('id-ID', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).format(Number(value));
export const tanggal = (value: string) => new Date(value.slice(0, 10) + 'T12:00:00').toLocaleDateString('id-ID', { day: 'numeric', month: 'short', year: 'numeric' });
export function Badge({ status }: { status: Setoran['status'] }) {
    return <span className={'inline-flex rounded-full px-3 py-1 text-sm font-semibold ' + ({ Menunggu: 'bg-amber-50 text-amber-800', Diverifikasi: 'bg-emerald-50 text-emerald-800', Ditolak: 'bg-rose-50 text-rose-800' }[status])}>{status}</span>;
}
export function Field({ name, label, errors, children }: { name: string; label: string; errors: ValidationErrors; children: ReactNode }) {
    return <div className="space-y-2"><label htmlFor={name} className="block text-sm font-semibold">{label}</label>{children}{errors[name]?.map((e, i) => <p role="alert" key={i} className="text-sm text-rose-700">{e}</p>)}</div>;
}
export function Notice({ text, error = false }: { text: string; error?: boolean }) {
    if (!text) return null;
    return <div role={error ? 'alert' : 'status'} className={'rounded-xl border px-4 py-3 ' + (error ? 'border-rose-200 bg-rose-50 text-rose-800' : 'border-emerald-200 bg-emerald-50 text-emerald-800')}>{text}</div>;
}
export function failure(error: unknown): { message: string; errors: ValidationErrors } {
    if (error instanceof HttpError) {
        return { message: error.status === 403 ? 'Akses ditolak (403). Anda tidak berhak melakukan tindakan ini atau keputusan setoran sudah final.' : error.status === 419 ? 'Sesi kedaluwarsa. Muat ulang halaman dan masuk kembali.' : error.status === 422 ? 'Periksa isian yang ditandai. Data belum disimpan.' : error.status === 401 ? 'Sesi berakhir. Silakan login kembali.' : error.message, errors: error.data?.errors ?? {} };
    }
    return { message: 'Koneksi gagal. Periksa jaringan lalu coba lagi.', errors: {} };
}
export function PageTitle({ eyebrow, title, description, children }: { eyebrow: string; title: string; description: string; children?: ReactNode }) {
    return <div className="flex flex-wrap items-end justify-between gap-4"><div><p className="mb-2 text-sm font-semibold uppercase tracking-widest text-emerald-700">{eyebrow}</p><h1 className="text-3xl font-bold tracking-tight">{title}</h1><p className="mt-2 max-w-2xl text-slate-500">{description}</p></div>{children}</div>;
}

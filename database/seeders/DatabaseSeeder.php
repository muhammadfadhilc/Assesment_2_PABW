<?php
namespace Database\Seeders;
use App\Models\User;
use Illuminate\Database\Seeder;
use Modules\JenisSampah\Models\JenisSampah;
use Modules\Setoran\Models\Setoran;
use Modules\Setoran\Services\NilaiSetoran;
class DatabaseSeeder extends Seeder {
    public function run(): void {
        User::firstOrCreate(['email' => 'admin@recyclehub.test'], ['name' => 'Admin RecycleHub', 'password' => 'Recycle123!', 'role' => 'admin']);
        $users = [];
        foreach (['Nadia Fiktif', 'Bima Fiktif'] as $i => $name) {
            $users[] = User::firstOrCreate(['email' => 'nasabah'.($i + 1).'@recyclehub.test'], ['name' => $name, 'password' => 'Recycle123!', 'role' => 'nasabah']);
        }
        $catalog = [
            ['K001', 'Kertas HVS', 'Kertas', '3000.00', 'Kertas bersih dan kering, pisahkan dari plastik.'],
            ['K002', 'Kardus', 'Kertas', '2500.00', 'Lipat kardus dan pastikan tidak basah.'],
            ['P001', 'Botol PET', 'Plastik', '4000.00', 'Kosongkan dan bersihkan botol minuman.'],
            ['P002', 'Gelas plastik', 'Plastik', '2000.00', 'Pisahkan sedotan dan tutup gelas.'],
            ['L001', 'Kaleng aluminium', 'Logam', '9000.00', 'Bersihkan kaleng sebelum disetor.'],
        ];
        foreach ($catalog as [$code, $name, $category, $price, $description]) {
            JenisSampah::firstOrCreate(['kode_jenis' => $code], ['nama_jenis' => $name, 'kategori' => $category, 'harga_per_kg' => $price, 'deskripsi' => $description]);
        }
        foreach (['Menunggu', 'Diverifikasi', 'Ditolak'] as $i => $status) {
            $jenis = JenisSampah::where('kode_jenis', $catalog[$i][0])->firstOrFail();
            Setoran::firstOrCreate(['catatan' => 'Contoh setoran fiktif '.($i + 1)], [
                'user_id' => $users[$i % 2]->id, 'jenis_sampah_id' => $jenis->id,
                'berat_kg' => '2.50', 'tanggal_setor' => '2026-11-20', 'status' => $status,
                'harga_saat_setor' => $jenis->harga_per_kg, 'total_nilai' => NilaiSetoran::hitung('2.50', $jenis->harga_per_kg),
            ]);
        }
    }
}

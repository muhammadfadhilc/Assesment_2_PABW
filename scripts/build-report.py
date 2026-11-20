import json, re, textwrap, sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'output'/'pdf'
OUT.mkdir(parents=True,exist_ok=True)
PDF=OUT/'707012500122_Muhammad_Fadhil_AsesmenPraktikum2.1_PaketB.pdf'
W,H=595.28,841.89
M=54
INK=(.12,.18,.20); GREEN=(.02,.38,.29); GRAY=(.38,.43,.45)
pages=[]; annotations=[]
lower={'a':556,'b':556,'c':500,'d':556,'e':556,'f':278,'g':556,'h':556,'i':222,'j':222,'k':500,'l':222,'m':833,'n':556,'o':556,'p':556,'q':556,'r':333,'s':500,'t':278,'u':556,'v':500,'w':722,'x':500,'y':500,'z':500}
upper=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ',[667,667,722,722,667,611,778,722,278,500,667,556,833,722,778,667,778,722,667,611,722,667,944,667,667,611]))
punct={' ':278,'.':278,',':278,':':278,';':278,'!':278,'/':278,'-':333,'(':333,')':333,'[':278,']':278,"'":191,'"':355,'%':889,'&':667,'?':556,'=':584,'+':584,'_':556,'@':1015}
def width(s,size,font='F1'):
    if font=='F3': return len(s)*size*.6
    if font=='F2':
        boldlower=dict(zip('abcdefghijklmnopqrstuvwxyz',[556,611,556,611,556,333,611,611,278,278,556,278,889,611,611,611,611,389,556,333,611,556,778,556,556,500]))
        boldupper=dict(zip('ABCDEFGHIJKLMNOPQRSTUVWXYZ',[722,722,722,722,667,611,778,722,278,556,722,611,833,722,778,667,778,722,667,611,722,667,944,667,667,611]))
        return sum(boldlower.get(c,boldupper.get(c,punct.get(c,556))) for c in s)*size/1000
    return sum(lower.get(c,upper.get(c,punct.get(c,556))) for c in s)*size/1000*(1.055 if font=='F2' else 1)
def wrap(s,size=10.7,maxw=W-2*M,font='F1'):
    lines=[]; line=''
    for word in s.split():
        test=(line+' '+word).strip()
        if width(test,size,font)>maxw and line:
            lines.append(line); line=word
        else: line=test
    if line: lines.append(line)
    return lines or ['']
def txt(s):
    return '<'+s.encode('cp1252','replace').hex().upper()+'>'
class Page:
    def __init__(self,kicker,title,sub=None):
        self.cmd=[]; self.y=72; self.links=[]
        self.text('RECYCLEHUB  /  PABW',M,34,8,'F2',GREEN)
        self.text('MUHAMMAD FADHIL  |  707012500122',W-266,34,7.5,'F1',GRAY)
        self.line(M,46,W-M,46,(.83,.88,.86))
        self.text(kicker.upper(),M,self.y,9,'F2',GREEN); self.y+=28
        self.heading(title,23)
        if sub: self.para(sub,10.5,color=GRAY)
    def text(self,s,x,y,size=10.7,font='F1',color=INK):
        self.cmd.append(f'{color[0]} {color[1]} {color[2]} rg BT /{font} {size} Tf 1 0 0 1 {x:.2f} {H-y:.2f} Tm {txt(s)} Tj ET')
    def line(self,x1,y1,x2,y2,c):
        self.cmd.append(f'{c[0]} {c[1]} {c[2]} RG .7 w {x1} {H-y1} m {x2} {H-y2} l S')
    def rect(self,x,y,w,h,c):
        self.cmd.append(f'{c[0]} {c[1]} {c[2]} rg {x} {H-y-h} {w} {h} re f')
    def heading(self,s,size=14):
        for line in wrap(s,size,font='F2'):
            self.text(line,M,self.y,size,'F2'); self.y+=size*1.25
        self.y+=7
    def para(self,s,size=10.7,color=INK):
        for line in wrap(s,size):
            self.text(line,M,self.y,size,'F1',color); self.y+=size*1.48
        self.y+=7
    def bullet(self,s):
        ls=wrap(s,10.4,W-2*M-14)
        self.text('-',M,self.y,10.4,'F2',GREEN)
        for line in ls:
            self.text(line,M+14,self.y,10.4); self.y+=15.3
        self.y+=5
    def code(self,label,code):
        self.para(label,8.2,GRAY)
        ls=[]
        for l in code.strip('\n').splitlines():
            ls.extend(textwrap.wrap(l,96,replace_whitespace=False,drop_whitespace=False) or [''])
        height=11.5*len(ls)+15
        self.rect(M-1,self.y-11,W-2*M+2,height,(.945,.96,.955))
        for line in ls:
            self.text(line,M+9,self.y,8.1,'F3'); self.y+=11.5
        self.y+=15
    def evidence(self,s):
        self.y+=10
        self.line(M,self.y-14,W-M,self.y-14,(.80,.87,.83))
        self.para('Bukti visual yang masih perlu dilengkapi',9.2,GREEN)
        self.para(s,9.3,GRAY)
    def finish(self):
        if self.y>766: raise RuntimeError(f'Page overflow {len(pages)+1}: {self.y}')
        n=len(pages)+1
        self.line(M,784,W-M,784,(.83,.88,.86))
        self.text('Asesmen Praktikum 2.1 - Paket B - Jalur 2',M,802,8,'F1',GRAY)
        self.text(str(n).zfill(2),W-M-14,802,9,'F2',GREEN)
        pages.append('\n'.join(self.cmd)); annotations.append(self.links)

def snippet(file,start,stop=None):
    lines=(ROOT/file).read_text(encoding='utf-8-sig').splitlines()
    a=next(i for i,l in enumerate(lines) if start in l)
    b=next((i for i in range(a+1,len(lines)) if stop and stop in lines[i]),min(a+8,len(lines))) if stop else min(a+8,len(lines))
    return '\n'.join(lines[a:b])

p=Page('Laporan praktikum','RecycleHub','Bank sampah kampus | SDG 12: Konsumsi dan Produksi yang Bertanggung Jawab')
p.y+=20
for label,value in [('Nama','Muhammad Fadhil'),('NIM / NRP','707012500122'),('Kelas','Belum dicantumkan'),('Paket','B - NIM genap'),('Jalur','2 - Laravel HMVC, React, Inertia.js'),('Tanggal asesmen','20 November 2026')]:
    p.text(label,M,p.y,10,'F1',GRAY); p.text(value,M+125,p.y,11,'F2'); p.y+=29
p.y+=16
p.heading('Repository',13)
url='https://github.com/muhammadfadhilc/Assesment_2_PABW'
p.para(url,9.4,GREEN)
p.links.append((M,H-p.y+9,W-M,H-p.y+36,url))
p.y+=12
p.heading('Tentang aplikasi',13)
p.para('RecycleHub membantu bank sampah kampus mencatat jenis sampah dan setoran nasabah. Admin mengelola katalog serta mengambil keputusan, sedangkan nasabah mencatat setoran miliknya. Seluruh data uji menggunakan identitas fiktif.')
p.heading('Status naskah',13)
p.para('Source code, migration, Seeder, pengujian otomatis, dan pemeriksaan HTTP telah disiapkan. Naskah ini masih berupa draf laporan: screenshot aplikasi, pemeriksaan tampilan mobile, kelas, serta akses repository perlu dilengkapi sebelum pengumpulan.',10.5)
p.finish()

p=Page('Soal 1 / 10 poin','Project Laravel dan HMVC')
p.para('Saya menggunakan proyek SmartFacility sebagai acuan, lalu mengganti fitur aktifnya menjadi JenisSampah dan Setoran. Modul lama dinonaktifkan agar route dan migration-nya tidak ikut dimuat. Database aplikasi menggunakan MySQL dengan nama recyclehub.')
p.code('Perintah yang dijalankan dari folder aplikasi',"""composer dump-autoload --no-interaction
php scripts/create-database.php
php artisan config:clear
php artisan migrate --seed --force
php artisan module:list
php artisan route:list --except-vendor
npm run build""")
p.code('.env.example - konfigurasi yang boleh dicantumkan',"""APP_NAME="RecycleHub"
APP_URL=http://127.0.0.1:8000
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=recyclehub
DB_USERNAME=root
DB_PASSWORD=""")
p.para('Versi yang digunakan: PHP 8.3.33, Laravel 12.72.0, nwidart/laravel-modules 12.0.5, inertia-laravel 2.0.28, React 19.2.x, dan Tailwind CSS 4.x. Kunci aplikasi disimpan di .env dan tidak dicantumkan dalam laporan.')
p.code('Struktur yang sama dipakai pada kedua modul',"""Modules/JenisSampah/              Modules/Setoran/
  app/Models/                     app/Models/
  app/Http/Controllers/           app/Http/Controllers/
  app/Http/Requests/              app/Http/Requests/
  app/Providers/                  app/Providers/
  database/migrations/            database/migrations/
  resources/js/pages/index.tsx    resources/js/pages/index.tsx
  routes/web.php                  routes/web.php""")
p.para('HMVC dipilih supaya perubahan katalog dan transaksi tidak menumpuk di satu controller. Setiap modul membawa model, validasi, route, dan antarmukanya sendiri. Autentikasi serta layout tetap digunakan bersama.',10.3)
p.evidence('Tambahkan hasil module:list, route kedua modul, dan satu halaman aplikasi yang berhasil dibuka.')
p.finish()

p=Page('Soal 2 / 15 poin','Autentikasi dan dashboard')
p.para('Login, registrasi, dan logout menggunakan autentikasi sesi Laravel Fortify. Halaman dashboard hanya dapat dibuka setelah login. Password disimpan melalui cast hashed pada model User.')
p.code('database/migrations/2025_11_01_000001_add_role_to_users_table.php',"$table->enum('role', ['admin', 'nasabah'])->default('nasabah');")
p.code('app/Actions/Fortify/CreateNewUser.php - payload role tidak dipakai',"""return User::create([
    'name' => $input['name'],
    'email' => $input['email'],
    'password' => $input['password'],
    'role' => UserRole::Nasabah,
]);""")
p.para('Seeder membuat satu admin dan dua nasabah fiktif. Password uji ketiganya adalah Recycle123!. Data contoh ini dipakai untuk membandingkan akses pemilik dan akun lain.')
p.bullet('Admin: admin@recyclehub.test')
p.bullet('Nasabah 1: nasabah1@recyclehub.test (Nadia Fiktif)')
p.bullet('Nasabah 2: nasabah2@recyclehub.test (Bima Fiktif)')
p.code('app/Http/Controllers/DashboardController.php - ringkasan dari Eloquent',"""'totalKatalog' => JenisSampah::count(),
'totalSetoran' => (clone $query)->count(),
'totalMenunggu' => (clone $query)->where('status', 'Menunggu')->count(),
'beratDiverifikasi' =>
    (clone $query)->where('status', 'Diverifikasi')->sum('berat_kg'),""")
p.para('Query dashboard nasabah dibatasi dengan user_id akun aktif. Pada data awal, admin melihat lima katalog, tiga setoran, satu Menunggu, dan berat terverifikasi 2,50 kg. Nasabah 1 memiliki dua setoran, sedangkan nasabah 2 memiliki satu setoran.')
p.para('Uji registrasi dengan role=admin tetap menghasilkan nasabah. Uji login/logout juga lulus; setelah logout, permintaan dashboard melalui browser diarahkan ke login, sedangkan permintaan JSON memperoleh HTTP 401.',10.4)
p.evidence('Tambahkan dashboard kedua role serta bukti akses /dashboard setelah logout.')
p.finish()

p=Page('Soal 3 / 15 poin','Middleware dan otorisasi')
p.para('Pembatasan akses dilakukan di server. Menyembunyikan tombol hanya membantu pengguna memahami tindakan yang tersedia; URL dan request buatan sendiri tetap diperiksa.')
p.code('bootstrap/app.php dan route modul',"""$middleware->alias(['role' => EnsureUserHasRole::class]);

Route::middleware('auth')->group(function () {
    // Seluruh halaman dan endpoint fitur.
});
Route::middleware('role:admin')->group(function () {
    // Mutasi katalog hanya untuk admin.
});""")
p.code('Modules/Setoran/app/Http/Requests/SetoranRequest.php',snippet('Modules/Setoran/app/Http/Requests/SetoranRequest.php','public function authorize()', 'public function rules()'))
p.code('Modules/Setoran/app/Http/Controllers/SetoranController.php',snippet('Modules/Setoran/app/Http/Controllers/SetoranController.php','private function authorizeItem','private function items'))
p.para('Pada daftar dan dashboard, nasabah hanya menerima record dengan user_id miliknya. Pada detail, edit, update, dan delete, server memeriksa pemilik record lagi. Nasabah juga harus berada pada status Menunggu untuk mengubah atau menghapus transaksi.')
p.para('Keputusan admin memiliki route khusus dengan middleware role:admin dan Form Request tersendiri. Saat menyimpan keputusan, row dikunci menggunakan lockForUpdate lalu status diperiksa ulang. Request yang datang setelah keputusan final ditolak.')
p.para('Hasil uji: nasabah kedua mendapat 403 ketika mencoba detail/edit/update/delete setoran nasabah pertama. Nasabah juga mendapat 403 ketika mencoba mutasi katalog atau keputusan admin. Data semula tetap ada.',10.4)
p.evidence('Tambahkan minimal dua bukti 403, misalnya akses detail akun lain dan request mutasi katalog dari nasabah.')
p.finish()

p=Page('Soal 4 / 15 poin','CRUD katalog jenis sampah')
p.para('Katalog menyimpan kode, nama, kategori, harga per kg, dan deskripsi. Kode dibuat unik pada database sehingga pemeriksaan tidak hanya bergantung pada form.')
p.code('Modules/JenisSampah/database/migrations/2026_11_20_000001_create_jenis_sampahs_table.php',"""$table->id();
$table->string('kode_jenis')->unique();
$table->string('nama_jenis');
$table->string('kategori');
$table->decimal('harga_per_kg', 12, 2);
$table->text('deskripsi')->nullable();
$table->timestamps();""")
p.para('Admin mempunyai route index, create, store, edit, update, dan destroy. Nasabah hanya membaca katalog. Lima data awal adalah Kertas HVS, Kardus, Botol PET, Gelas plastik, dan Kaleng aluminium.')
p.code('Modules/JenisSampah/app/Http/Requests/JenisSampahRequest.php',"""'kode_jenis' => ['required', 'string', 'max:255',
    Rule::unique('jenis_sampahs')->ignore($this->route('jenis_sampah'))],
'nama_jenis' => ['required', 'string', 'max:255'],
'kategori' => ['required', Rule::in(['Kertas', 'Plastik', 'Logam'])],
'harga_per_kg' => ['required', 'numeric', 'gt:0',
    'decimal:0,2', 'max:9999999999.99'],
'deskripsi' => ['nullable', 'string'],""")
p.para('Pencarian kode atau nama dikelompokkan dalam satu kondisi OR, kemudian digabung dengan filter kategori menggunakan AND. Kata kunci kosong tidak menambahkan kondisi pencarian sehingga daftar tetap mengikuti kategori yang dipilih.')
p.code('Controller JenisSampah - penolakan hapus katalog terpakai',"""if ($item->setorans()->exists()) {
    throw ValidationException::withMessages([
        'katalog' => 'Jenis sampah sudah digunakan dalam setoran dan tidak dapat dihapus.'
    ]);
}
$item->delete();""")
p.para('Selain pemeriksaan controller, foreign key setoran memakai RESTRICT. Saat harga katalog berubah, controller katalog tidak memperbarui kolom harga_saat_setor atau total_nilai pada setoran lama.',10.4)
p.evidence('Tambahkan tabel katalog, form tambah/edit, pencarian beserta kategori, dan pesan penolakan hapus katalog terpakai.')
p.finish()

p=Page('Soal 5 / 20 poin','Relasi dan perhitungan setoran')
p.para('Setiap setoran dimiliki satu nasabah dan menunjuk satu jenis sampah. Satu nasabah dapat memiliki banyak setoran; satu jenis sampah juga dapat digunakan dalam banyak setoran.')
p.code('Relasi model User, JenisSampah, dan Setoran',"""// app/Models/User.php
return $this->hasMany(\\Modules\\Setoran\\Models\\Setoran::class);
// Modules/JenisSampah/app/Models/JenisSampah.php
return $this->hasMany(Setoran::class);
// Modules/Setoran/app/Models/Setoran.php
return $this->belongsTo(User::class);
return $this->belongsTo(JenisSampah::class);""")
p.code('Migration Setoran - potongan skema',"""$table->foreignId('user_id')->constrained()->restrictOnDelete();
$table->foreignId('jenis_sampah_id')
    ->constrained('jenis_sampahs')->restrictOnDelete();
$table->decimal('berat_kg', 8, 2);
$table->date('tanggal_setor');
$table->text('catatan');
$table->enum('status', ['Menunggu', 'Diverifikasi', 'Ditolak'])
    ->default('Menunggu');
$table->string('foto_bukti')->nullable();
$table->decimal('harga_saat_setor', 12, 2);
$table->decimal('total_nilai', 14, 2);""")
p.code('SetoranController - harga dan nilai ditentukan ulang di server',"""$data = $request->safe()->except('foto_bukti');
$jenis = JenisSampah::lockForUpdate()
    ->findOrFail($data['jenis_sampah_id']);
$data['harga_saat_setor'] = $jenis->harga_per_kg;
$data['total_nilai'] = NilaiSetoran::hitung(
    (string) $data['berat_kg'], $jenis->harga_per_kg);
if (!$setoran) {
    $data['user_id'] = $request->user()->id;
    $data['status'] = 'Menunggu';
}""")
p.para('Hasil uji K001: 2,50 kg x Rp3.000,00 = Rp7.500,00. Setelah katalog menjadi Rp4.000,00, nilai setoran lama tetap Rp7.500,00. Ketika nasabah mengeditnya saat Menunggu, harga diambil ulang sehingga nilai menjadi Rp10.000,00. Payload harga dan total palsu tidak digunakan.',10.4)
p.evidence('Tambahkan bukti nilai awal, harga katalog berubah, dan hasil hitung ulang setelah edit.')
p.finish()

p=Page('Soal 5 / lanjutan','AJAX, upload, dan keputusan final')
p.para('Halaman dibuka melalui Inertia. Operasi transaksi kemudian memakai fetch dan FormData agar hasilnya dapat diproses tanpa memuat ulang seluruh halaman.')
p.code('Modules/Setoran/resources/js/pages/index.tsx - pengiriman form',"""const body = new FormData(e.currentTarget);
if (edit) body.set('_method', 'PUT');
const r = await http('/setoran' + (edit ? '/' + edit.id : ''), {
    method: 'POST', body
});
replace(r.item);
setFormOpen(false);
setNotice(r.message);""")
p.code('resources/js/lib/http.ts - bagian penting request',"""const response = await fetch(url, {
    method, body, credentials: 'same-origin',
    headers: {
        Accept: 'application/json',
        'X-Requested-With': 'XMLHttpRequest',
        'X-XSRF-TOKEN': getXsrfToken(),
    },
});""")
p.para('FormData membawa field biasa dan file dalam satu request. Content-Type tidak diatur manual supaya browser menyertakan boundary multipart dengan benar. Foto opsional harus JPG/JPEG/PNG, maksimal 2 MB.')
p.code('SetoranController - menyimpan path relatif di disk public',"""if ($request->hasFile('foto_bukti')) {
    $oldPath = $item->foto_bukti;
    $newPath = $request->file('foto_bukti')->store('setoran', 'public');
    $data['foto_bukti'] = $newPath;
}
// Setelah commit berhasil:
if ($oldPath) { Storage::disk('public')->delete($oldPath); }""")
p.para('Jika edit tidak membawa foto baru, path lama tidak diganti. Jika transaksi database gagal, file baru dibersihkan. Penghapusan setoran juga menghapus file setelah record berhasil dihapus.')
p.para('Admin hanya dapat menetapkan Diverifikasi atau Ditolak dari Menunggu. Keputusan final tidak bisa dikembalikan. Nasabah tidak diberi route keputusan, dan admin tidak diberi hak membuat atau mengubah isi setoran.')
p.evidence('Tambahkan daftar admin dengan nama pengirim, detail/Lihat Bukti, keputusan admin, serta satu request edit setoran final yang ditolak.')
p.finish()

p=Page('Soal 6 / 10 poin','Layout utama dan navigasi')
p.para('Dashboard, katalog, dan transaksi memakai layout React yang sama. Header menampilkan nama aplikasi dan pengguna aktif. Di bawahnya terdapat menu Dashboard, Katalog, Setoran, dan Profil; Logout dikirim menggunakan POST.')
p.code('resources/js/layouts/app-layout.tsx - susunan menu',"""const menu = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/katalog', label: 'Katalog', icon: Library },
    { href: '/setoran', label: 'Setoran', icon: PackageCheck },
    { href: '/profil', label: 'Profil', icon: UserRound },
];
<Link href="/logout" method="post" as="button">Logout</Link>""")
p.code('Layout bersama - penanda menu aktif',"""aria-current={url.startsWith(href) ? 'page' : undefined}
// Warna teks dan garis bawah mengikuti URL halaman aktif.
<main className="mx-auto max-w-7xl ...">{children}</main>
// Footer: simulasi pembelajaran, data fiktif, dan SDG 12.""")
p.para('Menu fitur utama tersedia bagi kedua role karena katalog dan daftar setoran sama-sama perlu dibaca. Tombol di dalam halaman yang dibedakan: admin melihat tambah/edit/hapus katalog dan keputusan setoran; nasabah melihat buat serta edit/hapus miliknya yang Menunggu.')
p.para('Profil menampilkan nama, email, dan role akun aktif dari props autentikasi. Pengguna tidak memilih identitas melalui parameter URL sehingga halaman ini tetap mengacu pada sesi login.')
p.code('resources/js/pages/profile.tsx - data profil',"""const { user, isAdmin } = useSharedProps();
[['Nama', user.name],
 ['Email', user.email],
 ['Role', isAdmin ? 'Admin' : 'Nasabah']]""")
p.para('Warna hijau dipakai untuk tindakan utama dan status Diverifikasi. Menunggu menggunakan warna kuning, sedangkan Ditolak dan tindakan hapus menggunakan merah. Nama status tetap ditulis supaya maknanya tidak bergantung pada warna saja.')
p.evidence('Tambahkan minimal dua halaman dengan header/footer yang sama, menu aktif yang berbeda, dan halaman Profil.')
p.finish()

p=Page('Soal 7 / 10 poin','Validasi dan umpan balik')
p.para('Validasi katalog dan transaksi menggunakan Form Request. Keputusan admin mempunyai KeputusanRequest tersendiri supaya endpoint keputusan hanya menerima nilai yang memang boleh ditetapkan admin.')
p.code('Modules/Setoran/app/Http/Requests/SetoranRequest.php',"""'jenis_sampah_id' => ['required', 'integer', 'exists:jenis_sampahs,id'],
'berat_kg' => ['required', 'numeric', 'gt:0',
    'decimal:0,2', 'max:999999.99'],
'tanggal_setor' => ['required', 'date_format:Y-m-d'],
'catatan' => ['required', 'string'],
'foto_bukti' => ['nullable', 'image', 'mimes:jpg,jpeg,png',
    'extensions:jpg,jpeg,png', 'max:2048'],""")
p.para('Jika server mengembalikan 422, helper mengambil errors dari JSON dan menampilkannya di field yang sesuai. Form tidak direset sehingga pengguna cukup memperbaiki bagian yang salah. Respons 403 menampilkan pesan akses ditolak, bukan pesan kesalahan isian.')
p.code('resources/js/components/recycle-ui.tsx dan halaman transaksi',"""// 422: errors berisi nama field dan daftar pesannya.
setErrors(f.errors);
setError(f.message);
// Saat sukses:
replace(r.item);
setNotice(r.message);
// Selalu pulihkan tombol.
finally { setBusy(false); }""")
p.heading('Contoh aturan lintas field',13)
p.para('Berat 999999,99 dan harga 9999999999,99 masing-masing masih sesuai kapasitas kolomnya, tetapi hasil perkalian melampaui decimal(14,2) pada total_nilai. Server menolak kombinasi ini dengan 422 pada berat_kg. Transaksi database memastikan nilai lama tidak berubah jika kegagalan terjadi saat update.')
p.code('Modules/Setoran/app/Services/NilaiSetoran.php',"""$total = bcadd(bcmul($berat, $harga, 4), '0.005', 2);
if (bccomp($total, '999999999999.99', 2) > 0) {
    throw ValidationException::withMessages([
        'berat_kg' => 'Berat dan harga menghasilkan total melebihi batas transaksi. Kurangi berat setoran.'
    ]);
}""")
p.evidence('Tambahkan error per field, pesan sukses, dan uji kombinasi berat/harga yang ditolak tanpa perubahan database.')
p.finish()

p=Page('Soal 8 / 5 poin','Antarmuka dan interaksi')
p.para('Antarmuka memakai komponen yang konsisten untuk form, tabel, tombol, badge, dan notifikasi. Layout tidak hanya mengecilkan tulisan ketika layar sempit; kartu dirapikan menjadi satu kolom dan tabel tetap bisa digeser.')
p.code('resources/css/app.css dan komponen halaman',"""// Tabel dibungkus container horizontal.
<div className="overflow-x-auto">
    <table className="rh-table">...</table>
</div>
// Kartu dashboard:
className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4"
// Form:
<fieldset disabled={busy} className="contents">...</fieldset>""")
p.para('State busy mencegah tombol dipakai berulang selama request. Label tombol berubah menjadi Menyimpan... atau Memuat..., lalu dipulihkan melalui finally, baik request berhasil maupun gagal. Daftar kosong juga diberi pesan agar tidak terlihat seperti halaman rusak.')
p.heading('Pemeriksaan yang sudah dilakukan',13)
p.bullet('TypeScript lolos pemeriksaan tipe dengan npm run types.')
p.bullet('Aset produksi berhasil dibangun dengan npm run build.')
p.bullet('Endpoint halaman dan transaksi diuji melalui HTTP dengan cookie sesi serta token CSRF yang sebenarnya.')
p.heading('Pemeriksaan visual yang belum selesai',13)
p.para('Rancangan responsif sudah ada pada source, tetapi tampilan desktop dan smartphone belum dapat dipastikan melalui browser otomatis. Computer Use berhenti karena URL Chrome tidak dapat dikenali dengan cukup yakin. Karena itu, laporan ini belum menyertakan screenshot aplikasi.')
p.para('Sebelum pengumpulan, buka dashboard, katalog, dan transaksi pada laptop. Kemudian periksa mode perangkat berukuran sekitar 390 px: pastikan menu bisa dipakai, form terbaca, tabel dapat digeser, dan notifikasi tidak terpotong. Gunakan throttling Network untuk menangkap keadaan tombol nonaktif.')
p.evidence('Tambahkan screenshot desktop, tampilan mobile, dan keadaan tombol ketika request berlangsung. Bagian ini belum dianggap selesai hanya berdasarkan source CSS.')
p.finish()

p=Page('Hasil uji dan kesimpulan','Pemeriksaan implementasi')
p.para('Pengujian menggunakan database terpisah agar tidak mengganggu data contoh aplikasi. Suite otomatis berjalan pada SQLite in-memory dan MySQL recyclehub_testing.')
p.code('Perintah dan hasil verifikasi',"""php artisan test --compact
20 tests passed, 182 assertions
# Hasil sama pada SQLite dan database MySQL pengujian.

npm run types
# Lulus tanpa kesalahan TypeScript.

npm run build
# Build produksi berhasil.

node scripts/smoke-http.mjs
# Sesi MySQL, Inertia, CSRF 419, validasi 422, akses 403: lulus.

composer validate --no-check-publish
# composer.json is valid""")
p.para('Kasus yang diperiksa meliputi role palsu saat registrasi, password hash, login/logout, isolasi dua nasabah, larangan admin membuat/mengedit setoran, keputusan final, harga historis, total palsu, katalog terpakai, pembulatan, validasi file, serta penggantian dan pembersihan foto.')
p.para('Pemeriksaan HTTP juga memastikan token CSRF dipakai pada request nyata. Tanpa token, request ditolak dengan 419. Dengan token tetapi isian tidak lengkap, server mengembalikan 422. Percobaan mutasi yang tidak berwenang mendapat 403.')
p.heading('Kesimpulan',13)
p.para('RecycleHub sudah memisahkan pengelolaan katalog dan setoran ke dalam dua modul. Pembatasan role, kepemilikan, status, dan perhitungan nilai dijalankan pada backend. Antarmuka menerima hasil dari server melalui AJAX sehingga perubahan transaksi langsung tercermin pada daftar.')
p.para('Pengujian otomatis dan HTTP sudah lulus. Pemeriksaan instalasi dari clone repository, akses GitHub untuk dosen, screenshot desktop/mobile, serta pengecekan PDF akhir tetap harus diselesaikan sebelum pengumpulan. Koneksi ke GitHub dari lingkungan ini gagal, sehingga akses repository belum dapat dinyatakan terverifikasi.',10.4)
p.finish()

p=Page('Refleksi wajib / 1-3','Alur data dan keamanan')
p.heading('1. Alur data kedua modul dan relasi tiga tabel',13)
p.para('Saya memisahkan data jenis sampah ke modul JenisSampah dan transaksi ke modul Setoran. Admin mengisi katalog lebih dulu. Saat nasabah membuat setoran, pilihan jenis sampah diambil dari katalog itu, lalu server membaca harga per kilogramnya dan menyimpan salinan harga pada transaksi.')
p.para('Tabel users berelasi satu-ke-banyak dengan setorans melalui user_id. Tabel jenis_sampahs juga berelasi satu-ke-banyak dengan setorans melalui jenis_sampah_id. Jadi satu nasabah bisa punya banyak setoran, tetapi setiap setoran hanya mempunyai satu pemilik dan satu jenis sampah. Harga disalin agar perubahan katalog tidak mengubah riwayat transaksi.')
p.heading('2. Mencegah akses akun lain dan keputusan palsu',13)
p.para('Server mengambil pengguna dari sesi login, bukan dari user_id kiriman browser. Daftar setoran nasabah dibatasi berdasarkan ID akun aktif. Untuk detail, edit, update, dan delete, server memeriksa pemilik record lagi. Dengan begitu, mengganti ID pada URL tidak membuat nasabah bisa membuka setoran orang lain.')
p.para('Keputusan admin memakai endpoint tersendiri yang dilindungi middleware role dan Form Request. Payload status pada form setoran nasabah tidak dipakai. Ketika keputusan disimpan, row dikunci lalu status Menunggu diperiksa ulang. Jika sudah final, request berikutnya ditolak dengan 403.')
p.heading('3. Mengapa backend tetap memeriksa aturan dan nilai?',13)
p.para('Batas input pada form bisa dilewati, misalnya lewat DevTools atau request buatan sendiri. Karena itu, nilai uang, role, pemilik, dan status tidak boleh dipercaya hanya karena tampil benar di browser. Backend harus memvalidasi data dan mengambil harga langsung dari database.')
p.para('Pemeriksaan ulang juga penting ketika keadaan berubah setelah form dibuka. Harga katalog mungkin sudah diperbarui atau admin sudah mengambil keputusan. Lock dan transaksi database menjaga supaya request lama tidak menimpa keadaan terbaru. Untuk uang, perhitungan desimal mencegah selisih pembulatan yang dapat muncul dari floating point.')
p.finish()

p=Page('Refleksi wajib / 4-6','AJAX, SDGs, dan kendala')
p.heading('4. AJAX, FormData, 422, dan state React',13)
p.para('Saat tombol simpan ditekan, React membentuk FormData dari isian dan foto, lalu fetch mengirimkannya beserta token CSRF. Server memeriksa request, menyimpan data yang sah, dan mengembalikan JSON. Setelah berhasil, state daftar diperbarui menggunakan record dari server sehingga halaman tidak perlu dimuat ulang.')
p.para('Jika responsnya 422, React mengambil pesan per field dari errors. Isian tidak dihapus sehingga pengguna bisa memperbaiki bagian yang salah. Status 403 dibedakan karena masalahnya ada pada hak akses atau status final. State busy mengatur tombol selama request dan dikembalikan melalui finally.')
p.heading('5. Indikator SDGs dan batas penafsirannya',13)
p.para('Indikator yang paling dekat dengan kasus SDG 12 adalah total berat setoran berstatus Diverifikasi. Angka itu lebih layak dipakai daripada seluruh berat yang diajukan karena sudah melewati keputusan admin. Katalog Kertas, Plastik, dan Logam juga membantu pencatatan pemilahan menjadi lebih tertib.')
p.para('Namun, berat terverifikasi belum membuktikan dampak sosial secara menyeluruh. Aplikasi tidak mencatat apakah sampah benar-benar didaur ulang, kualitas prosesnya, emisi yang berkurang, perubahan kebiasaan warga kampus, atau manfaat ekonomi yang diterima. Dalam simulasi ini datanya juga fiktif. Jadi angka dashboard merupakan indikator pencatatan, bukan bukti bahwa seluruh tujuan SDG 12 sudah tercapai.')
p.heading('6. Kendala utama dan cara mengatasinya',13)
p.para('Kendala teknis yang muncul adalah build Vite pada Windows gagal karena mencoba membaca direktori induk yang dibatasi. Build berhasil setelah script memakai --configLoader runner. Cara ini dipertahankan pada package.json agar perintah build di README sesuai dengan cara yang sudah diuji.')
p.para('Pemeriksaan HTTP awal juga sempat memperoleh 409 karena request Inertia belum membawa versi aset. Skrip uji kemudian mengambil versi dari halaman awal dan mengirimkannya pada request berikutnya. Setelah diperbaiki, pengujian HTTP lulus. Pemeriksaan visual masih menjadi bagian yang perlu dilanjutkan karena akses browser otomatis terhenti; hasil mobile tidak saya anggap lulus sebelum diperiksa langsung.')
p.finish()

# Minimal standard PDF: searchable text, vector elements, and an active repository link.
objs=[None]
def add(data):
    objs.append(data if isinstance(data,bytes) else data.encode('latin1')); return len(objs)-1
catalog=add(''); tree=add('')
fonts=[add(f'<< /Type /Font /Subtype /Type1 /BaseFont /{name} /Encoding /WinAnsiEncoding >>') for name in ['Helvetica','Helvetica-Bold','Courier']]
pageids=[]
for content,links in zip(pages,annotations):
    stream=content.encode('ascii'); contentid=add(b'<< /Length '+str(len(stream)).encode()+b' >>\nstream\n'+stream+b'\nendstream')
    annids=[]
    for x1,y1,x2,y2,url in links:
        annids.append(add(f'<< /Type /Annot /Subtype /Link /Rect [{x1} {y1} {x2} {y2}] /Border [0 0 0] /A << /S /URI /URI ({url}) >> >>'))
    ann=' /Annots ['+' '.join(f'{a} 0 R' for a in annids)+']' if annids else ''
    pageids.append(add(f'<< /Type /Page /Parent {tree} 0 R /MediaBox [0 0 {W} {H}] /Resources << /Font << /F1 {fonts[0]} 0 R /F2 {fonts[1]} 0 R /F3 {fonts[2]} 0 R >> >> /Contents {contentid} 0 R{ann} >>'))
objs[catalog]=f'<< /Type /Catalog /Pages {tree} 0 R >>'.encode()
objs[tree]=f'<< /Type /Pages /Count {len(pageids)} /Kids ['.encode()+' '.join(f'{i} 0 R' for i in pageids).encode()+b'] >>'
info=add('<< /Title (RecycleHub - Asesmen Praktikum 2.1 Paket B) /Author (Muhammad Fadhil) /Subject (Dokumentasi implementasi dan refleksi) >>')
pdf=bytearray(b'%PDF-1.4\n%\xe2\xe3\xcf\xd3\n'); offsets=[0]
for i,obj in enumerate(objs[1:],1):
    offsets.append(len(pdf)); pdf.extend(f'{i} 0 obj\n'.encode()+obj+b'\nendobj\n')
xref=len(pdf);pdf.extend(f'xref\n0 {len(objs)}\n0000000000 65535 f \n'.encode())
for off in offsets[1:]: pdf.extend(f'{off:010} 00000 n \n'.encode())
pdf.extend(f'trailer\n<< /Size {len(objs)} /Root {catalog} 0 R /Info {info} 0 R >>\nstartxref\n{xref}\n%%EOF\n'.encode())
PDF.write_bytes(pdf)
print(json.dumps({'file':str(PDF),'pages':len(pages),'bytes':len(pdf)}))

# RecycleHub — Asesmen Praktikum 2.1 Paket B

Aplikasi simulasi bank sampah kampus untuk **SDG 12: Konsumsi dan Produksi yang Bertanggung Jawab**.
Jalur 2: Laravel HMVC, nwidart/laravel-modules, React, Inertia.js, Tailwind CSS, Fetch API, dan FormData.
Seluruh akun contoh merupakan data fiktif.

## Versi dan prasyarat

Versi terkunci yang digunakan:

| Komponen | Versi |
| --- | --- |
| PHP saat pengujian | 8.3.33; kebutuhan project >= 8.2 |
| Laravel | 12.72.0 |
| nwidart/laravel-modules | 12.0.5 |
| inertia-laravel | 2.0.28 |
| Laravel Fortify | 1.42.0 |
| React | 19.2.x |
| Tailwind CSS | 4.x |
| Vite | 7.1.5 |
| MySQL saat pengujian | 8.4.3 |
| Node.js saat pengujian | 24.22.1; gunakan Node >= 22.12 |

Gunakan Composer 2, npm, serta ekstensi PHP pdo_mysql, bcmath, fileinfo, mbstring, openssl, dan ekstensi standar Laravel. Pengujian foto memerlukan GD; tes SQLite memerlukan pdo_sqlite. BCMath diperlukan untuk perkalian dan pembulatan uang tanpa kehilangan presisi floating point.

## Instalasi

Jalankan perintah dari folder aplikasi yang memuat file artisan dan composer.json, yaitu smartfacility_hmvc_react. Nama folder proyek acuan dipertahankan.

1. Nyalakan MySQL melalui Laragon atau layanan MySQL lokal.
2. Pasang dependensi dan buat konfigurasi lokal:

```powershell
composer install
Copy-Item .env.example .env
php artisan key:generate
```

Jangan menimpa .env yang sudah dikonfigurasi. Isi DB_USERNAME dan DB_PASSWORD sesuai instalasi lokal:

```dotenv
APP_NAME="RecycleHub"
APP_URL=http://127.0.0.1:8000
DB_CONNECTION=mysql
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=recyclehub
DB_USERNAME=root
DB_PASSWORD=
```

Konfigurasi contoh memakai root lokal tanpa password. Kredensial aktual disimpan hanya di .env.

3. Buat database (script tidak menghapus database yang sudah ada), jalankan migration dan Seeder:

```powershell
php artisan config:clear
php scripts/create-database.php
php artisan migrate --seed
php artisan storage:link
```

Jika pengguna MySQL tidak memiliki hak CREATE DATABASE, buat database recyclehub melalui alat pengelola MySQL, kemudian jalankan migration. Jika storage link sudah ada dan menuju storage/app/public proyek ini, gunakan link tersebut.

4. Build dan jalankan:

```powershell
npm ci
npm run build
php artisan serve
```

Buka http://127.0.0.1:8000. Setelah build, aplikasi cukup dijalankan dengan php artisan serve. Untuk pengembangan, jalankan npm run dev pada terminal kedua. Jika mengganti APP_URL atau port server, sesuaikan .env dan jalankan php artisan config:clear.

Script npm menggunakan --configLoader runner agar Vite tidak perlu membundel konfigurasi melalui folder induk yang mungkin tidak dapat dibaca pada Windows.

Alternatif otomatis Windows setelah konfigurasi .env dan MySQL siap:

```powershell
.\setup.ps1
```

Script ini memasang dependensi, membuat database jika belum ada, menjalankan migration/Seeder, membuat storage link, dan build aset. Database acuan SmartFacility tidak dihapus. Gunakan database recyclehub agar skema acuan tidak bercampur dengan aplikasi ini.

## Akun uji fiktif

| Role | Email | Password |
| --- | --- | --- |
| Admin | admin@recyclehub.test | Recycle123! |
| Nasabah 1 — Nadia Fiktif | nasabah1@recyclehub.test | Recycle123! |
| Nasabah 2 — Bima Fiktif | nasabah2@recyclehub.test | Recycle123! |

Seeder menyediakan lima jenis sampah dan tiga setoran: Menunggu, Diverifikasi, dan Ditolak, melibatkan kedua nasabah. Seeder dapat dijalankan ulang tanpa menggandakan data contoh. Jangan mengganti data contoh dengan identitas pribadi.

Registrasi publik selalu menetapkan role nasabah di server. Password di-hash oleh cast model User. Login, logout, registrasi, pembatasan percobaan login, dan sesi memakai Laravel Fortify.

## Fitur dan aturan bisnis

- Dashboard admin: jumlah katalog, jumlah seluruh setoran, setoran Menunggu, dan total berat Diverifikasi.
- Dashboard nasabah: ringkasan serta daftar setoran miliknya saja.
- Katalog: pencarian kode/nama dan filter kategori melalui query database; mutasi hanya admin; kode unik; kategori Kertas/Plastik/Logam.
- Setoran: daftar, detail, tambah, edit, hapus, dan keputusan admin memakai fetch. React state diperbarui tanpa reload halaman.
- Form tambah/edit dikirim sebagai FormData. PUT/PATCH dengan file memakai POST dan field _method. Header X-XSRF-TOKEN dibaca dari cookie Laravel.
- user_id berasal dari sesi, status awal Menunggu, dan harga berasal dari database. Kiriman status, pemilik, harga, atau total palsu pada form setoran diabaikan.
- Saat setoran Menunggu diedit, server membaca ulang harga katalog dan menghitung ulang total.
- Perubahan harga katalog tidak mengubah harga historis setoran yang belum diedit.
- Admin tidak membuat setoran dan tidak mengubah isi setoran. Hanya admin menetapkan Menunggu menjadi Diverifikasi atau Ditolak, satu kali.
- Nasabah hanya mengedit/menghapus setoran sendiri yang masih Menunggu. Admin dapat menghapus setoran apa pun. Tombol hapus meminta konfirmasi.
- Katalog yang dirujuk setoran tidak dapat dihapus, baik melalui pemeriksaan controller maupun foreign key RESTRICT.
- Foto opsional JPG/JPEG/PNG maksimum 2 MB disimpan dengan nama acak di Storage disk public. Database menyimpan path relatif. Bukti dapat dibuka melalui Lihat Bukti.
- Edit tanpa foto mempertahankan foto lama. Penggantian atau penghapusan setoran membersihkan foto lama setelah transaksi database berhasil. File baru dibersihkan jika penyimpanan database gagal.
- Perhitungan positif memakai BCMath dan pembulatan half-up dua desimal. Kombinasi berat/harga yang melampaui kapasitas decimal total_nilai ditolak sebagai 422 tanpa menyimpan perubahan.
- Form Request memvalidasi isian; error tampil per field dan isian valid tetap ada. Error 403 dibedakan dari validasi 422. Tombol dinonaktifkan selama request.
- Layout bersama memuat header, menu aktif, konten, footer, Profil, dan Logout. Tabel dapat digeser horizontal pada layar kecil.

## Struktur HMVC

```text
Modules/
  JenisSampah/
    app/
      Models/JenisSampah.php
      Http/Controllers/JenisSampahController.php
      Http/Requests/JenisSampahRequest.php
      Providers/JenisSampahServiceProvider.php
    database/migrations/
    resources/js/pages/index.tsx
    routes/web.php
    composer.json
    module.json
  Setoran/
    app/
      Models/Setoran.php
      Http/Controllers/SetoranController.php
      Http/Requests/SetoranRequest.php
      Http/Requests/KeputusanRequest.php
      Services/NilaiSetoran.php
      Providers/SetoranServiceProvider.php
    database/migrations/
    resources/js/pages/index.tsx
    routes/web.php
    composer.json
    module.json
app/
  Actions/Fortify/CreateNewUser.php
  Enums/UserRole.php
  Http/Middleware/EnsureUserHasRole.php
  Http/Controllers/DashboardController.php
  Models/User.php
resources/js/
  layouts/app-layout.tsx
  components/recycle-ui.tsx
  lib/http.ts
  lib/resolve-page.ts
database/seeders/DatabaseSeeder.php
```

HMVC memisahkan fitur katalog dan transaksi sehingga model, validasi, controller, route, migration, dan antarmuka dapat dipelihara per fitur. Komponen lintas fitur seperti autentikasi dan layout tetap dibagikan. Resolver Inertia mendukung nama halaman JenisSampah::index dan Setoran::index. Modul Fasilitas/Pengaduan dari proyek acuan masih tersimpan sebagai referensi tetapi dinonaktifkan di modules_statuses.json; route dan migration modul lama tidak dimuat.

Verifikasi:

```powershell
php artisan module:list
php artisan route:list --path=katalog -v
php artisan route:list --path=setoran -v
```

Auth melindungi route kedua modul. Alias middleware role didaftarkan pada bootstrap/app.php. Otorisasi kepemilikan/status diperiksa di server, termasuk pemeriksaan ulang dengan lockForUpdate saat mutasi, sehingga keputusan final tidak dapat ditimpa request yang terlambat.

## Pengujian

Tes standar memakai SQLite in-memory sehingga tidak mengubah database aplikasi:

```powershell
php artisan test --compact
npm run types
npm run build
composer validate --no-check-publish
```

Untuk pengujian MySQL gunakan **database terpisah yang khusus tes**. RefreshDatabase membuat ulang skema database pengujian.

```powershell
php scripts/create-database.php recyclehub_testing
$env:DB_CONNECTION = 'mysql'
$env:DB_DATABASE = 'recyclehub_testing'
php artisan test --compact
Remove-Item Env:DB_CONNECTION
Remove-Item Env:DB_DATABASE
```

Suite tests/Feature/RecycleHubTest.php memeriksa registrasi dengan payload role palsu, password hash, sesi/logout, proteksi guest, mutasi katalog, pencarian/filter, pemilik/status/total palsu, harga historis, isolasi dua nasabah pada daftar/dashboard/detail/edit/update/delete, larangan admin membuat/mengedit, keputusan final, validasi, pembulatan, batas total lintas field, dan siklus upload foto.

Pengujian HTTP dengan server berjalan dan akun Seeder:

```powershell
node scripts/smoke-http.mjs
```

Script ini memeriksa cookie sesi MySQL, protokol halaman Inertia, JSON tersaring, CSRF 419, validasi 422, akses 403, dan logout. Script tidak membuat atau menghapus transaksi. Jalankan setelah build selesai; proses build mengganti manifest aset sementara.

Hasil verifikasi implementasi: 21 tes/185 assertions lulus pada SQLite dan MySQL; pemeriksaan tipe TypeScript, build produksi, dan HTTP smoke lulus. Pemeriksaan visual desktop/mobile belum terverifikasi karena alat Computer Use tidak dapat memastikan URL Chrome pada sesi pengembangan. Lakukan pemeriksaan manual sebelum mengambil screenshot laporan.

## Ringkasan cara mengerjakan Soal 1–8 dan lokasi file

Semua lokasi di bawah dihitung dari folder `smartfacility_hmvc_react` (folder yang berisi `artisan`). Klik nama file untuk membuka implementasinya. Urutan pengerjaan: siapkan database dan modul, buat autentikasi, pasang otorisasi, kerjakan katalog dan transaksi, lalu rapikan layout dan validasi.

| Soal | Cara mengerjakan secara ringkas | Lokasi implementasi |
| --- | --- | --- |
| **1. Project dan HMVC** | Atur koneksi MySQL `recyclehub`, siapkan kunci aplikasi, dan jalankan migration. Aktifkan modul JenisSampah dan Setoran, lalu periksa dengan `php artisan module:list` dan `php artisan route:list`. HMVC memisahkan kode berdasarkan fitur agar mudah dipelihara. | [Konfigurasi contoh](.env.example), [dependensi Laravel/HMVC](composer.json), [status modul](modules_statuses.json), [modul JenisSampah](Modules/JenisSampah), [modul Setoran](Modules/Setoran). |
| **2. Autentikasi dan dashboard** | Tambahkan role dengan default `nasabah`. Gunakan Fortify untuk register/login/logout; role registrasi ditetapkan di server dan password di-hash. Buat satu admin serta dua nasabah melalui Seeder. Hitung ringkasan dashboard dari database sesuai pengguna yang login. | [Migration role](database/migrations/2025_11_01_000001_add_role_to_users_table.php), [registrasi](app/Actions/Fortify/CreateNewUser.php), [model User dan hash password](app/Models/User.php), [konfigurasi halaman autentikasi](app/Providers/FortifyServiceProvider.php), [Seeder](database/seeders/DatabaseSeeder.php), [query dashboard](app/Http/Controllers/DashboardController.php), [halaman dashboard](resources/js/pages/dashboard.tsx). |
| **3. Middleware dan otorisasi** | Daftarkan middleware role dan lindungi route dengan `auth`. Batasi mutasi katalog/keputusan untuk admin. Pada transaksi, periksa pemilik dan status Menunggu di backend; tindakan yang tidak berwenang dikembalikan sebagai 403. Sesuaikan tombol React dengan hak akses yang sama. | [Middleware role](app/Http/Middleware/EnsureUserHasRole.php), [pendaftaran alias](bootstrap/app.php), [route katalog](Modules/JenisSampah/routes/web.php), [route setoran](Modules/Setoran/routes/web.php), [pemeriksaan kepemilikan/status](Modules/Setoran/app/Http/Controllers/SetoranController.php), [otorisasi form setoran](Modules/Setoran/app/Http/Requests/SetoranRequest.php). |
| **4. CRUD katalog** | Buat tabel dan model jenis sampah dengan kode unik. Sediakan tambah, edit, hapus, pencarian kode/nama, dan filter kategori. Validasi melalui Form Request. Tolak penghapusan jenis sampah yang dipakai transaksi; perubahan harga tidak mengubah setoran lama. | [Migration katalog](Modules/JenisSampah/database/migrations/2026_11_20_000001_create_jenis_sampahs_table.php), [model](Modules/JenisSampah/app/Models/JenisSampah.php), [controller dan query pencarian/filter](Modules/JenisSampah/app/Http/Controllers/JenisSampahController.php), [Form Request](Modules/JenisSampah/app/Http/Requests/JenisSampahRequest.php), [tabel dan form React](Modules/JenisSampah/resources/js/pages/index.tsx). |
| **5. Setoran dengan AJAX** | Buat tabel setoran dan relasinya ke User serta JenisSampah. Ambil pemilik dari sesi, tetapkan Menunggu, dan hitung nilai dari harga database. Kirim form/foto melalui `fetch` dan `FormData`, lalu perbarui state dari JSON. Simpan foto di Storage public dan bersihkan file saat diganti/dihapus. Admin hanya boleh mengambil satu keputusan final. | [Migration setoran](Modules/Setoran/database/migrations/2026_11_20_000002_create_setorans_table.php), [model dan relasi](Modules/Setoran/app/Models/Setoran.php), [controller transaksi/upload/keputusan](Modules/Setoran/app/Http/Controllers/SetoranController.php), [perhitungan desimal](Modules/Setoran/app/Services/NilaiSetoran.php), [helper fetch dan CSRF](resources/js/lib/http.ts), [form, daftar, detail, dan state React](Modules/Setoran/resources/js/pages/index.tsx). |
| **6. Layout dan navigasi** | Buat layout React bersama dengan header, konten, footer, menu aktif, dan Logout. Pakai pada dashboard, katalog, serta setoran. Halaman Profil menampilkan nama, email, dan role akun aktif. | [Layout dan menu](resources/js/layouts/app-layout.tsx), [Profil](resources/js/pages/profile.tsx), [route dashboard/profil](routes/web.php), [props pengguna aktif](app/Http/Middleware/HandleInertiaRequests.php). |
| **7. Validasi dan umpan balik** | Validasi katalog, setoran, serta keputusan memakai Form Request. Baca error 422 dan tampilkan di field tanpa menghapus isian; bedakan dari 403. Tampilkan pesan sukses hanya sesudah server berhasil menyimpan. Periksa juga kombinasi berat/harga agar total tidak melampaui kapasitas kolom. | [Request katalog](Modules/JenisSampah/app/Http/Requests/JenisSampahRequest.php), [request setoran](Modules/Setoran/app/Http/Requests/SetoranRequest.php), [request keputusan](Modules/Setoran/app/Http/Requests/KeputusanRequest.php), [Field, Notice, dan pemetaan error](resources/js/components/recycle-ui.tsx), [pesan validasi Indonesia](lang/id/validation.php), [batas total nilai](Modules/Setoran/app/Services/NilaiSetoran.php). |
| **8. Antarmuka dan UX** | Gunakan gaya tombol, form, tabel, badge, serta notifikasi yang konsisten. Susun kartu/form secara responsif dan bungkus tabel dengan `overflow-x-auto`. Gunakan state `busy` untuk loading/tombol nonaktif, pulihkan dengan `finally`, dan tampilkan pesan saat daftar kosong. Periksa desktop dan mobile melalui browser. | [CSS bersama](resources/css/app.css), [komponen status/notifikasi](resources/js/components/recycle-ui.tsx), [dashboard responsif](resources/js/pages/dashboard.tsx), [halaman katalog](Modules/JenisSampah/resources/js/pages/index.tsx), [halaman setoran dan loading](Modules/Setoran/resources/js/pages/index.tsx). |

Untuk mengecek aturan bisnis dan akses kedua akun, lihat [tes fitur RecycleHub](tests/Feature/RecycleHubTest.php). Contoh pengujian HTTP nyata, termasuk sesi dan CSRF, ada di [scripts/smoke-http.mjs](scripts/smoke-http.mjs). Cara menjalankannya dijelaskan pada bagian **Pengujian** di atas; daftar screenshot untuk tiap soal ada di bawah.

## Panduan bukti laporan Soal 1–8

Gunakan potongan kode dari file yang disebutkan, jelaskan dengan bahasa sendiri, dan ambil screenshot dari aplikasi yang Anda jalankan. Jangan memasukkan .env, rahasia, atau seluruh source ke PDF.

| Soal | Sumber implementasi dan bukti yang dapat diambil |
| --- | --- |
| 1 | composer.json/composer.lock, .env.example, modules_statuses.json, struktur kedua modul, hasil module:list/route:list, halaman aplikasi; jelaskan pemisahan HMVC. |
| 2 | Migration role, CreateNewUser, DatabaseSeeder, dashboard admin/nasabah; setelah logout buka /dashboard dan tunjukkan redirect login. |
| 3 | EnsureUserHasRole, bootstrap/app.php, route modul, SetoranRequest dan authorizeItem; nasabah2 mencoba detail/edit/delete ID nasabah1 (403); nasabah mencoba mutasi katalog (403). |
| 4 | Migration/model/request/controller JenisSampah, tabel katalog, form tambah/edit, pencarian dan filter; coba hapus K001 yang dipakai transaksi dan tangkap pesan penolakan. |
| 5 | Migration/relasi Setoran, NilaiSetoran, controller, lib/http.ts, form React; buat 2,50 kg K001 harga 3000 menghasilkan 7500, ubah harga katalog ke 4000, tunjukkan harga lama tetap, edit saat Menunggu menjadi 10000; verifikasi dan tunjukkan edit ditolak. |
| 6 | layouts/app-layout.tsx; screenshot dashboard/katalog/setoran dengan header, menu aktif, footer yang sama; Profil memuat nama/email/role. |
| 7 | Kedua Form Request dan KeputusanRequest; submit berat 1.234 atau catatan kosong; tampilkan 422 per field. Untuk lintas field, harga 9999999999.99 dan berat 999999.99 masing-masing berada dalam batas kolom tetapi total melampaui decimal(14,2); tunjukkan penolakan dan data tidak berubah. |
| 8 | Screenshot desktop dan mode smartphone (mis. 390 px); tabel dapat digeser, badge/notifikasi konsisten; gunakan Network throttling untuk mengambil screenshot tombol Menyimpan…/disabled. |

Untuk uji kepemilikan, login kedua nasabah secara bergantian atau gunakan jendela incognito yang terpisah. Gunakan tab Network browser untuk bukti kode respons AJAX 403/422. Gunakan data uji tambahan jika ingin mempertahankan tiga contoh awal.

Laporan PDF: identitas sendiri, tautan GitHub yang dapat diakses dosen, dokumentasi Soal 1–8, kesimpulan dan refleksi. Nama file NRP_Nama_AsesmenPraktikum2.1_PaketB.pdf, maksimum 10 MB. Isi identitas, screenshot nyata, refleksi pribadi, serta tautan repository Anda sendiri sebelum pengumpulan.

## Repository

Draf laporan 13 halaman untuk Muhammad Fadhil, NIM 707012500122, tersedia di output/pdf/707012500122_Muhammad_Fadhil_AsesmenPraktikum2.1_PaketB.pdf. Keenam refleksi sudah dijawab. Naskah masih memerlukan kelas, screenshot aplikasi, pemeriksaan mobile, dan verifikasi akses repository sebelum dikumpulkan. Tautan repository pada naskah: https://github.com/muhammadfadhilc/Assesment_2_PABW. Belum ada source yang dipush dari lingkungan ini.

Source penyusun PDF ada di scripts/build-report.py dan memakai Python standard library. Pada Laragon komputer ini dapat dijalankan dengan `C:/laragon/bin/python/python-3.13/python.exe scripts/build-report.py`; pada komputer lain gunakan interpreter Python yang tersedia.

Commit source, Modules/JenisSampah dan Modules/Setoran, migration, Seeder, Form Request, middleware, composer.json/composer.lock, package.json/package-lock.json, .env.example, dan README.

.env, vendor, node_modules, public/build, public/storage, dan file runtime tidak disertakan; .gitignore sudah mengecualikannya. Buat storage link dan build aset di komputer tujuan. Folder workspace saat implementasi belum merupakan repository Git; belum ada push ke GitHub atau pengumpulan LMS.
# Assesment_2_PABW

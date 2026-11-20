<?php

use App\Models\User;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Facades\Storage;
use Inertia\Testing\AssertableInertia as Assert;
use Modules\JenisSampah\Models\JenisSampah;
use Modules\Setoran\Models\Setoran;
use Modules\Setoran\Services\NilaiSetoran;

function katalogUji(array $data = []): JenisSampah {
    return JenisSampah::create(array_merge(['kode_jenis' => 'K001', 'nama_jenis' => 'Kertas HVS', 'kategori' => 'Kertas', 'harga_per_kg' => '3000.00'], $data));
}
function payloadSetoran(JenisSampah $jenis, array $data = []): array {
    return array_merge(['jenis_sampah_id' => $jenis->id, 'berat_kg' => '2.50', 'tanggal_setor' => '2026-11-20', 'catatan' => 'Kertas bersih dan kering'], $data);
}
function setoranUji(User $user, JenisSampah $jenis, string $status = 'Menunggu'): Setoran {
    return Setoran::create([...payloadSetoran($jenis), 'user_id' => $user->id, 'status' => $status, 'harga_saat_setor' => $jenis->harga_per_kg, 'total_nilai' => '7500.00']);
}

beforeEach(function () { $this->withoutVite(); });

it('assigns nasabah during malicious public registration and hashes passwords', function () {
    $this->post('/register', ['name' => 'Fiktif Baru', 'email' => 'baru@example.test', 'password' => 'Password123!', 'password_confirmation' => 'Password123!', 'role' => 'admin'])->assertRedirect('/dashboard');
    $user = User::where('email', 'baru@example.test')->firstOrFail();
    expect($user->role->value)->toBe('nasabah')->and(Hash::check('Password123!', $user->password))->toBeTrue();
});

it('authenticates the session and denies dashboard after logout', function () {
    $user = User::factory()->create(['password' => 'Password123!']);
    $this->post('/login', ['email' => $user->email, 'password' => 'Password123!'])->assertRedirect('/dashboard');
    $this->assertAuthenticatedAs($user);
    $this->post('/logout')->assertRedirect('/');
    $this->get('/dashboard')->assertRedirect('/login');
});

it('protects module pages and json endpoints from guests', function () {
    foreach (['/dashboard', '/profil', '/katalog', '/setoran', '/setoran/create'] as $url) $this->get($url)->assertRedirect('/login');
    $this->postJson('/setoran', [])->assertUnauthorized();
    $this->getJson('/katalog')->assertUnauthorized();
});

it('denies nasabah all catalog mutation and form routes', function () {
    $this->actingAs(User::factory()->create());
    $jenis = katalogUji();
    $this->get('/katalog/create')->assertForbidden();
    $this->get('/katalog/'.$jenis->id.'/edit')->assertForbidden();
    $this->postJson('/katalog', [])->assertForbidden();
    $this->putJson('/katalog/'.$jenis->id, ['nama_jenis' => 'Palsu'])->assertForbidden();
    $this->deleteJson('/katalog/'.$jenis->id)->assertForbidden();
    expect($jenis->fresh()->nama_jenis)->toBe('Kertas HVS');
});

it('supports validated admin catalog CRUD and unique codes', function () {
    $this->actingAs(User::factory()->admin()->create());
    $data = ['kode_jenis' => 'P001', 'nama_jenis' => 'Botol PET', 'kategori' => 'Plastik', 'harga_per_kg' => '4000'];
    $id = $this->postJson('/katalog', $data)->assertCreated()->json('item.id');
    $this->postJson('/katalog', $data)->assertUnprocessable()->assertJsonValidationErrors('kode_jenis');
    $this->putJson('/katalog/'.$id, [...$data, 'harga_per_kg' => '4500'])->assertOk();
    $this->putJson('/katalog/'.$id, [...$data, 'kategori' => 'Organik', 'harga_per_kg' => '0'])->assertUnprocessable()->assertJsonValidationErrors(['kategori', 'harga_per_kg']);
    $this->deleteJson('/katalog/'.$id)->assertOk();
    $this->assertDatabaseMissing('jenis_sampahs', ['id' => $id]);
});

it('searches code or name and combines category filters including empty keyword', function () {
    katalogUji(); katalogUji(['kode_jenis' => 'P001', 'nama_jenis' => 'Botol PET', 'kategori' => 'Plastik']);
    $this->actingAs(User::factory()->create());
    $this->getJson('/katalog?q=K001')->assertJsonCount(1, 'items')->assertJsonPath('items.0.kode_jenis', 'K001');
    $this->getJson('/katalog?q=Kertas&kategori=Plastik')->assertJsonCount(0, 'items');
    $this->getJson('/katalog?q=&kategori=Plastik')->assertJsonCount(1, 'items')->assertJsonPath('items.0.kode_jenis', 'P001');
});

it('uses session owner, pending status and server prices despite forged payload', function () {
    $user = User::factory()->create(); $other = User::factory()->create(); $jenis = katalogUji();
    $this->actingAs($user)->postJson('/setoran', payloadSetoran($jenis, ['user_id' => $other->id, 'status' => 'Diverifikasi', 'harga_saat_setor' => '1', 'total_nilai' => '1']))
        ->assertCreated()->assertJsonPath('item.user_id', $user->id)->assertJsonPath('item.status', 'Menunggu')->assertJsonPath('item.harga_saat_setor', '3000.00')->assertJsonPath('item.total_nilai', '7500.00');
});

it('treats zero as a search term rather than an empty search', function () {
    katalogUji();
    katalogUji(['kode_jenis' => 'ABC', 'nama_jenis' => 'Kardus']);
    $this->actingAs(User::factory()->create());
    $this->getJson('/katalog?q=0')->assertJsonCount(1, 'items')->assertJsonPath('items.0.kode_jenis', 'K001');
    $this->getJson('/katalog?q=')->assertJsonCount(2, 'items');
});

it('preserves historical prices until an owner edits a waiting transaction', function () {
    $user = User::factory()->create(); $jenis = katalogUji(); $item = setoranUji($user, $jenis);
    $jenis->update(['harga_per_kg' => '4000.00']);
    expect($item->fresh()->harga_saat_setor)->toBe('3000.00')->and($item->fresh()->total_nilai)->toBe('7500.00');
    $this->actingAs($user)->putJson('/setoran/'.$item->id, payloadSetoran($jenis))->assertOk()->assertJsonPath('item.harga_saat_setor', '4000.00')->assertJsonPath('item.total_nilai', '10000.00');
});

it('isolates list dashboard detail edit update and delete between two nasabah', function () {
    $owner = User::factory()->create(); $other = User::factory()->create(); $jenis = katalogUji(); $item = setoranUji($owner, $jenis);
    $this->actingAs($other)->getJson('/setoran')->assertJsonCount(0, 'items');
    $this->get('/dashboard')->assertInertia(fn (Assert $page) => $page->where('totalSetoran', 0)->has('items', 0));
    foreach (['/setoran/'.$item->id, '/setoran/'.$item->id.'/edit'] as $url) { $this->get($url)->assertForbidden(); $this->getJson($url)->assertForbidden(); }
    $this->putJson('/setoran/'.$item->id, payloadSetoran($jenis, ['catatan' => 'Palsu']))->assertForbidden();
    $this->deleteJson('/setoran/'.$item->id)->assertForbidden();
    expect($item->fresh()->catatan)->toBe('Kertas bersih dan kering');
    $this->actingAs($owner)->getJson('/setoran/'.$item->id)->assertOk();
    $this->getJson('/setoran/'.$item->id.'/edit')->assertOk();
});

it('denies admin creation and content editing but permits any deletion', function () {
    $user = User::factory()->create(); $jenis = katalogUji(); $item = setoranUji($user, $jenis, 'Ditolak');
    $this->actingAs(User::factory()->admin()->create());
    $this->get('/setoran/create')->assertForbidden();
    $this->postJson('/setoran', payloadSetoran($jenis))->assertForbidden();
    $this->get('/setoran/'.$item->id.'/edit')->assertForbidden();
    $this->putJson('/setoran/'.$item->id, payloadSetoran($jenis))->assertForbidden();
    $this->deleteJson('/setoran/'.$item->id)->assertOk();
});

it('enforces one final decision and prevents nasabah decisions', function (string $status) {
    $user = User::factory()->create(); $jenis = katalogUji(); $item = setoranUji($user, $jenis);
    $this->actingAs($user)->patchJson('/setoran/'.$item->id.'/keputusan', ['status' => $status])->assertForbidden();
    $this->actingAs(User::factory()->admin()->create());
    $this->patchJson('/setoran/'.$item->id.'/keputusan', ['status' => 'Menunggu'])->assertUnprocessable()->assertJsonValidationErrors('status');
    $this->patchJson('/setoran/'.$item->id.'/keputusan', ['status' => $status])->assertOk();
    $this->patchJson('/setoran/'.$item->id.'/keputusan', ['status' => 'Menunggu'])->assertForbidden();
    $this->patchJson('/setoran/'.$item->id.'/keputusan', ['status' => $status === 'Ditolak' ? 'Diverifikasi' : 'Ditolak'])->assertForbidden();
    $this->actingAs($user)->putJson('/setoran/'.$item->id, payloadSetoran($jenis))->assertForbidden();
    $this->get('/setoran/'.$item->id.'/edit')->assertForbidden();
    $this->deleteJson('/setoran/'.$item->id)->assertForbidden();
    expect($item->fresh()->status)->toBe($status);
})->with(['Diverifikasi', 'Ditolak']);

it('refuses deleting a referenced catalog without changing records', function () {
    $jenis = katalogUji(); setoranUji(User::factory()->create(), $jenis);
    $this->actingAs(User::factory()->admin()->create())->deleteJson('/katalog/'.$jenis->id)->assertUnprocessable()->assertJsonValidationErrors('katalog');
    $this->assertDatabaseHas('jenis_sampahs', ['id' => $jenis->id]); $this->assertDatabaseCount('setorans', 1);
});

it('validates setoran fields and never writes invalid records', function () {
    $jenis = katalogUji(); $this->actingAs(User::factory()->create());
    $this->postJson('/setoran', payloadSetoran($jenis, ['jenis_sampah_id' => 99999, 'berat_kg' => '1.234', 'tanggal_setor' => '2026-02-30', 'catatan' => '']))->assertUnprocessable()->assertJsonValidationErrors(['jenis_sampah_id', 'berat_kg', 'tanggal_setor', 'catatan']);
    $this->postJson('/setoran', payloadSetoran($jenis, ['berat_kg' => '0']))->assertUnprocessable();
    $this->assertDatabaseCount('setorans', 0);
});

it('rejects cross-field total overflow atomically on create and update', function () {
    $jenis = katalogUji(['harga_per_kg' => '9999999999.99']); $user = User::factory()->create();
    $this->actingAs($user)->postJson('/setoran', payloadSetoran($jenis, ['berat_kg' => '999999.99']))->assertUnprocessable()->assertJsonValidationErrors('berat_kg');
    $this->assertDatabaseCount('setorans', 0);
    $jenis->update(['harga_per_kg' => '3000']); $item = setoranUji($user, $jenis); $jenis->update(['harga_per_kg' => '9999999999.99']);
    $this->putJson('/setoran/'.$item->id, payloadSetoran($jenis, ['berat_kg' => '999999.99']))->assertUnprocessable();
    expect($item->fresh()->total_nilai)->toBe('7500.00')->and($item->fresh()->harga_saat_setor)->toBe('3000.00');
});

it('rounds decimal calculations to two places using half-up', function () {
    expect(NilaiSetoran::hitung('0.01', '0.50'))->toBe('0.01')->and(NilaiSetoran::hitung('2.50', '3000.00'))->toBe('7500.00');
});

it('stores optional photo, preserves it without replacement, cleans replacement and deletion', function () {
    Storage::fake('public'); $jenis = katalogUji(); $user = User::factory()->create(); $this->actingAs($user);
    $r = $this->post('/setoran', [...payloadSetoran($jenis), 'foto_bukti' => UploadedFile::fake()->image('bukti.png')], ['Accept' => 'application/json'])->assertCreated();
    $id = $r->json('item.id'); $old = $r->json('item.foto_bukti'); Storage::disk('public')->assertExists($old);
    $this->putJson('/setoran/'.$id, payloadSetoran($jenis))->assertOk()->assertJsonPath('item.foto_bukti', $old);
    $r = $this->post('/setoran/'.$id, [...payloadSetoran($jenis), '_method' => 'PUT', 'foto_bukti' => UploadedFile::fake()->image('baru.jpg')], ['Accept' => 'application/json'])->assertOk();
    $new = $r->json('item.foto_bukti'); Storage::disk('public')->assertMissing($old); Storage::disk('public')->assertExists($new);
    $this->deleteJson('/setoran/'.$id)->assertOk(); Storage::disk('public')->assertMissing($new);
});

it('rejects large or unsupported photos and preserves previous database contents', function () {
    Storage::fake('public'); $jenis = katalogUji(); $user = User::factory()->create(); $this->actingAs($user);
    foreach ([UploadedFile::fake()->image('besar.png')->size(2049), UploadedFile::fake()->image('animasi.gif'), UploadedFile::fake()->create('palsu.jpg', 10, 'text/plain')] as $file) {
        $this->post('/setoran', [...payloadSetoran($jenis), 'foto_bukti' => $file], ['Accept' => 'application/json'])->assertUnprocessable()->assertJsonValidationErrors('foto_bukti');
    }
    $this->assertDatabaseCount('setorans', 0); expect(Storage::disk('public')->allFiles())->toBe([]);
});

it('returns database-derived summaries and seeds five types and all example statuses', function () {
    $this->seed();
    $this->assertDatabaseCount('jenis_sampahs', 5); $this->assertDatabaseCount('setorans', 3);
    $this->actingAs(User::where('role', 'admin')->firstOrFail())->get('/dashboard')->assertInertia(fn (Assert $page) => $page->where('totalKatalog', 5)->where('totalSetoran', 3)->where('totalMenunggu', 1)->where('beratDiverifikasi', fn ($value) => (float) $value === 2.5)->has('items', 3));
    $this->actingAs(User::where('email', 'nasabah1@recyclehub.test')->firstOrFail())->get('/dashboard')->assertInertia(fn (Assert $page) => $page->where('totalSetoran', 2)->has('items', 2));
    $this->seed(); $this->assertDatabaseCount('setorans', 3);
});

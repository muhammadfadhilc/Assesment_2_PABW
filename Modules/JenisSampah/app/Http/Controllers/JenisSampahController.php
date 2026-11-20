<?php
namespace Modules\JenisSampah\Http\Controllers;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Database\QueryException;
use Illuminate\Support\Facades\DB;
use Illuminate\Validation\ValidationException;
use Inertia\Inertia;
use Modules\JenisSampah\Models\JenisSampah;
use Modules\JenisSampah\Http\Requests\JenisSampahRequest;
class JenisSampahController extends Controller {
    public function index(Request $request) {
        $filters = $request->validate(['q' => 'nullable|string|max:255', 'kategori' => 'nullable|in:Kertas,Plastik,Logam']);
        $term = trim($filters['q'] ?? '');
        $items = JenisSampah::query()
            ->when($term !== '', fn ($q) => $q->where(fn ($q) => $q->where('kode_jenis', 'like', '%'.$term.'%')->orWhere('nama_jenis', 'like', '%'.$term.'%')))
            ->when($filters['kategori'] ?? null, fn ($q, $category) => $q->where('kategori', $category))
            ->orderBy('kode_jenis')->get();
        return $request->expectsJson() ? response()->json(['items' => $items]) : Inertia::render('JenisSampah::index', ['items' => $items, 'filters' => $filters]);
    }
    public function create() { return Inertia::render('JenisSampah::index', ['items' => JenisSampah::orderBy('kode_jenis')->get(), 'openForm' => true]); }
    public function edit(JenisSampah $jenis_sampah) { return Inertia::render('JenisSampah::index', ['items' => JenisSampah::orderBy('kode_jenis')->get(), 'editing' => $jenis_sampah, 'openForm' => true]); }
    public function store(JenisSampahRequest $request) {
        return response()->json(['item' => JenisSampah::create($request->validated()), 'message' => 'Jenis sampah berhasil ditambahkan.'], 201);
    }
    public function update(JenisSampahRequest $request, JenisSampah $jenis_sampah) {
        $jenis_sampah->update($request->validated());
        return response()->json(['item' => $jenis_sampah->fresh(), 'message' => 'Katalog diperbarui. Harga setoran tersimpan tetap dipertahankan.']);
    }
    public function destroy(JenisSampah $jenis_sampah) {
        try {
            DB::transaction(function () use ($jenis_sampah) {
                $item = JenisSampah::lockForUpdate()->findOrFail($jenis_sampah->id);
                if ($item->setorans()->exists()) {
                    throw ValidationException::withMessages(['katalog' => 'Jenis sampah sudah digunakan dalam setoran dan tidak dapat dihapus.']);
                }
                $item->delete();
            });
        } catch (QueryException $e) {
            if (!in_array((string) $e->getCode(), ['23000', '23503'])) { throw $e; }
            throw ValidationException::withMessages(['katalog' => 'Jenis sampah sudah digunakan dalam setoran dan tidak dapat dihapus.']);
        }
        return response()->json(['message' => 'Jenis sampah berhasil dihapus.']);
    }
}

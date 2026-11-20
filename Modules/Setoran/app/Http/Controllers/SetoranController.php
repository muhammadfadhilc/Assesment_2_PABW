<?php
namespace Modules\Setoran\Http\Controllers;
use App\Http\Controllers\Controller;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Inertia\Inertia;
use Modules\JenisSampah\Models\JenisSampah;
use Modules\Setoran\Http\Requests\SetoranRequest;
use Modules\Setoran\Http\Requests\KeputusanRequest;
use Modules\Setoran\Models\Setoran;
use Modules\Setoran\Services\NilaiSetoran;
use Throwable;
class SetoranController extends Controller {
    private function authorizeItem(Request $request, Setoran $item, bool $mutate = false): void {
        abort_unless($request->user()->isAdmin() || $item->user_id === $request->user()->id, 403, 'Anda tidak berhak mengakses setoran akun lain.');
        if ($mutate && !$request->user()->isAdmin()) {
            abort_unless($item->status === 'Menunggu', 403, 'Setoran dengan keputusan final tidak dapat diubah atau dihapus.');
        }
    }
    private function items(Request $request) {
        return Setoran::with(['user:id,name', 'jenisSampah'])
            ->when(!$request->user()->isAdmin(), fn ($q) => $q->where('user_id', $request->user()->id))
            ->latest('id')->get();
    }
    private function page(Request $request, array $extra = []) {
        return Inertia::render('Setoran::index', [...$extra, 'items' => $this->items($request), 'katalog' => JenisSampah::orderBy('kode_jenis')->get()]);
    }
    public function index(Request $request) {
        return $request->expectsJson() ? response()->json(['items' => $this->items($request)]) : $this->page($request);
    }
    public function create(Request $request) { return $this->page($request, ['openForm' => true]); }
    public function show(Request $request, Setoran $setoran) {
        $this->authorizeItem($request, $setoran);
        $setoran->load(['user:id,name', 'jenisSampah']);
        return $request->expectsJson() ? response()->json(['item' => $setoran]) : $this->page($request, ['detail' => $setoran]);
    }
    public function edit(Request $request, Setoran $setoran) {
        $this->authorizeItem($request, $setoran, true);
        $setoran->load(['user:id,name', 'jenisSampah']);
        return $request->expectsJson() ? response()->json(['item' => $setoran]) : $this->page($request, ['editing' => $setoran, 'openForm' => true]);
    }
    private function save(SetoranRequest $request, ?Setoran $setoran = null) {
        $newPath = null;
        $oldPath = null;
        try {
            $item = DB::transaction(function () use ($request, $setoran, &$newPath, &$oldPath) {
                $item = $setoran ? Setoran::lockForUpdate()->findOrFail($setoran->id) : new Setoran;
                if ($setoran) {
                    $this->authorizeItem($request, $item, true);
                    abort_if($request->user()->isAdmin(), 403);
                }
                $data = $request->safe()->except('foto_bukti');
                $jenis = JenisSampah::lockForUpdate()->findOrFail($data['jenis_sampah_id']);
                $data['harga_saat_setor'] = $jenis->harga_per_kg;
                $data['total_nilai'] = NilaiSetoran::hitung((string) $data['berat_kg'], $jenis->harga_per_kg);
                if (!$setoran) { $data['user_id'] = $request->user()->id; $data['status'] = 'Menunggu'; }
                if ($request->hasFile('foto_bukti')) {
                    $oldPath = $item->foto_bukti;
                    $newPath = $request->file('foto_bukti')->store('setoran', 'public');
                    $data['foto_bukti'] = $newPath;
                }
                $item->fill($data)->save();
                return $item;
            });
        } catch (Throwable $e) {
            if ($newPath) { Storage::disk('public')->delete($newPath); }
            throw $e;
        }
        if ($oldPath) { Storage::disk('public')->delete($oldPath); }
        return response()->json(['item' => $item->load(['user:id,name', 'jenisSampah']), 'message' => $setoran ? 'Setoran diperbarui dan nilai dihitung ulang.' : 'Setoran berhasil dibuat dengan status Menunggu.'], $setoran ? 200 : 201);
    }
    public function store(SetoranRequest $request) { return $this->save($request); }
    public function update(SetoranRequest $request, Setoran $setoran) { return $this->save($request, $setoran); }
    public function keputusan(KeputusanRequest $request, Setoran $setoran) {
        $item = DB::transaction(function () use ($request, $setoran) {
            $item = Setoran::lockForUpdate()->findOrFail($setoran->id);
            abort_unless($item->status === 'Menunggu', 403, 'Keputusan sudah final.');
            $item->update($request->validated());
            return $item;
        });
        return response()->json(['item' => $item->load(['user:id,name', 'jenisSampah']), 'message' => 'Keputusan '.$item->status.' berhasil disimpan.']);
    }
    public function destroy(Request $request, Setoran $setoran) {
        $path = DB::transaction(function () use ($request, $setoran) {
            $item = Setoran::lockForUpdate()->findOrFail($setoran->id);
            $this->authorizeItem($request, $item, true);
            $path = $item->foto_bukti;
            $item->delete();
            return $path;
        });
        if ($path) { Storage::disk('public')->delete($path); }
        return response()->json(['message' => 'Setoran berhasil dihapus.']);
    }
}

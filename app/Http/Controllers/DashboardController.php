<?php
namespace App\Http\Controllers;
use Illuminate\Http\Request;
use Inertia\Inertia;
use Modules\JenisSampah\Models\JenisSampah;
use Modules\Setoran\Models\Setoran;
class DashboardController extends Controller {
    public function __invoke(Request $request) {
        $query = Setoran::query()->when(!$request->user()->isAdmin(), fn ($q) => $q->where('user_id', $request->user()->id));
        return Inertia::render('dashboard', [
            'totalKatalog' => JenisSampah::count(),
            'totalSetoran' => (clone $query)->count(),
            'totalMenunggu' => (clone $query)->where('status', 'Menunggu')->count(),
            'beratDiverifikasi' => (clone $query)->where('status', 'Diverifikasi')->sum('berat_kg'),
            'items' => (clone $query)->with(['jenisSampah', 'user:id,name'])->latest('id')->get(),
        ]);
    }
}

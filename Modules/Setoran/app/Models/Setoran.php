<?php
namespace Modules\Setoran\Models;
use App\Models\User;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Support\Facades\Storage;
use Modules\JenisSampah\Models\JenisSampah;
class Setoran extends Model {
    protected $fillable = ['user_id', 'jenis_sampah_id', 'berat_kg', 'tanggal_setor', 'catatan', 'status', 'foto_bukti', 'harga_saat_setor', 'total_nilai'];
    protected $appends = ['foto_url'];
    protected function casts(): array {
        return ['berat_kg' => 'decimal:2', 'harga_saat_setor' => 'decimal:2', 'total_nilai' => 'decimal:2', 'tanggal_setor' => 'date:Y-m-d'];
    }
    public function user(): BelongsTo { return $this->belongsTo(User::class); }
    public function jenisSampah(): BelongsTo { return $this->belongsTo(JenisSampah::class); }
    public function getFotoUrlAttribute(): ?string { return $this->foto_bukti ? Storage::disk('public')->url($this->foto_bukti) : null; }
}

<?php
namespace Modules\JenisSampah\Models;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Modules\Setoran\Models\Setoran;
class JenisSampah extends Model {
    protected $fillable = ['kode_jenis', 'nama_jenis', 'kategori', 'harga_per_kg', 'deskripsi'];
    protected function casts(): array { return ['harga_per_kg' => 'decimal:2']; }
    public function setorans(): HasMany { return $this->hasMany(Setoran::class); }
}

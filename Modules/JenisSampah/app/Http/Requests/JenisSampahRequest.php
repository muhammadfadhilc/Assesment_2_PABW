<?php
namespace Modules\JenisSampah\Http\Requests;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;
class JenisSampahRequest extends FormRequest {
    public function authorize(): bool { return $this->user()?->isAdmin() ?? false; }
    public function rules(): array {
        return [
            'kode_jenis' => ['required', 'string', 'max:255', Rule::unique('jenis_sampahs')->ignore($this->route('jenis_sampah'))],
            'nama_jenis' => ['required', 'string', 'max:255'],
            'kategori' => ['required', Rule::in(['Kertas', 'Plastik', 'Logam'])],
            'harga_per_kg' => ['required', 'numeric', 'gt:0', 'decimal:0,2', 'max:9999999999.99'],
            'deskripsi' => ['nullable', 'string'],
        ];
    }
}

<?php
namespace Modules\Setoran\Http\Requests;
use Illuminate\Foundation\Http\FormRequest;
class SetoranRequest extends FormRequest {
    public function authorize(): bool {
        $item = $this->route('setoran');
        return $this->user()?->hasRole('nasabah') && (!$item || ($item->user_id === $this->user()->id && $item->status === 'Menunggu'));
    }
    public function rules(): array {
        return [
            'jenis_sampah_id' => ['required', 'integer', 'exists:jenis_sampahs,id'],
            'berat_kg' => ['required', 'numeric', 'gt:0', 'decimal:0,2', 'max:999999.99'],
            'tanggal_setor' => ['required', 'date_format:Y-m-d'],
            'catatan' => ['required', 'string'],
            'foto_bukti' => ['nullable', 'image', 'mimes:jpg,jpeg,png', 'extensions:jpg,jpeg,png', 'max:2048'],
        ];
    }
}

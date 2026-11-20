<?php
namespace Modules\Setoran\Http\Requests;
use Illuminate\Foundation\Http\FormRequest;
use Illuminate\Validation\Rule;
class KeputusanRequest extends FormRequest {
    public function authorize(): bool { return $this->user()?->isAdmin() && $this->route('setoran')->status === 'Menunggu'; }
    public function rules(): array { return ['status' => ['required', Rule::in(['Diverifikasi', 'Ditolak'])]]; }
}

<?php
namespace Modules\Setoran\Services;
use Illuminate\Validation\ValidationException;
class NilaiSetoran {
    public static function hitung(string $berat, string $harga): string {
        // Positive amounts: exact decimal multiplication and half-up rounding.
        $total = bcadd(bcmul($berat, $harga, 4), '0.005', 2);
        if (bccomp($total, '999999999999.99', 2) > 0) {
            throw ValidationException::withMessages(['berat_kg' => 'Berat dan harga menghasilkan total melebihi batas transaksi. Kurangi berat setoran.']);
        }
        return $total;
    }
}

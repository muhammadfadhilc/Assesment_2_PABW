<?php
use Illuminate\Support\Facades\Route;
use Modules\JenisSampah\Http\Controllers\JenisSampahController;
Route::middleware('auth')->group(function () {
    Route::get('katalog', [JenisSampahController::class, 'index'])->name('katalog.index');
    Route::middleware('role:admin')->group(function () {
        Route::get('katalog/create', [JenisSampahController::class, 'create'])->name('katalog.create');
        Route::post('katalog', [JenisSampahController::class, 'store'])->name('katalog.store');
        Route::get('katalog/{jenis_sampah}/edit', [JenisSampahController::class, 'edit'])->name('katalog.edit');
        Route::put('katalog/{jenis_sampah}', [JenisSampahController::class, 'update'])->name('katalog.update');
        Route::delete('katalog/{jenis_sampah}', [JenisSampahController::class, 'destroy'])->name('katalog.destroy');
    });
});

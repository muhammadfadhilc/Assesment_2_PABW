<?php
use App\Http\Controllers\DashboardController;
use Illuminate\Support\Facades\Route;
use Inertia\Inertia;
use Laravel\Fortify\Features;
Route::get('/', fn () => Inertia::render('welcome', ['canRegister' => Features::enabled(Features::registration())]))->name('home');
Route::middleware('auth')->group(function () {
    Route::get('/dashboard', DashboardController::class)->name('dashboard');
    Route::get('/profil', fn () => Inertia::render('profile'))->name('profile');
});
require __DIR__.'/settings.php';

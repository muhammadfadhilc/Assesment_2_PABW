<?php
namespace Modules\JenisSampah\Providers;
use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Facades\Route;
class JenisSampahServiceProvider extends ServiceProvider {
    public function boot(): void {
        $this->loadMigrationsFrom(module_path('JenisSampah', 'database/migrations'));
        Route::middleware('web')->group(module_path('JenisSampah', 'routes/web.php'));
    }
}

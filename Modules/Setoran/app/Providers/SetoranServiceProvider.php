<?php
namespace Modules\Setoran\Providers;
use Illuminate\Support\ServiceProvider;
use Illuminate\Support\Facades\Route;
class SetoranServiceProvider extends ServiceProvider {
    public function boot(): void {
        $this->loadMigrationsFrom(module_path('Setoran', 'database/migrations'));
        Route::middleware('web')->group(module_path('Setoran', 'routes/web.php'));
    }
}

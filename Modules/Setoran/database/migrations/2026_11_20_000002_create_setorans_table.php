<?php
use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;
return new class extends Migration {
    public function up(): void {
        Schema::create('setorans', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained()->restrictOnDelete();
            $table->foreignId('jenis_sampah_id')->constrained('jenis_sampahs')->restrictOnDelete();
            $table->decimal('berat_kg', 8, 2);
            $table->date('tanggal_setor');
            $table->text('catatan');
            $table->enum('status', ['Menunggu', 'Diverifikasi', 'Ditolak'])->default('Menunggu');
            $table->string('foto_bukti')->nullable();
            $table->decimal('harga_saat_setor', 12, 2);
            $table->decimal('total_nilai', 14, 2);
            $table->timestamps();
            $table->index(['user_id', 'status']);
        });
    }
    public function down(): void { Schema::dropIfExists('setorans'); }
};

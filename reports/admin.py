from django.contrib import admin

from .models import (
    Report,
    SecurityShift
)


# =========================
# REPORT ADMIN
# =========================
@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):

    list_display = (

        'id',

        'nama_barang',

        'kategori',

        'status',

        'status_verifikasi',

        'created_at'

    )

    list_filter = (

        'status',

        'status_verifikasi',

        'kategori'

    )

    search_fields = (

        'nama_barang',

        'lokasi'

    )


# =========================
# SECURITY SHIFT ADMIN
# =========================
@admin.register(SecurityShift)
class SecurityShiftAdmin(admin.ModelAdmin):

    list_display = (

        'nama_shift',

        'nomor_whatsapp',

        'jam_mulai',

        'jam_selesai',

        'aktif'

    )
from django.db import models
from django.conf import settings
import uuid



# =========================
# REPORT MODEL
# =========================
class Report(models.Model):

    STATUS_CHOICES = (

        ('hilang', 'Kehilangan'),

        ('temuan', 'Temuan'),

        ('selesai', 'Selesai'),

    )

    VERIFIKASI_CHOICES = (

        ('pending', 'Pending'),

        ('approved', 'Approved'),

        ('rejected', 'Rejected'),

    )

    KATEGORI_CHOICES = (

        ('Elektronik', 'Elektronik'),
        ('Fashion', 'Fashion'),
        ('Dokumen', 'Dokumen'),
        ('Aksesoris', 'Aksesoris'),
        ('Tas', 'Tas'),
        ('Dompet', 'Dompet'),
        ('Kunci', 'Kunci'),
        ('Kendaraan', 'Kendaraan'),
        ('Helm', 'Helm'),
        ('Botol Minum', 'Botol Minum'),
        ('Laptop', 'Laptop'),
        ('Handphone', 'Handphone'),
        ('Jam Tangan', 'Jam Tangan'),
        ('Perhiasan', 'Perhiasan'),
        ('Lainnya', 'Lainnya'),

    )

    #
    # USER
    #

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    #
    # DATA BARANG
    #

    nama_barang = models.CharField(
        max_length=255
    )

    kategori = models.CharField(
        max_length=100,
        choices=KATEGORI_CHOICES
    )

    warna = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    merek = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    deskripsi = models.TextField()

    foto_barang = models.ImageField(
        upload_to='barang/',
        blank=True,
        null=True
    )

    #
    # STATUS BARANG
    #

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES
    )

    status_verifikasi = models.CharField(
        max_length=20,
        choices=VERIFIKASI_CHOICES,
        default='pending'
    )

    #
    # LOKASI
    #

    lokasi = models.CharField(
        max_length=255
    )

    latitude = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    longitude = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    tanggal_kejadian = models.DateField()

    #
    # DATA SERAH TERIMA
    #

    nama_penemu = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    nama_penerima = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    petugas_penyerahan = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    lokasi_penyerahan = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    catatan_penyerahan = models.TextField(
        blank=True,
        null=True
    )

    #
    # FILE BUKTI
    #

    ktm_penemu = models.ImageField(
        upload_to='serah_terima/',
        blank=True,
        null=True
    )

    ktm_penerima = models.ImageField(
        upload_to='serah_terima/',
        blank=True,
        null=True
    )

    dokumentasi_penyerahan = models.ImageField(
        upload_to='serah_terima/',
        blank=True,
        null=True
    )

    #
    # TIMESTAMP
    #

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):

        return self.nama_barang

# =========================

#    SHIFT MODEL

# =========================
class SecurityShift(models.Model):

    group_id = models.CharField(
        max_length=100,
        default=uuid.uuid4,
        editable=False
    )

    nama_security = models.CharField(
        max_length=100
    )

    nomor_whatsapp = models.CharField(
        max_length=20
    )

    nama_shift = models.CharField(
        max_length=20,
        choices=(
            ('pagi', 'Pagi'),
            ('sore', 'Sore'),
            ('malam', 'Malam')
        )
    )

    jam_mulai = models.TimeField()

    jam_selesai = models.TimeField()

    tanggal_jaga = models.DateField()

    aktif = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return f"{self.nama_security} - {self.tanggal_jaga}"

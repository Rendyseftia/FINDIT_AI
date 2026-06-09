from datetime import (
    datetime,
    date
)
import uuid


from django.shortcuts import (
    render,
    redirect,
    get_object_or_404
)

from django.http import JsonResponse

from django.contrib.auth.decorators import (
    login_required,
    user_passes_test
)

from rapidfuzz import fuzz

from .models import (
    Report,
    SecurityShift
)

from .services.gemini_service import analyze_image


# =========================
# ADMIN CHECK
# =========================
def admin_required(user):

    return (
        user.is_authenticated
        and user.role == 'admin'
    )


# =========================
# GET ACTIVE SECURITY
# =========================
def get_active_security():

    now = datetime.now()

    current_time = now.time()

    today = date.today()

    shifts = SecurityShift.objects.filter(

        aktif=True,

        tanggal_jaga=today

    )

    active_shift = None

    for shift in shifts:

        #
        # SHIFT NORMAL
        #

        if shift.jam_mulai < shift.jam_selesai:

            if (

                current_time >= shift.jam_mulai
                and
                current_time <= shift.jam_selesai

            ):

                active_shift = shift
                break

        #
        # SHIFT LEWAT TENGAH MALAM
        #

        else:

            if (

                current_time >= shift.jam_mulai
                or
                current_time <= shift.jam_selesai

            ):

                active_shift = shift
                break

    return active_shift


# =========================
# HOME
# =========================
def home(request):

    reports = Report.objects.filter(

        status_verifikasi='approved'

    ).order_by('-id')

    context = {

        'reports': reports

    }

    return render(

        request,

        'index.html',

        context

    )


# =========================
# DETAIL REPORT
# =========================
def detail_report(request, report_id):

    report = get_object_or_404(

        Report,

        id=report_id,

        status_verifikasi='approved'

    )

    #
    # ACTIVE SECURITY
    #

    active_shift = get_active_security()

    #
    # DEFAULT NUMBER
    #

    whatsapp_number = "628000000000"

    security_name = "Security Kampus"

    if active_shift:

        whatsapp_number = (
            active_shift.nomor_whatsapp
        )

        security_name = (
            active_shift.nama_security
        )

    #
    # WHATSAPP MESSAGE
    #

    whatsapp_message = (

        f"Halo {security_name}, "
        f"saya ingin menghubungi "
        f"terkait laporan barang "
        f"'{report.nama_barang}'."

    )

    #
    # WA URL
    #

    whatsapp_url = (

        f"https://wa.me/{whatsapp_number}"
        f"?text={whatsapp_message}"

    )

    #
    # SMART MATCH
    #

    smart_matches = Report.objects.filter(

        kategori=report.kategori,

        status_verifikasi='approved'

    ).exclude(

        id=report.id

    )[:3]

    context = {

        'report': report,

        'smart_matches': smart_matches,

        'whatsapp_url': whatsapp_url,

        'active_shift': active_shift

    }

    return render(

        request,

        'reports/detail.html',

        context

    )


# =========================
# CREATE REPORT
# =========================
@login_required
def create_report(request):

    report_type = request.GET.get(
        'type'
    )

    if request.method == 'POST':

        report = Report.objects.create(

            user=request.user,

            nama_barang=request.POST.get(
                'nama_barang'
            ),

            kategori=request.POST.get(
                'kategori'
            ),

            warna=request.POST.get(
                'warna'
            ),

            merek=request.POST.get(
                'merek'
            ),

            deskripsi=request.POST.get(
                'deskripsi'
            ),

            foto_barang=request.FILES.get(
                'foto_barang'
            ),

            status=request.POST.get(
                'status'
            ),

            lokasi=request.POST.get(
                'lokasi'
            ),

            latitude=request.POST.get(
                'latitude'
            ),

            longitude=request.POST.get(
                'longitude'
            ),

            tanggal_kejadian=request.POST.get(
                'tanggal_kejadian'
            ),

            status_verifikasi='pending'

        )

        return redirect(

            'smartmatch_preview',

            report_id=report.id

        )

    context = {

        'report_type': report_type

    }

    return render(

        request,

        'reports/create.html',

        context

    )


# =========================
# SMART MATCH CHECK
# =========================
@login_required
def smart_match_check(request):

    if request.method != 'POST':

        return JsonResponse({

            'match': False

        })

    nama_barang = (

        request.POST.get(
            'nama_barang',
            ''
        ).strip()

    )

    kategori = (

        request.POST.get(
            'kategori',
            ''
        ).strip()

    )

    if not nama_barang:

        return JsonResponse({

            'match': False

        })

    reports = Report.objects.filter(

        status_verifikasi='approved'

    )

    best_match = None

    highest_score = 0

    for report in reports:

        report_name = (
            report.nama_barang or ''
        ).lower()

        report_category = (
            report.kategori or ''
        ).lower()

        name_score = fuzz.partial_ratio(

            nama_barang.lower(),

            report_name

        )

        category_bonus = 0

        if kategori.lower() == report_category:

            category_bonus = 20

        final_score = (

            name_score +
            category_bonus

        )

        if final_score > 100:

            final_score = 100

        if final_score > highest_score:

            highest_score = final_score

            best_match = report

    if best_match and highest_score >= 40:

        return JsonResponse({

            'match': True,

            'score': int(highest_score),

            'report': {

                'id':
                best_match.id,

                'nama_barang':
                best_match.nama_barang,

                'kategori':
                best_match.kategori,

                'lokasi':
                best_match.lokasi,

                'foto':
                best_match.foto_barang.url
                if best_match.foto_barang
                else ''

            }

        })

    return JsonResponse({

        'match': False

    })


# =========================
# SMARTMATCH PREVIEW
# =========================
@login_required
def smartmatch_preview(request, report_id):

    report = get_object_or_404(

        Report,

        id=report_id

    )

    reports = Report.objects.filter(

        status_verifikasi='approved'

    ).exclude(

        id=report.id

    )

    best_match = None

    highest_score = 0

    for item in reports:

        nama_score = fuzz.partial_ratio(

            report.nama_barang.lower(),

            item.nama_barang.lower()

        )

        kategori_score = 100 if (

            report.kategori.lower()
            ==
            item.kategori.lower()

        ) else 0

        score = (

            nama_score * 0.8 +

            kategori_score * 0.2

        )

        if score > highest_score:

            highest_score = score

            best_match = item

    context = {

        'report': report,

        'best_match': best_match,

        'score': highest_score

    }

    return render(

        request,

        'reports/smartmatch_preview.html',

        context

    )


# =========================
# AI ANALYZE
# =========================
@login_required
def ai_analyze(request):

    
    if request.method != 'POST':

        return JsonResponse({

            'error': 'Invalid request'

        })

    try:

        image = request.FILES.get(
            'foto_barang'
        )

        result = analyze_image(
            image
        )

        return JsonResponse(
            result
        )

    except Exception as e:

        return JsonResponse({

            'error': str(e)

        })


# =========================
# ADMIN DASHBOARD
# =========================
@login_required
@user_passes_test(admin_required)
def admin_dashboard(request):

    pending_reports = Report.objects.filter(

        status_verifikasi='pending'

    ).order_by('-id')

    approved_reports = Report.objects.filter(

        status_verifikasi='approved'

    ).exclude(

        status='selesai'

    ).order_by('-id')

    selesai_reports_list = Report.objects.filter(

        status='selesai'

    ).order_by('-id')

    pending_count = pending_reports.count()

    approved_count = approved_reports.count()

    selesai_reports = selesai_reports_list.count()

    context = {

        'pending_reports':
        pending_reports,

        'approved_reports':
        approved_reports,

        'pending_count':
        pending_count,

        'approved_count':
        approved_count,

        'selesai_reports':
        selesai_reports,

        'selesai_reports_list':
        selesai_reports_list

    }

    return render(

        request,

        'dashboard/admin_dashboard.html',

        context

    )


# =========================
# APPROVE REPORT
# =========================
@login_required
@user_passes_test(admin_required)
def approve_report(request, report_id):

    report = get_object_or_404(

        Report,

        id=report_id

    )

    report.status_verifikasi = 'approved'

    report.save()

    return redirect(
        'admin_dashboard'
    )


# =========================
# REJECT REPORT
# =========================
@login_required
@user_passes_test(admin_required)
def reject_report(request, report_id):

    report = get_object_or_404(

        Report,

        id=report_id

    )

    report.status_verifikasi = 'rejected'

    report.save()

    return redirect(
        'admin_dashboard'
    )


# =========================
# SERAH TERIMA BARANG
# =========================
@login_required
@user_passes_test(admin_required)
def serah_terima_barang(request, report_id):

    report = get_object_or_404(

        Report,

        id=report_id

    )

    if request.method == 'POST':

        report.nama_penemu = request.POST.get(
            'nama_penemu'
        )

        report.nama_penerima = request.POST.get(
            'nama_penerima'
        )

        report.petugas_penyerahan = (
            request.user.nama_lengkap
        )

        report.lokasi_penyerahan = request.POST.get(
            'lokasi_penyerahan'
        )

        report.catatan_penyerahan = request.POST.get(
            'catatan_penyerahan'
        )

        if request.FILES.get('ktm_penemu'):

            report.ktm_penemu = request.FILES.get(
                'ktm_penemu'
            )

        if request.FILES.get('ktm_penerima'):

            report.ktm_penerima = request.FILES.get(
                'ktm_penerima'
            )

        if request.FILES.get('dokumentasi_penyerahan'):

            report.dokumentasi_penyerahan = request.FILES.get(
                'dokumentasi_penyerahan'
            )

        report.status = 'selesai'

        report.save()

        return redirect(
            'admin_dashboard'
        )

    return redirect(
        'admin_dashboard'
    )


# =========================
# DELETE REPORT
# =========================
@login_required
@user_passes_test(admin_required)
def delete_report(request, report_id):

    report = get_object_or_404(

        Report,

        id=report_id

    )

    report.delete()

    return redirect(
        'admin_dashboard'
    )


# =========================
# SECURITY SHIFT DASHBOARD
# =========================
@login_required
@user_passes_test(admin_required)
def security_shift_dashboard(request):
    groups = {}

    shifts = SecurityShift.objects.all().order_by(
        'tanggal_jaga'
    )

    for shift in shifts:

        if shift.group_id not in groups:

            groups[shift.group_id] = {

                'id': shift.id,

                'group_id': shift.group_id,

                'nama_security': shift.nama_security,

                'nama_shift': shift.nama_shift,

                'nomor_whatsapp': shift.nomor_whatsapp,

                'jam_mulai': shift.jam_mulai,

                'jam_selesai': shift.jam_selesai,

                'aktif': shift.aktif,

                'tanggal_list': []

            }

        groups[shift.group_id]['tanggal_list'].append(
            shift.tanggal_jaga
        )

    context = {

        'shifts': groups.values()

    }

    return render(

        request,

        'dashboard/security_shift.html',

        context

    )



# =========================
# ADD SECURITY SHIFT
# =========================
@login_required
@user_passes_test(admin_required)
def add_security_shift(request):

    if request.method == 'POST':

        nama_security = request.POST.get(
            'nama_security'
        )

        nama_shift = request.POST.get(
            'nama_shift'
        )

        nomor_whatsapp = request.POST.get(
            'nomor_whatsapp'
        )

        jam_mulai = request.POST.get(
            'jam_mulai'
        )

        jam_selesai = request.POST.get(
            'jam_selesai'
        )

        tanggal_input = request.POST.get(
            'tanggal_jaga'
        )

        aktif = bool(
            request.POST.get('aktif')
        )

        tanggal_list = [
            t.strip()
            for t in tanggal_input.split(',')
            if t.strip()
        ]

        group_id = str(
            uuid.uuid4()
        )

        for tanggal in tanggal_list:

            SecurityShift.objects.create(

                group_id=group_id,

                nama_security=nama_security,

                nama_shift=nama_shift,

                nomor_whatsapp=nomor_whatsapp,

                jam_mulai=jam_mulai,

                jam_selesai=jam_selesai,

                tanggal_jaga=tanggal,

                aktif=aktif

            )

        return redirect(
            'security_shift_dashboard'
        )

    return render(
        request,
        'dashboard/add_security_shift.html'
    )


# =========================
# EDIT SECURITY SHIFT
# =========================
@login_required
@user_passes_test(admin_required)
def edit_security_shift(request, shift_id):

    shift = get_object_or_404(
        SecurityShift,
        id=shift_id
    )

    related_shifts = SecurityShift.objects.filter(
        group_id=shift.group_id
    ).order_by(
        'tanggal_jaga'
    )

    tanggal_jaga = ",".join(
        [
            str(item.tanggal_jaga)
            for item in related_shifts
        ]
    )

    if request.method == 'POST':

        nama_security = request.POST.get(
            'nama_security'
        )

        nama_shift = request.POST.get(
            'nama_shift'
        )

        nomor_whatsapp = request.POST.get(
            'nomor_whatsapp'
        )

        jam_mulai = request.POST.get(
            'jam_mulai'
        )

        jam_selesai = request.POST.get(
            'jam_selesai'
        )

        tanggal_input = request.POST.get(
            'tanggal_jaga',
            ''
        )

        aktif = bool(
            request.POST.get('aktif')
        )

        tanggal_list = [
            t.strip()
            for t in tanggal_input.split(',')
            if t.strip()
        ]

        group_id = shift.group_id

        related_shifts.delete()

        for tanggal in tanggal_list:

            SecurityShift.objects.create(

                group_id=group_id,

                nama_security=nama_security,

                nama_shift=nama_shift,

                nomor_whatsapp=nomor_whatsapp,

                jam_mulai=jam_mulai,

                jam_selesai=jam_selesai,

                tanggal_jaga=tanggal,

                aktif=aktif

            )

        return redirect(
            'security_shift_dashboard'
        )

    context = {

        'shift': shift,

        'tanggal_jaga': tanggal_jaga

    }

    return render(

        request,

        'dashboard/edit_security_shift.html',

        context

    )



# =========================
# DELETE SECURITY SHIFT
# =========================
@login_required
@user_passes_test(admin_required)
def delete_security_shift(request, shift_id):


    shift = get_object_or_404(
        SecurityShift,
        id=shift_id
    )

    SecurityShift.objects.filter(
        group_id=shift.group_id
    ).delete()

    return redirect(
        'security_shift_dashboard'
    )


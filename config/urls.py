from django.contrib import admin
from django.urls import (
    path,
    include
)

from django.conf import settings
from django.conf.urls.static import static

from reports.views import (

    #
    # MAIN
    #
    home,
    create_report,
    detail_report,

    #
    # ADMIN
    #
    admin_dashboard,
    approve_report,
    reject_report,
    serah_terima_barang,
    delete_report,

    #
    # AI
    #
    ai_analyze,

    #
    # SMART MATCH
    #
    smart_match_check,
    smartmatch_preview,

    #
    # SECURITY SHIFT
    #
    security_shift_dashboard,
    add_security_shift,
    edit_security_shift,
    delete_security_shift

)

urlpatterns = [

    # =========================
    # DJANGO ADMIN
    # =========================

    path(
        'admin/',
        admin.site.urls
    ),

    # =========================
    # HOME
    # =========================

    path(
        '',
        home,
        name='home'
    ),

    # =========================
    # REPORT
    # =========================

    path(
        'laporan/create/',
        create_report,
        name='create_report'
    ),

    path(
        'laporan/<int:report_id>/',
        detail_report,
        name='detail_report'
    ),

    # =========================
    # SMART MATCH
    # =========================

    path(
        'smart-match-check/',
        smart_match_check,
        name='smart_match_check'
    ),

    path(
        'smartmatch/<int:report_id>/',
        smartmatch_preview,
        name='smartmatch_preview'
    ),

    # =========================
    # AI ANALYZE
    # =========================

    path(
        'ai/analyze/',
        ai_analyze,
        name='ai_analyze'
    ),

    # =========================
    # ADMIN DASHBOARD
    # =========================

    path(
        'dashboard/admin/',
        admin_dashboard,
        name='admin_dashboard'
    ),

    path(
        'dashboard/admin/approve/<int:report_id>/',
        approve_report,
        name='approve_report'
    ),

    path(
        'dashboard/admin/reject/<int:report_id>/',
        reject_report,
        name='reject_report'
    ),

    #
    # SERAH TERIMA
    #

    path(
        'dashboard/admin/serah-terima/<int:report_id>/',
        serah_terima_barang,
        name='serah_terima_barang'
    ),

    #
    # DELETE REPORT
    #

    path(
        'dashboard/admin/delete/<int:report_id>/',
        delete_report,
        name='delete_report'
    ),

    # =========================
    # SECURITY SHIFT
    # =========================

    path(
        'dashboard/security/',
        security_shift_dashboard,
        name='security_shift_dashboard'
    ),

    path(
        'dashboard/security/add/',
        add_security_shift,
        name='add_security_shift'
    ),

    path(
        'dashboard/security/edit/<int:shift_id>/',
        edit_security_shift,
        name='edit_security_shift'
    ),

    path(
        'dashboard/security/delete/<int:shift_id>/',
        delete_security_shift,
        name='delete_security_shift'
    ),

    # =========================
    # ACCOUNTS
    # =========================

    path(
        '',
        include('accounts.urls')
    ),

]

# =========================
# MEDIA FILES
# =========================

if settings.DEBUG:

    urlpatterns += static(

        settings.MEDIA_URL,

        document_root=settings.MEDIA_ROOT

    )
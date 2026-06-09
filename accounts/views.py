from django.shortcuts import (
    render,
    redirect
)

from django.contrib.auth import (
    authenticate,
    login,
    logout
)

from django.contrib import messages

from django.utils import timezone

from datetime import timedelta

from django.contrib.auth.hashers import (
    make_password
)

import random

from .models import User

from .services.fonnte_service import (
    send_whatsapp_otp
)


# =========================
# REGISTER
# =========================
def register_view(request):

    #
    # SUDAH LOGIN
    #

    if request.user.is_authenticated:

        #
        # ADMIN
        #

        if request.user.role == 'admin':

            return redirect(
                'admin_dashboard'
            )

        #
        # USER
        #

        return redirect(
            'home'
        )

    #
    # REGISTER
    #

    if request.method == 'POST':

        nama_lengkap = request.POST.get(
            'nama_lengkap'
        )

        no_whatsapp = request.POST.get(
            'no_whatsapp'
        )

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        #
        # PASSWORD TIDAK COCOK
        #

        if password != confirm_password:

            messages.error(

                request,

                'Konfirmasi password tidak cocok.'

            )

            return redirect(
                'register'
            )

        #
        # FORMAT NOMOR
        #

        if no_whatsapp.startswith('08'):

            no_whatsapp = (
                '62' +
                no_whatsapp[1:]
            )

        #
        # USERNAME SUDAH ADA
        #

        if User.objects.filter(
            username=username
        ).exists():

            messages.error(

                request,

                'Username sudah digunakan.'

            )

            return redirect(
                'register'
            )

        #
        # NOMOR SUDAH ADA
        #

        if User.objects.filter(
            no_whatsapp=no_whatsapp
        ).exists():

            messages.error(

                request,

                'Nomor WhatsApp sudah digunakan.'

            )

            return redirect(
                'register'
            )

        #
        # CREATE USER
        #

        User.objects.create_user(

            username=username,

            password=password,

            nama_lengkap=nama_lengkap,

            no_whatsapp=no_whatsapp,

            role='user'

        )

        #
        # SUCCESS
        #

        messages.success(

            request,

            'Register berhasil. Silakan login.'

        )

        return redirect(
            'login'
        )

    return render(
        request,
        'auth/register.html'
    )


# =========================
# LOGIN
# =========================
def login_view(request):

    #
    # SUDAH LOGIN
    #

    if request.user.is_authenticated:

        #
        # ADMIN
        #

        if request.user.role == 'admin':

            return redirect(
                'admin_dashboard'
            )

        #
        # USER
        #

        return redirect(
            'home'
        )

    #
    # LOGIN
    #

    if request.method == 'POST':

        username = request.POST.get(
            'username'
        )

        password = request.POST.get(
            'password'
        )

        #
        # AUTHENTICATE
        #

        user = authenticate(

            request,

            username=username,

            password=password

        )

        #
        # LOGIN SUCCESS
        #

        if user is not None:

            login(
                request,
                user
            )

            #
            # ADMIN REDIRECT
            #

            if user.role == 'admin':

                return redirect(
                    'admin_dashboard'
                )

            #
            # USER REDIRECT
            #

            return redirect(
                'home'
            )

        #
        # LOGIN FAILED
        #

        messages.error(

            request,

            'Username atau password salah.'

        )

        return redirect(
            'login'
        )

    return render(
        request,
        'auth/login.html'
    )


# =========================
# FORGOT PASSWORD
# =========================
def forgot_password(request):

    if request.method == 'POST':

        no_whatsapp = request.POST.get(
            'no_whatsapp'
        )

        #
        # FORMAT NOMOR
        #

        if no_whatsapp.startswith('08'):

            no_whatsapp = (
                '62' +
                no_whatsapp[1:]
            )

        #
        # CARI USER
        #

        user = User.objects.filter(
            no_whatsapp=no_whatsapp
        ).first()

        #
        # USER TIDAK DITEMUKAN
        #

        if not user:

            messages.error(

                request,

                'Nomor WhatsApp tidak ditemukan.'

            )

            return redirect(
                'forgot_password'
            )

        #
        # GENERATE OTP
        #

        otp = str(

            random.randint(
                100000,
                999999
            )

        )

        #
        # SAVE OTP
        #

        user.otp_code = otp

        user.otp_expired = (

            timezone.now()
            +
            timedelta(minutes=5)

        )

        user.save()

        #
        # SEND OTP
        #

        send_whatsapp_otp(

            user.no_whatsapp,

            otp

        )

        #
        # SAVE SESSION
        #

        request.session[
            'reset_user_id'
        ] = user.id

        #
        # SUCCESS
        #

        messages.success(

            request,

            'Kode OTP berhasil dikirim ke WhatsApp.'

        )

        return redirect(
            'verify_otp'
        )

    return render(
        request,
        'auth/forgot_password.html'
    )


# =========================
# VERIFY OTP
# =========================
def verify_otp(request):

    user_id = request.session.get(
        'reset_user_id'
    )

    #
    # NO SESSION
    #

    if not user_id:

        return redirect(
            'forgot_password'
        )

    user = User.objects.get(
        id=user_id
    )

    if request.method == 'POST':

        otp = request.POST.get(
            'otp'
        )

        #
        # OTP SALAH
        #

        if user.otp_code != otp:

            messages.error(

                request,

                'Kode OTP salah.'

            )

            return redirect(
                'verify_otp'
            )

        #
        # OTP EXPIRED
        #

        if timezone.now() > user.otp_expired:

            messages.error(

                request,

                'Kode OTP expired.'

            )

            return redirect(
                'verify_otp'
            )

        return redirect(
            'reset_password'
        )

    return render(
        request,
        'auth/verify_otp.html'
    )


# =========================
# RESET PASSWORD
# =========================
def reset_password(request):

    user_id = request.session.get(
        'reset_user_id'
    )

    #
    # NO SESSION
    #

    if not user_id:

        return redirect(
            'forgot_password'
        )

    user = User.objects.get(
        id=user_id
    )

    if request.method == 'POST':

        password = request.POST.get(
            'password'
        )

        confirm_password = request.POST.get(
            'confirm_password'
        )

        #
        # PASSWORD TIDAK COCOK
        #

        if password != confirm_password:

            messages.error(

                request,

                'Konfirmasi password tidak cocok.'

            )

            return redirect(
                'reset_password'
            )

        #
        # UPDATE PASSWORD
        #

        user.password = make_password(
            password
        )

        #
        # CLEAR OTP
        #

        user.otp_code = None

        user.otp_expired = None

        user.save()

        #
        # CLEAR SESSION
        #

        if 'reset_user_id' in request.session:

            del request.session[
                'reset_user_id'
            ]

        #
        # SUCCESS
        #

        messages.success(

            request,

            'Password berhasil diubah. Silakan login.'

        )

        return redirect(
            'login'
        )

    return render(
        request,
        'auth/reset_password.html'
    )


# =========================
# LOGOUT
# =========================
def logout_view(request):

    logout(request)

    return redirect(
        'home'
    )
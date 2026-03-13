from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.app.services.supabase_service import supabase_service
import re

auth_bp = Blueprint('auth', __name__)
supabase = supabase_service.get_client()

@auth_bp.route("/")
def inicio():
    return redirect(url_for("auth.login"))

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            user = response.user
            session["user_id"] = user.id
            session["email"] = user.email

            flash("Inicio de sesión correcto", "success")
            return redirect(url_for("dashboard.dashboard_view"))

        except Exception as e:
            flash(f"Error al iniciar sesión: {str(e)}", "error")
            return redirect(url_for("auth.login"))

    return render_template("auth/login.html")

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html")

    nombre = request.form.get("nombre", "").strip()
    tipo_ingreso = request.form.get("tipo_ingreso", "").strip()
    meta_ahorro = request.form.get("meta_ahorro", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        flash("El correo no tiene un formato válido", "warning")
        return redirect(url_for("auth.register"))

    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        user = response.user

        if user:
            supabase.table("profiles").insert({
                "user_id": user.id,
                "nombre": nombre,
                "tipo_ingreso": tipo_ingreso,
                "meta_ahorro": float(meta_ahorro)
            }).execute()

        flash("Usuario registrado correctamente. Ahora inicia sesión.", "success")
        return redirect(url_for("auth.login"))

    except Exception as e:
        error_texto = str(e)
        if "email rate limit exceeded" in error_texto.lower():
            flash("Demasiados intentos. Espera unos minutos.", "warning")
        else:
            flash(f"Error al registrarse: {error_texto}", "error")

        return redirect(url_for("auth.register"))

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente", "info")
    return redirect(url_for("auth.login"))

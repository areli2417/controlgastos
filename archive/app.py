from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os
import re

load_dotenv()

app = Flask(__name__)

app.secret_key = os.getenv("SECRET_KEY")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.route("/")
def inicio():
    return redirect(url_for("login"))


# -----------------------------
# LOGIN
# -----------------------------
@app.route("/login", methods=["GET", "POST"])
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

            flash("Inicio de sesión correcto")
            return redirect(url_for("dashboard"))

        except Exception as e:
            flash(f"Error al iniciar sesión: {str(e)}")
            return redirect(url_for("login"))

    return render_template("login.html")


# -----------------------------
# REGISTER
# -----------------------------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    nombre = request.form.get("nombre", "").strip()
    tipo_ingreso = request.form.get("tipo_ingreso", "").strip()
    meta_ahorro = request.form.get("meta_ahorro", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "").strip()

    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        flash("El correo no tiene un formato válido")
        return redirect(url_for("register"))

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

        flash("Usuario registrado correctamente. Ahora inicia sesión.")
        return redirect(url_for("login"))

    except Exception as e:
        error_texto = str(e)

        if "email rate limit exceeded" in error_texto.lower():
            flash("Demasiados intentos en poco tiempo. Espera unos minutos o revisa la configuración de email en Supabase.")
        else:
            flash(f"Error al registrarse: {error_texto}")

        return redirect(url_for("register"))


# -----------------------------
# DASHBOARD
# -----------------------------
@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    filtro = request.args.get("filtro", "todos")
    seccion = request.args.get("seccion", "perfil")

    try:
        perfil_resp = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        ingresos_resp = supabase.table("incomes").select("*").eq("user_id", user_id).execute()
        gastos_resp = supabase.table("expenses").select("*").eq("user_id", user_id).execute()
        ahorros_resp = supabase.table("savings").select("*").eq("user_id", user_id).execute()

        perfil = perfil_resp.data[0] if perfil_resp.data else None
        ingresos = ingresos_resp.data if ingresos_resp.data else []
        gastos = gastos_resp.data if gastos_resp.data else []
        ahorros = ahorros_resp.data if ahorros_resp.data else []

        hoy = datetime.today().date()

        def aplicar_filtro(registros):
            if filtro == "todos":
                return registros

            filtrados = []

            for registro in registros:
                fecha_texto = registro.get("fecha")
                if not fecha_texto:
                    continue

                fecha_registro = datetime.strptime(fecha_texto, "%Y-%m-%d").date()

                if filtro == "semana":
                    inicio_semana = hoy - timedelta(days=hoy.weekday())
                    if fecha_registro >= inicio_semana:
                        filtrados.append(registro)

                elif filtro == "quincena":
                    if hoy.day <= 15:
                        inicio_quincena = hoy.replace(day=1)
                        fin_quincena = hoy.replace(day=15)
                    else:
                        inicio_quincena = hoy.replace(day=16)
                        fin_quincena = hoy

                    if inicio_quincena <= fecha_registro <= fin_quincena:
                        filtrados.append(registro)

                elif filtro == "mes":
                    if fecha_registro.year == hoy.year and fecha_registro.month == hoy.month:
                        filtrados.append(registro)

            return filtrados

        ingresos = aplicar_filtro(ingresos)
        gastos = aplicar_filtro(gastos)
        ahorros = aplicar_filtro(ahorros)

        total_ingresos = sum(float(i["monto"]) for i in ingresos)
        total_gastos = sum(float(g["monto"]) for g in gastos)
        total_ahorros = sum(float(a["monto"]) for a in ahorros)

        disponible = total_ingresos - total_gastos - total_ahorros

        gastos_por_categoria = {}
        for gasto in gastos:
            categoria = gasto["categoria"]
            monto = float(gasto["monto"])

            if categoria in gastos_por_categoria:
                gastos_por_categoria[categoria] += monto
            else:
                gastos_por_categoria[categoria] = monto

        porcentaje_meta = 0
        ingreso_mensual_estimado = 0

        if perfil and perfil.get("meta_ahorro"):
            meta = float(perfil["meta_ahorro"])
            if meta > 0:
                porcentaje_meta = min((total_ahorros / meta) * 100, 100)

        if perfil and perfil.get("tipo_ingreso"):
            if perfil["tipo_ingreso"] == "semanal":
                ingreso_mensual_estimado = total_ingresos * 4
            elif perfil["tipo_ingreso"] == "quincenal":
                ingreso_mensual_estimado = total_ingresos * 2

        return render_template(
            "dashboard.html",
            email=session.get("email"),
            perfil=perfil,
            ingresos=ingresos,
            gastos=gastos,
            ahorros=ahorros,
            total_ingresos=total_ingresos,
            total_gastos=total_gastos,
            total_ahorros=total_ahorros,
            disponible=disponible,
            gastos_por_categoria=gastos_por_categoria,
            porcentaje_meta=porcentaje_meta,
            ingreso_mensual_estimado=ingreso_mensual_estimado,
            filtro=filtro,
            seccion=seccion
        )

    except Exception as e:
        flash(f"Error al cargar dashboard: {str(e)}")
        return redirect(url_for("login"))

# -----------------------------
# GUARDAR INGRESO
# -----------------------------
@app.route("/guardar_ingreso", methods=["POST"])
def guardar_ingreso():
    if "user_id" not in session:
        return redirect(url_for("login"))

    monto = request.form.get("monto", "").strip()
    tipo_periodo = request.form.get("tipo_periodo", "").strip()
    fecha = request.form.get("fecha", "").strip()

    try:
        supabase.table("incomes").insert({
            "user_id": session["user_id"],
            "monto": float(monto),
            "tipo_periodo": tipo_periodo,
            "fecha": fecha
        }).execute()

        flash("Ingreso guardado correctamente.")

    except Exception as e:
        flash(f"Error al guardar ingreso: {str(e)}")

    return redirect(url_for("dashboard"))


# -----------------------------
# GUARDAR GASTO
# -----------------------------
@app.route("/guardar_gasto", methods=["POST"])
def guardar_gasto():
    if "user_id" not in session:
        return redirect(url_for("login"))

    categoria = request.form.get("categoria", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    monto = request.form.get("monto", "").strip()
    fecha = request.form.get("fecha", "").strip()

    try:
        supabase.table("expenses").insert({
            "user_id": session["user_id"],
            "categoria": categoria,
            "descripcion": descripcion,
            "monto": float(monto),
            "fecha": fecha
        }).execute()

        flash("Gasto guardado correctamente.")

    except Exception as e:
        flash(f"Error al guardar gasto: {str(e)}")

    return redirect(url_for("dashboard"))
# -----------------------------
# EDITAR GASTO
# -----------------------------
@app.route("/editar_gasto/<id>", methods=["GET", "POST"])
def editar_gasto(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        categoria = request.form.get("categoria", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        monto = request.form.get("monto", "").strip()
        fecha = request.form.get("fecha", "").strip()

        try:
            supabase.table("expenses").update({
                "categoria": categoria,
                "descripcion": descripcion,
                "monto": float(monto),
                "fecha": fecha
            }).eq("id", id).eq("user_id", session["user_id"]).execute()

            flash("Gasto actualizado correctamente.")
            return redirect(url_for("dashboard"))

        except Exception as e:
            flash(f"Error al actualizar gasto: {str(e)}")
            return redirect(url_for("editar_gasto", id=id))

    try:
        respuesta = supabase.table("expenses").select("*").eq("id", id).eq("user_id", session["user_id"]).execute()

        if not respuesta.data:
            flash("Gasto no encontrado.")
            return redirect(url_for("dashboard"))

        gasto = respuesta.data[0]
        return render_template("editar_gasto.html", gasto=gasto)

    except Exception as e:
        flash(f"Error al cargar gasto: {str(e)}")
        return redirect(url_for("dashboard"))

# -----------------------------
# EDITAR INGRESO
# -----------------------------
@app.route("/editar_ingreso/<id>", methods=["GET", "POST"])
def editar_ingreso(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        monto = request.form.get("monto", "").strip()
        tipo_periodo = request.form.get("tipo_periodo", "").strip()
        fecha = request.form.get("fecha", "").strip()

        try:
            supabase.table("incomes").update({
                "monto": float(monto),
                "tipo_periodo": tipo_periodo,
                "fecha": fecha
            }).eq("id", id).eq("user_id", session["user_id"]).execute()

            flash("Ingreso actualizado correctamente.")
            return redirect(url_for("dashboard"))

        except Exception as e:
            flash(f"Error al actualizar ingreso: {str(e)}")
            return redirect(url_for("editar_ingreso", id=id))

    try:
        respuesta = supabase.table("incomes").select("*").eq("id", id).eq("user_id", session["user_id"]).execute()

        if not respuesta.data:
            flash("Ingreso no encontrado.")
            return redirect(url_for("dashboard"))

        ingreso = respuesta.data[0]
        return render_template("editar_ingreso.html", ingreso=ingreso)

    except Exception as e:
        flash(f"Error al cargar ingreso: {str(e)}")
        return redirect(url_for("dashboard"))

# -----------------------------
# EDITAR AHORRO
# -----------------------------
@app.route("/editar_ahorro/<id>", methods=["GET", "POST"])
def editar_ahorro(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        monto = request.form.get("monto", "").strip()
        fecha = request.form.get("fecha", "").strip()

        try:
            supabase.table("savings").update({
                "monto": float(monto),
                "fecha": fecha
            }).eq("id", id).eq("user_id", session["user_id"]).execute()

            flash("Ahorro actualizado correctamente.")
            return redirect(url_for("dashboard"))

        except Exception as e:
            flash(f"Error al actualizar ahorro: {str(e)}")
            return redirect(url_for("editar_ahorro", id=id))

    try:
        respuesta = supabase.table("savings").select("*").eq("id", id).eq("user_id", session["user_id"]).execute()

        if not respuesta.data:
            flash("Ahorro no encontrado.")
            return redirect(url_for("dashboard"))

        ahorro = respuesta.data[0]
        return render_template("editar_ahorro.html", ahorro=ahorro)

    except Exception as e:
        flash(f"Error al cargar ahorro: {str(e)}")
        return redirect(url_for("dashboard"))


# -----------------------------
# GUARDAR AHORRO
# -----------------------------
@app.route("/guardar_ahorro", methods=["POST"])
def guardar_ahorro():
    if "user_id" not in session:
        return redirect(url_for("login"))

    monto = request.form.get("monto", "").strip()
    fecha = request.form.get("fecha", "").strip()

    try:
        supabase.table("savings").insert({
            "user_id": session["user_id"],
            "monto": float(monto),
            "fecha": fecha
        }).execute()

        flash("Ahorro guardado correctamente.")

    except Exception as e:
        flash(f"Error al guardar ahorro: {str(e)}")

    return redirect(url_for("dashboard"))

    # -----------------------------
# ELIMINAR INGRESO
# -----------------------------
@app.route("/eliminar_ingreso/<id>", methods=["POST"])
def eliminar_ingreso(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        supabase.table("incomes").delete().eq("id", id).eq("user_id", session["user_id"]).execute()
        flash("Ingreso eliminado correctamente.")
    except Exception as e:
        flash(f"Error al eliminar ingreso: {str(e)}")

    return redirect(url_for("dashboard"))


# -----------------------------
# ELIMINAR GASTO
# -----------------------------
@app.route("/eliminar_gasto/<id>", methods=["POST"])
def eliminar_gasto(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        supabase.table("expenses").delete().eq("id", id).eq("user_id", session["user_id"]).execute()
        flash("Gasto eliminado correctamente.")
    except Exception as e:
        flash(f"Error al eliminar gasto: {str(e)}")

    return redirect(url_for("dashboard"))


# -----------------------------
# ELIMINAR AHORRO
# -----------------------------
@app.route("/eliminar_ahorro/<id>", methods=["POST"])
def eliminar_ahorro(id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    try:
        supabase.table("savings").delete().eq("id", id).eq("user_id", session["user_id"]).execute()
        flash("Ahorro eliminado correctamente.")
    except Exception as e:
        flash(f"Error al eliminar ahorro: {str(e)}")

    return redirect(url_for("dashboard"))


# -----------------------------
# LOGOUT
# -----------------------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente")
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)
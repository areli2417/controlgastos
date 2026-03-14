from flask import Blueprint, request, redirect, url_for, session, flash, render_template
from backend.app.services.supabase_service import supabase_service

transactions_bp = Blueprint('transactions', __name__)
supabase = supabase_service.get_client()

# --- INGRESOS ---
@transactions_bp.route("/guardar_ingreso", methods=["POST"])
def guardar_ingreso():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    monto = request.form.get("monto")
    tipo_periodo = request.form.get("tipo_periodo")
    fecha = request.form.get("fecha")
    try:
        supabase.table("incomes").insert({"user_id": session["user_id"], "monto": float(monto), "tipo_periodo": tipo_periodo, "fecha": fecha}).execute()
        flash("Ingreso guardado correctamente.", "success")
    except Exception as e: flash(f"Error: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_view"))

@transactions_bp.route("/editar_ingreso/<id>", methods=["GET", "POST"])
def editar_ingreso(id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    if request.method == "POST":
        monto = request.form.get("monto")
        tipo_periodo = request.form.get("tipo_periodo")
        fecha = request.form.get("fecha")
        try:
            supabase.table("incomes").update({"monto": float(monto), "tipo_periodo": tipo_periodo, "fecha": fecha}).eq("id", id).eq("user_id", session["user_id"]).execute()
            flash("Ingreso actualizado.", "success")
            return redirect(url_for("dashboard.dashboard_view"))
        except Exception as e: flash(f"Error: {str(e)}", "error")
    
    resp = supabase.table("incomes").select("*").eq("id", id).eq("user_id", session["user_id"]).execute()
    if not resp.data: return redirect(url_for("dashboard.dashboard_view"))
    return render_template("transactions/editar_ingreso.html", ingreso=resp.data[0])

@transactions_bp.route("/eliminar_ingreso/<id>", methods=["POST"])
def eliminar_ingreso(id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    try:
        supabase.table("incomes").delete().eq("id", id).eq("user_id", session["user_id"]).execute()
        flash("Ingreso eliminado.", "info")
    except Exception as e: flash(f"Error: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_view"))

# --- GASTOS ---
@transactions_bp.route("/guardar_gasto", methods=["POST"])
def guardar_gasto():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    try:
        supabase.table("expenses").insert({
            "user_id": session["user_id"],
            "categoria": request.form.get("categoria"),
            "descripcion": request.form.get("descripcion"),
            "monto": float(request.form.get("monto")),
            "fecha": request.form.get("fecha")
        }).execute()
        flash("Gasto guardado.", "success")
    except Exception as e: flash(f"Error: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_view"))

@transactions_bp.route("/editar_gasto/<id>", methods=["GET", "POST"])
def editar_gasto(id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    if request.method == "POST":
        try:
            supabase.table("expenses").update({
                "categoria": request.form.get("categoria"),
                "descripcion": request.form.get("descripcion"),
                "monto": float(request.form.get("monto")),
                "fecha": request.form.get("fecha")
            }).eq("id", id).eq("user_id", session["user_id"]).execute()
            flash("Gasto actualizado.", "success")
            return redirect(url_for("dashboard.dashboard_view"))
        except Exception as e: flash(f"Error: {str(e)}", "error")

    resp = supabase.table("expenses").select("*").eq("id", id).eq("user_id", session["user_id"]).execute()
    if not resp.data: return redirect(url_for("dashboard.dashboard_view"))
    return render_template("transactions/editar_gasto.html", gasto=resp.data[0])

@transactions_bp.route("/eliminar_gasto/<id>", methods=["POST"])
def eliminar_gasto(id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    try:
        supabase.table("expenses").delete().eq("id", id).eq("user_id", session["user_id"]).execute()
        flash("Gasto eliminado.", "info")
    except Exception as e: flash(f"Error: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_view"))

# --- AHORROS ---
@transactions_bp.route("/guardar_ahorro", methods=["POST"])
def guardar_ahorro():
    if "user_id" not in session: return redirect(url_for("auth.login"))
    try:
        supabase.table("savings").insert({
            "user_id": session["user_id"],
            "monto": float(request.form.get("monto")),
            "fecha": request.form.get("fecha")
        }).execute()
        flash("Ahorro guardado.", "success")
    except Exception as e: flash(f"Error: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_view"))

@transactions_bp.route("/editar_ahorro/<id>", methods=["GET", "POST"])
def editar_ahorro(id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    if request.method == "POST":
        try:
            supabase.table("savings").update({
                "monto": float(request.form.get("monto")),
                "fecha": request.form.get("fecha")
            }).eq("id", id).eq("user_id", session["user_id"]).execute()
            flash("Ahorro actualizado.", "success")
            return redirect(url_for("dashboard.dashboard_view"))
        except Exception as e: flash(f"Error: {str(e)}", "error")

    resp = supabase.table("savings").select("*").eq("id", id).eq("user_id", session["user_id"]).execute()
    if not resp.data: return redirect(url_for("dashboard.dashboard_view"))
    return render_template("transactions/editar_ahorro.html", ahorro=resp.data[0])

@transactions_bp.route("/eliminar_ahorro/<id>", methods=["POST"])
def eliminar_ahorro(id):
    if "user_id" not in session: return redirect(url_for("auth.login"))
    try:
        supabase.table("savings").delete().eq("id", id).eq("user_id", session["user_id"]).execute()
        flash("Ahorro eliminado.", "info")
    except Exception as e: flash(f"Error: {str(e)}", "error")
    return redirect(url_for("dashboard.dashboard_view"))

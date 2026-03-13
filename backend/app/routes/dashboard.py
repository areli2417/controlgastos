from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend.app.services.supabase_service import supabase_service
from backend.app.utils.filters import aplicar_filtro_fechas
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)
supabase = supabase_service.get_client()

@dashboard_bp.route("/dashboard")
def dashboard_view():
    if "user_id" not in session:
        return redirect(url_for("auth.login"))

    user_id = session["user_id"]
    filtro = request.args.get("filtro", "todos")
    seccion = request.args.get("seccion", "resumen") # Ajustado a resumen por defecto

    try:
        # Consultas a Supabase
        perfil_resp = supabase.table("profiles").select("*").eq("user_id", user_id).execute()
        ingresos_resp = supabase.table("incomes").select("*").eq("user_id", user_id).execute()
        gastos_resp = supabase.table("expenses").select("*").eq("user_id", user_id).execute()
        ahorros_resp = supabase.table("savings").select("*").eq("user_id", user_id).execute()

        perfil = perfil_resp.data[0] if perfil_resp.data else None
        
        # Aplicar filtros
        ingresos = aplicar_filtro_fechas(ingresos_resp.data if ingresos_resp.data else [], filtro)
        gastos = aplicar_filtro_fechas(gastos_resp.data if gastos_resp.data else [], filtro)
        ahorros = aplicar_filtro_fechas(ahorros_resp.data if ahorros_resp.data else [], filtro)

        # Cálculos de negocio
        total_ingresos = sum(float(i["monto"]) for i in ingresos)
        total_gastos = sum(float(g["monto"]) for g in gastos)
        total_ahorros = sum(float(a["monto"]) for a in ahorros)
        disponible = total_ingresos - total_gastos - total_ahorros

        gastos_por_categoria = {}
        for gasto in gastos:
            cat = gasto["categoria"]
            monto = float(gasto["monto"])
            gastos_por_categoria[cat] = gastos_por_categoria.get(cat, 0) + monto

        porcentaje_meta = 0
        if perfil and perfil.get("meta_ahorro"):
            meta = float(perfil["meta_ahorro"])
            if meta > 0:
                porcentaje_meta = min((total_ahorros / meta) * 100, 100)

        ingreso_mensual_estimado = 0
        if perfil and perfil.get("tipo_ingreso"):
            if perfil["tipo_ingreso"] == "semanal":
                ingreso_mensual_estimado = total_ingresos * 4
            elif perfil["tipo_ingreso"] == "quincenal":
                ingreso_mensual_estimado = total_ingresos * 2

        return render_template(
            "dashboard/index.html",
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
        flash(f"Error al cargar dashboard: {str(e)}", "error")
        return redirect(url_for("auth.login"))

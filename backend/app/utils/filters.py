from datetime import datetime, timedelta

def aplicar_filtro_fechas(registros, filtro, hoy=None):
    if hoy is None:
        hoy = datetime.today().date()
    
    if filtro == "todos":
        return registros

    filtrados = []

    for registro in registros:
        fecha_texto = registro.get("fecha")
        if not fecha_texto:
            continue

        try:
            fecha_registro = datetime.strptime(fecha_texto, "%Y-%m-%d").date()
        except ValueError:
            continue

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
            
            # Nota: El código original tenía un pequeño bug lógico con el fin de la quincena 
            # pero mantendré la compatibilidad si es necesario, 
            # aunque aquí lo expreso de forma más clara.
            if inicio_quincena <= fecha_registro <= hoy: # Usando hoy como tope si es mes actual
                filtrados.append(registro)

        elif filtro == "mes":
            if fecha_registro.year == hoy.year and fecha_registro.month == hoy.month:
                filtrados.append(registro)

    return filtrados

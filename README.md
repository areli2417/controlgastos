# Control de Gastos - Refactorizado

Este proyecto ha sido refactorizado para separar correctamente las responsabilidades de Backend y Frontend, siguiendo una arquitectura modular y moderna.

## Estructura del Proyecto

### Backend (Python/Flask)
Ubicado en la carpeta `backend/`.
- `app/`: Contiene la lógica modular de la aplicación.
  - `routes/`: Definición de Blueprints para Autenticación, Dashboard y Transacciones.
  - `services/`: Servicio de Supabase para centralizar las peticiones a la base de datos.
  - `utils/`: Funciones de filtrado y ayuda.
- `config.py`: Manejo de variables de entorno con `python-dotenv`.
- `run.py`: Punto de entrada para ejecutar la aplicación.

### Frontend
Ubicado en la carpeta `frontend/`.
- `templates/`: Plantillas Jinja2 organizadas por módulos.
  - `base.html`: Layout principal con **Tailwind CSS**, **Lucide Icons** y **Chart.js**.
  - `auth/`: Vistas de inicio de sesión y registro.
  - `dashboard/`: Vista principal del tablero financiero.
  - `transactions/`: Vistas para editar ingresos, gastos y ahorros.
- `static/`: Archivos estáticos.

## Tecnologías Utilizadas
- **Backend**: Flask, Supabase Python Client.
- **Frontend**: Tailwind CSS (CDN), Chart.js, Lucide Icons.
- **Base de Datos**: Supabase (PostgreSQL).

## Cómo Ejecutar
1. Instalar dependencias: `pip install -r requirements.txt`
2. Configurar el archivo `.env` con tus credenciales de Supabase.
3. Ejecutar: `python backend/run.py`

## Mejoras Realizadas
- **Arquitectura**: Migración de un archivo monolítico (`app.py`) a una estructura de Blueprints y Servicios.
- **Interfaz**: Rediseño total con Tailwind CSS, ofreciendo un aspecto moderno, limpio y responsive.
- **Visualización**: Gráficas mejoradas con Chart.js, incluyendo animaciones y una mejor distribución de datos.
- **Mantenibilidad**: Código más limpio y fácil de escalar.

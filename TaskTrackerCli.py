from argparse import ArgumentParser
from datetime import datetime
from tabulate import tabulate
import json
import os
import sys
import locale

# Establecer la configuración regional a español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def main():
    # Obtener las consultas disponibles
    consultas = ObtenerConsultas()

    # Obtener la consulta y los argumentos proporcionados por el usuario
    consulta, args = ObtenerConsulta(consultas)

    # Definir la ruta del archivo base.json en el directorio del usuario
    RUTABASE = os.path.expanduser("~/base.json")

    # Cargar la base de datos desde el archivo
    base = CargarBase(RUTABASE)

    try:
        # Ejecutar la consulta con los argumentos proporcionados
        consulta(base, **args)
    except KeyError:
        # Salir si no se encuentra una tarea con el ID proporcionado
        sys.exit("No se han encontrado tareas con el ID proporcionado")

    # Guardar la base de datos actualizada en el archivo
    GuardarBase(base, RUTABASE)

def CargarBase(path):
    try:
        # Intentar cargar la base de datos desde el archivo
        with open(path) as f:
            base = json.load(f)
    except:
        # Si falla, inicializar una base de datos vacía
        base = {}
    return base

def GuardarBase(base, path):
    # Guardar la base de datos en el archivo
    with open(path, "w") as f:
        json.dump(base, f)

def ObtenerConsultas():
    # Definir las consultas disponibles y sus argumentos
    return {
        "add": {
            "target": AgregarTarea,
            "help": "Agregar una tarea a tu lista de tareas",
            "args": [
                {"name_or_flags": ["descripcion"], "help": "Descripción de la tarea"}
            ],
        },
        "delete": {
            "target": EliminarTarea,
            "help": "Eliminar una tarea de tu lista de tareas",
            "args": [
                {
                    "name_or_flags": ["id"],
                    "help": "ID de la tarea que deseas eliminar",
                }
            ],
        },
        "update": {
            "target": ActualizarTarea,
            "help": "Actualizar la descripción de una tarea",
            "args": [
                {
                    "name_or_flags": ["id"],
                    "help": "ID de la tarea que deseas actualizar",
                },
                {
                    "name_or_flags": ["descripcion"],
                    "help": "Nueva descripción de la tarea",
                },
            ],
        },
        "list": {
            "target": ListarTareas,
            "help": "Listar todas las tareas",
            "args": [
                {
                    "name_or_flags": ["--estatus", "-e"],
                    "help": "Filtrar tareas por estado (todas, terminadas, por hacer, en progreso)",
                    "choices": ["todas", "terminadas", "por hacer", "en progreso"],
                    "type": str.lower,
                    "default": "todas",
                }
            ],
        },
        "mark-in-progress": {
            "target": MarcarEnProgeso,
            "help": "Marcar una tarea como 'en progreso'",
            "args": [{"name_or_flags": ["id"], "help": "ID de la tarea"}],
        },
        "mark-done": {
            "target": MarcarTerminada,
            "help": "Marcar una tarea como 'terminada'",
            "args": [{"name_or_flags": ["id"], "help": "ID de la tarea"}],
        },
    }

def ObtenerConsulta(consultas):
    # Crear un parser de argumentos
    parser = ArgumentParser(
        description="Una app en línea de comandos para manejar tareas."
    )
    # Crear subparsers para cada comando
    sub_parsers = parser.add_subparsers(title="commands", dest="command", required=True)

    # Añadir cada consulta como un subcomando
    for name, properties in consultas.items():
        p = sub_parsers.add_parser(name, help=properties["help"])
        for arg in properties["args"]:
            p.add_argument(*arg.pop("name_or_flags"), **arg)

    # Parsear los argumentos proporcionados por el usuario
    args = parser.parse_args().__dict__
    consulta = consultas[args.pop("command")]["target"]

    return consulta, args

def AgregarTarea(base, descripcion):
    # Obtener la fecha y hora actual
    today = datetime.today().isoformat()
    # Generar un nuevo ID para la tarea
    id = str(int(max("0", *base.keys())) + 1)
    # Añadir la nueva tarea a la base de datos
    base[id] = {
        "descripcion": descripcion,
        "estatus": "por hacer",
        "creada": today,
        "actualizada": today,
    }
    print("Tarea agregada:\n")
    # Listar la tarea recién agregada
    ListarTareas({id: base[id]})

def EliminarTarea(base, id):
    print("Tarea eliminada:\n")
    # Listar la tarea antes de eliminarla
    ListarTareas({id: base[id]})
    # Eliminar la tarea de la base de datos
    del base[id]

def ActualizarTarea(base, id, descripcion):
    # Actualizar la descripción y la fecha de actualización de la tarea
    base[id]["descripcion"] = descripcion
    base[id]["actualizada"] = datetime.today().isoformat()
    print("Tarea actualizada:\n")
    # Listar la tarea actualizada
    ListarTareas({id: base[id]})

def ListarTareas(base, estatus = 'todas'):
    # Formato de fecha y hora
    DATETIME_FORMAT = "%H:%M, %a, %d de %b de %Y"
    if (estatus == "terminadas"):
        estatus = "terminada"
    # Crear una tabla con las tareas filtradas por estado
    table = (
        {
            "Id": id,
            "Descripción": properties["descripcion"],
            "Estatus": properties["estatus"],
            "Fecha de creación": datetime.fromisoformat(properties["creada"]).strftime(
                DATETIME_FORMAT
            ),
            "Fecha de actualización": datetime.fromisoformat(properties["actualizada"]).strftime(
                DATETIME_FORMAT
            ),
        }
        for id, properties in sorted(base.items(), key=lambda t: t[0])
        if estatus == "todas" or estatus == properties["estatus"]
    )
    # Formatear la tabla
    table = tabulate(table, tablefmt="mixed_grid", headers="keys")
    if (estatus == "todas"):
        print(table or "No hay tareas aún.")
    else:   
        print(table or f"No hay tareas aún con el estatus: {estatus}.")

def MarcarEnProgeso(base, id):
    # Marcar la tarea como "en progreso" y actualizar la fecha de actualización
    base[id]["estatus"] = "en progreso"
    base[id]["actualizada"] = datetime.today().isoformat()
    print("Tarea en progreso:\n")
    # Listar la tarea actualizada
    ListarTareas({id: base[id]})

def MarcarTerminada(base, id):
    # Marcar la tarea como "terminada" y actualizar la fecha de actualización
    base[id]["estatus"] = "terminada"
    base[id]["actualizada"] = datetime.today().isoformat()
    print("Tarea terminada:\n")
    # Listar la tarea actualizada
    ListarTareas({id: base[id]})

if __name__ == "__main__":
    main()
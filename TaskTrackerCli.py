from argparse import ArgumentParser
from datetime import datetime
from tabulate import tabulate
import json
import os
import sys


def main():
    consultas = ObtenerConsultas()

    consulta, args = ObtenerConsulta(consultas)

    RUTABASE = os.path.expanduser("~/base.json")

    base = CargarBase(RUTABASE)

    try:
        consulta(base, **args)
    except KeyError:
        sys.exit("No se han encontrado tareas con el ID proporcionado")

    GuardarBase(base, RUTABASE)


def CargarBase(path):
    try:
        with open(path) as f:
            base = json.load(f)
    except:
        base = {}
    return base


def GuardarBase(base, path):
    with open(path, "w") as f:
        json.dump(base, f)


def ObtenerConsultas():
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
                    "help": "Filtrar tareas por estado (todas, terminada, por hacer, en progreso)",
                    "choices": ["todas", "terminada", "por hacer", "en progreso"],
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
    parser = ArgumentParser(
        description="Una app en línea de comandos para manejar tareas."
    )
    sub_parsers = parser.add_subparsers(title="commands", dest="command", required=True)

    for name, properties in consultas.items():
        p = sub_parsers.add_parser(name, help=properties["help"])
        for arg in properties["args"]:
            p.add_argument(*arg.pop("name_or_flags"), **arg)

    args = parser.parse_args().__dict__
    consulta = consultas[args.pop("command")]["target"]

    return consulta, args


def AgregarTarea(base, descripcion):
    today = datetime.today().isoformat()
    id = str(int(max("0", *base.keys())) + 1)
    base[id] = {
        "descripcion": descripcion,
        "estatus": "por hacer",
        "creada": today,
        "actualizada": today,
    }
    ListarTareas({id: base[id]})


def EliminarTarea(base, id):
    print("Tarea eliminada:")
    ListarTareas({id: base[id]})
    del base[id]


def ActualizarTarea(base, id, descripcion):
    base[id]["descripcion"] = descripcion
    base[id]["actualizada"] = datetime.today().isoformat()
    ListarTareas({id: base[id]})


def ListarTareas(base, estatus = 'todas'):
    DATETIME_FORMAT = "%d/%m/%Y %H:%M:%S"

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

    print(
        tabulate(table, tablefmt="mixed_grid", headers="keys") or "No hay tareas aún."
    )


def MarcarEnProgeso(base, id):
    base[id]["estatus"] = "en progreso"
    base[id]["actualizada"] = datetime.today().isoformat()
    ListarTareas({id: base[id]})


def MarcarTerminada(base, id):
    base[id]["estatus"] = "terminada"
    base[id]["actualizada"] = datetime.today().isoformat()
    ListarTareas({id: base[id]})


if __name__ == "__main__":
    main()
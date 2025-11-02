# Actividad 14

## Fase 1

### Singleton

* `SingletonMeta` verifica si la clase ya tiene una clase creada en el diccionario `_instances`. Si no existe, la crea. Caso contrario, devuelve la ya existente. Es decir, posterior a la primera llamada al constructor, se devuelve el mismo objeto.
* El atributo `_lock` asegura que esta opción sea segura en entornos con múltiples hilos. Es decir, si dos hilos llaman al constructor `_lock` asegura que solo se ejecute uno de ellos.

### Factory

* La clase `NullResourceFactory` centraliza y estandariza la creación de recursos Terraform del tipo `null_resource`. En lugar de escribir manualmente los bloques JSON cada vez, la fábrica ofrece un método create() que construye la estructura correcta de forma automática. Esto encapsula la lógica de creación, haciendo que el código sea más limpio, reutilizable y fácil de mantener, además de permitir generar recursos consistentes.
* Los triggers dentro del `null_resource` son claves especiales que Terraform usa para determinar cuándo debe recrear ese recurso. En esta fábrica, si no se proporcionan triggers personalizados, se añaden dos por defecto: un UUID único (`factory_uuid`) y un timestamp con la hora actual en UTC. Estos valores garantizan idempotencia controlada: cada vez que cambian, Terraform detecta una diferencia y fuerza la recreación del recurso.

### Composite

* `CompositeModule` actúa como un contenedor que combina varios recursos Terraform independientes en una sola estructura coherente. Cada recurso individual —por ejemplo, los generados por una fábrica o definidos manualmente— se agrega al módulo mediante el método add(), almacenándose internamente como un diccionario.
* Cuando se llama a `export()`, la clase recorre todos los recursos agregados y fusiona sus bloques resource en una sola lista dentro de un diccionario común. El resultado es un JSON unificado y válido para Terraform, que puede escribirse directamente a un archivo .tf.json. De esta manera, el patrón Composite permite tratar múltiples recursos como si fueran un único módulo lógico, facilitando la organización, reutilización y despliegue de configuraciones complejas de forma estructurada y escalable.

### Builder
* Primero, el método `build_null_fleet()` usa la Factory (`NullResourceFactory`) para crear un recurso base del tipo `null_resource` con su estructura JSON estándar y triggers únicos. Ese bloque base se envuelve en un Prototype (`ResourcePrototype`), que permite clonar el recurso tantas veces como sea necesario sin volver a construirlo desde cero. En cada clon, una función mutator renombra el recurso (app → app_0, app_1, etc.), asegurando que cada uno tenga un identificador único dentro del conjunto.
* Cada clon generado se agrega al Composite (`CompositeModule`), que actúa como un contenedor que acumula todos los recursos creados. Finalmente, el método `export()` toma este conjunto combinado y lo serializa a un único archivo main.tf.json listo para usar con Terraform.

## Fase 2

### Ejercicio 2.1

```python
    def reset(self) -> None:
        self.settings.clear()
```

- En este caso, solo es necesario limpiar el diccionario en el mismo objeto. La instancia conserva sus metadatos originales.

### Ejercicio 2.2

```python
from datetime import datetime
from typing import Dict, Any
from factory import NullResourceFactory

class TimestampedNullResourceFactory(NullResourceFactory):

    @staticmethod
    def create(name: str, fmt: str, triggers: Dict[str, Any] | None = None) -> Dict[str, Any]:
        ts = datetime.utcnow().strftime(fmt)
        triggers = triggers or {}
        triggers["timestamp_fmt"] = ts  # agrega el timestamp formateado
        return super(TimestampedNullResourceFactory, TimestampedNullResourceFactory).create(name, triggers)
```

- Esta variante acepta un formato para la creación de timestamps.

### Ejercicio 2.4

```python
    def export(self) -> Dict[str, Any]:
        merged: Dict[str, Any] = {
            "terraform": {},
            "provider": {},
            "locals": {},
            "variable": {},
            "data": {},
            "module": {},
            "resource": {},
            "output": {},
        }

        for child in self._children:
            if "terraform" in child:
                merged["terraform"] = {**merged["terraform"], **child["terraform"]}
            if "provider" in child:
                self._merge_simple_map(merged["provider"], child["provider"], "provider")
            if "locals" in child:
                for k, v in child["locals"].items():
                    if k in merged["locals"]:
                        raise ValueError(f"Local duplicado: {k}")
                    merged["locals"][k] = v
            if "variable" in child:
                self._merge_simple_map(merged["variable"], child["variable"], "variable")
            if "data" in child:
                for dtype, dnamed in child["data"].items():
                    merged["data"].setdefault(dtype, {})
                    for dname, dbody in dnamed.items():
                        if dname in merged["data"][dtype]:
                            raise ValueError(f"Data duplicada {dtype}.{dname}")
                        merged["data"][dtype][dname] = dbody
            if "module" in child:
                self._merge_simple_map(merged["module"], child["module"], "module")
            if "resource" in child:
                self._merge_resources(merged["resource"], child["resource"])
            if "output" in child:
                self._merge_simple_map(merged["output"], child["output"], "output")

        return {k: v for k, v in merged.items() if v not in ({}, [])}
```

### Ejercicio 2.5

```python
    def build_group(self, name: str, size: int):
        base = NullResourceFactory.create(name)
        proto = ResourcePrototype(base)
        group = CompositeModule()
        for i in range(size):
            def mut(block, i=i):  # captura i para evitar late binding
                res = block["resource"]["null_resource"].pop(name)
                block["resource"]["null_resource"][f"{name}_{i}"] = res
            group.add(proto.clone(mut))
        # Inserta el grupo como submódulo
        self.module.add({"module": {name: group.export()}})
        return self
```

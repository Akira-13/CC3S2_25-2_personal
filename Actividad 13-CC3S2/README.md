# Actividad 13

## Fase 1

### Resultado de actividad

```json
ak13a@fedora ~/D/2/D/s/L/e/app1> terraform plan

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # null_resource.app1 will be created
  + resource "null_resource" "app1" {
      + id       = (known after apply)
      + triggers = {
          + "name"    = "app1"
          + "network" = "net1"
        }
    }

Plan: 1 to add, 0 to change, 0 to destroy.
```

### Preguntas

* ¿Cómo interpreta Terraform el cambio de variable?
  * Terraform relee la configuración con `plan` y toma el nuevo `defualt` del módulo. Cualquier referencia a `network` se reevalúa, haciendo que `triggers` aparezca con cambios.
* ¿Qué diferencia hay entre modificar el JSON vs. parchear directamente el recurso?
  * Modificarel JSON implica modificar la fuente de verdad, ayudando con la reproducibilidad.
  * Modificar directamente el recurso crea config drift y será sobreescrito en la próxima generación.
* ¿Por qué Terraform no recrea todo el recurso, sino que aplica el cambio "in-place"?
  * Se usa un grafo de dependencia para llegar al estado deseado con cambios mínimos. En este caso, solo es necesario modificar `triggers`.
* ¿Qué pasa si editas directamente `main.tf.json` en lugar de la plantilla de variables?
  * Solo funciona hasta regenerar los ambientes con `generate_envs.py`. 

## Fase 2

### Remediación drift

#### Resultado de actividad

```json
ak13a@fedora ~/D/2/D/s/L/e/app2> terraform apply

Terraform used the selected providers to generate the following execution plan. Resource actions are indicated with the following symbols:
  + create

Terraform will perform the following actions:

  # null_resource.app2 will be created
  + resource "null_resource" "app2" {
      + id       = (known after apply)
      + triggers = {
          + "name"    = "app2"
          + "network" = "net2"
        }
    }

Plan: 1 to add, 0 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes

null_resource.app2: Creating...
null_resource.app2: Provisioning with 'local-exec'...
null_resource.app2 (local-exec): Executing: ["/bin/sh" "-c" "echo 'Arrancando servidor app2 en red net2'"]
null_resource.app2 (local-exec): Arrancando servidor app2 en red net2
null_resource.app2: Creation complete after 0s [id=7183041385972530000]

Apply complete! Resources: 1 added, 0 changed, 0 destroyed.
```

### Migrando a IaC

#### Script

```python
import json, re
from pathlib import Path

root = Path(__file__).resolve().parent
legacy = root / "legacy"
tfdir = root / "tfgen"
tfdir.mkdir(exist_ok=True)

cfg = (legacy / "config.cfg").read_text(encoding="utf-8")
m = re.search(r"^PORT\s*=\s*(.+)$", cfg, re.M)
port = (m.group(1).strip().strip('"').strip("'")) if m else "8080"

# tfgen/network.tf.json
network = {
    "terraform": {
        "required_providers": {"null": {"source": "hashicorp/null", "version": "3.2.2"}}
    },
    "provider": {"null": [{}]},
    "variable": {"port": {"type": "string", "default": port}},
}
(tfdir / "network.tf.json").write_text(json.dumps(network, indent=2), encoding="utf-8")

# tfgen/main.tf.json
cfg_rel = "${path.module}/../legacy/config.cfg"
run_rel = "${path.module}/../legacy/run.sh"
main = {
    "resource": {
        "null_resource": {
            "legacy": {
                "triggers": {
                    "port": "${var.port}",
                    "config_sha": f'${{sha1(file("{cfg_rel}"))}}',
                    "script_sha": f'${{sha1(file("{run_rel}"))}}',
                },
                "provisioner": [
                    {
                        "local-exec": {
                            "command": (
                                "bash -lc 'set -a; source "
                                + cfg_rel
                                + '; set +a; echo "Arrancando $PORT"\''
                            )
                        }
                    }
                ],
            }
        }
    }
}
(tfdir / "main.tf.json").write_text(json.dumps(main, indent=2), encoding="utf-8")

print("Generado tfgen/network.tf.json y tfgen/main.tf.json")
```

#### Resultado

```
null_resource.legacy: Creating...
null_resource.legacy: Provisioning with 'local-exec'...
null_resource.legacy (local-exec): Executing: ["/bin/sh" "-c" "bash -lc 'set -a; source ./../legacy/config.cfg; set +a; echo \"Arrancando $PORT\"'"]
null_resource.legacy (local-exec): Arrancando 8080
null_resource.legacy: Creation complete after 0s [id=8037177551834641824]

```

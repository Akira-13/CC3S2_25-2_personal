#!/usr/bin/env python3
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

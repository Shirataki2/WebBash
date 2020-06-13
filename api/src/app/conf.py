from docker import types
from typing import Mapping

docker_prepare_conf = {
    "command": "bash",
    "stdout": False,
    "stderr": False,
    "detach": True,
    "remove": True,
    "tty": True,
    "environment": {
        "LANG": "ja_JP.UTF-8"
    },
    "network_disabled": True,
    "network_mode": 'none',
    "pids_limit": 128,
    "mem_limit": '256m',
    "memswap_limit": '256m',
    "shm_size": '256m',
    "cpuset_cpus": '0,1',
    "cpu_period": 50000,
    "cpu_quota": 40000,
    "ulimits": [
        types.Ulimit(name='fsize', soft=5000000, hard=5000000)
    ]
}

fastapi_config: Mapping = {
    'title': 'WebBash API',
    'openapi_prefix': '/api',
    'openapi_url': "/openapi.json",
    'docs_url': '/dev',
    'redoc_url': '/docs'
}

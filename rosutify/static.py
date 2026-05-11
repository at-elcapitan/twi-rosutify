from .configuration import EnvVar

ENV_VARIABLES = [
    EnvVar(
        "TG_API_KEY",
        required=True
    ),
    EnvVar(
        "TW_USER",
        required=True
    ),
    EnvVar(
        "TW_PASS",
        required=True
    )
]
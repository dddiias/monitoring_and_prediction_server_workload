from .start import router as start_router
from .metrics import router as metrics_router
from .settings import router as settings_router
from .predict import router as predict_router
from .help import router as help_router
from .fsm.cpu_limit import router as fsm_cpu_limit_router
from .fsm.connect_fsm import router as connect_fsm_router
from .server_manage import router as server_manage_router

routers = [
    start_router,
    metrics_router,
    settings_router,
    predict_router,
    help_router,
    fsm_cpu_limit_router,
    connect_fsm_router,
    server_manage_router,
]

from fastapi import APIRouter
from app.api.v1 import user, task, category, tag

router_v1 = APIRouter(prefix="/api/v1")
router_v1.include_router(user.router)
router_v1.include_router(category.router)
router_v1.include_router(task.router)
router_v1.include_router(tag.router)

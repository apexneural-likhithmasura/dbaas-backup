"""
Health Check Routes
System health monitoring and status endpoints
"""

from fastapi import APIRouter, Depends
from app.api.controllers.health_controller import HealthController
from app.schemas.common_schema import HealthResponse, DetailedHealthResponse

router = APIRouter()


@router.get("/", response_model=HealthResponse)
async def health_check():
    """Basic health check endpoint"""
    controller = HealthController()
    return await controller.basic_health_check()


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check():
    """Detailed health check with system information"""
    controller = HealthController()
    return await controller.detailed_health_check()


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    controller = HealthController()
    return await controller.readiness_check()


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    controller = HealthController()
    return await controller.liveness_check()

"""
Capa de Aplicación
"""
from .DTOs import ScrapingResultDTO, AIAnalysisResultDTO, PipelineResultDTO
from .UseCases import ScrapingUseCase, AIAnalysisUseCase, PipelineUseCase
from .Services import ApplicationService

__all__ = [
    "ScrapingResultDTO",
    "AIAnalysisResultDTO", 
    "PipelineResultDTO",
    "ScrapingUseCase",
    "AIAnalysisUseCase",
    "PipelineUseCase",
    "ApplicationService"
]

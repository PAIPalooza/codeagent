"""Models package initialization module.

This module imports all model classes to make them available when the models
package is imported, ensuring they're registered with SQLAlchemy.
"""

from .base import BaseMixin
# Import all models to register them with SQLAlchemy
from .project import Project, ProjectStatus
from .generation_step import GenerationStep, StepStatus
from .log import Log, LogLevel

# List of all model classes for easy access
__all__ = [
    "BaseMixin",
    "Project",
    "ProjectStatus",
    "GenerationStep",
    "StepStatus",
    "Log",
    "LogLevel",
]

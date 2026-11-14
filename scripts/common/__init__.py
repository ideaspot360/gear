# -*- coding: utf-8 -*-
"""
H-GEAR STUDIO Blog - 공통 도안 제작 엔진 패키지
Smart Diagram Layout & Geometry Collision Avoidance Package
"""

from .smart_diagram_engine import (
    SpatialObstacleRegistry,
    SmartDiagramEngine,
    SmartCallout,
    SmartCalloutOptimizer,
    RadialCircleLabelDistributor,
    ArcClipper,
    line_box_collision,
    point_box_collision,
    box_box_collision,
)

__all__ = [
    "SpatialObstacleRegistry",
    "SmartDiagramEngine",
    "SmartCallout",
    "SmartCalloutOptimizer",
    "RadialCircleLabelDistributor",
    "ArcClipper",
    "line_box_collision",
    "point_box_collision",
    "box_box_collision",
]

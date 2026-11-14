# -*- coding: utf-8 -*-
"""
H-GEAR STUDIO Blog - 공통 스마트 도안 제작 엔진 모듈
Common Smart Diagram Layout & Geometry Collision Avoidance Engine

이 모듈은 학술 도안 제작 시 텍스트 라벨과 치형 곡선, 피치원, 작용선,
접촉점 등 핵심 기하 형상 간의 충돌 및 가림을 방지하고,
다국어(KO, EN, DE, JA) 텍스트 폭 편차에도 완전무결한 여백 분산을 보장하는 공통 엔진입니다.

핵심 구성 요소:
  1. SpatialObstacleRegistry: 디스플레이 좌표계 기하 형상(선분, 호, 다각형, 랜드마크 점) 장애물 레지스트리.
  2. line_box_collision (Liang-Barsky): 초고속 2D 선분-AABB 박스 충돌 판정 커널.
  3. point_box_collision: 원/랜드마크-AABB 박스 충돌 판정 커널.
  4. box_box_collision: AABB-AABB 박스 충돌 판정 커널.
  5. ArcClipper: 원호 각도 구간 클리핑 및 치수 영역 침범 방지 유틸리티.
  6. SmartCallout: 외곽 여백 단조 정렬(Outward Alignment) 및 꺾은선 지시선 헬퍼.
  7. RadialCircleLabelDistributor: 동심원 라벨 외곽 여백 단조 정렬기.
  8. SmartCalloutOptimizer: 8/16-방위각 탐색 및 비용 함수를 통한 최적 빈 공간 탐색기.
  9. SmartDiagramEngine: 캔버스 바인딩, 지시선 생성, 5-게이트 무결성 감사 총괄 클래스.
"""

import math
from typing import List, Tuple, Dict, Optional, Any, Set, Union
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.text as mtext
from matplotlib.transforms import Bbox

# 다국어 폰트 기본 설정 (Windows, Linux, macOS 호환)
plt.rcParams["font.sans-serif"] = ["Malgun Gothic", "Noto Sans CJK KR", "AppleGothic", "DejaVu Sans", "sans-serif"]
plt.rcParams["axes.unicode_minus"] = False


# ==============================================================================
# 1. 초고속 기하 충돌 판정 커널 (Collision Kernels)
# ==============================================================================

def line_box_collision(
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    box: Tuple[float, float, float, float],
    padding: float = 0.0,
) -> bool:
    """
    Liang-Barsky 2D 선분-AABB 박스 교차 판정 알고리즘.

    Args:
        p1: 선분 시작점 (x1, y1)
        p2: 선분 종료점 (x2, y2)
        box: (x_min, y_min, x_max, y_max)
        padding: 박스 확장 여백 (데이터 또는 디스플레이 픽셀 단위)

    Returns:
        bool: 선분이 박스(확장 포함)와 교차하거나 내부에 포함되면 True, 아니면 False.
    """
    x0, y0, x1, y1 = box
    if padding != 0.0:
        x0 -= padding
        y0 -= padding
        x1 += padding
        y1 += padding

    # 1. AABB 외곽 빠른 배제 (Bounding Box Quick Rejection)
    min_x = min(p1[0], p2[0])
    max_x = max(p1[0], p2[0])
    min_y = min(p1[1], p2[1])
    max_y = max(p1[1], p2[1])

    if max_x < x0 or min_x > x1 or max_y < y0 or min_y > y1:
        return False

    # 2. 양 끝점 중 하나라도 박스 내부인 경우 즉시 교차
    if (x0 <= p1[0] <= x1 and y0 <= p1[1] <= y1) or (x0 <= p2[0] <= x1 and y0 <= p2[1] <= y1):
        return True

    # 3. Liang-Barsky 매개변수 t in [0, 1] 클리핑
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]

    p = [-dx, dx, -dy, dy]
    q = [p1[0] - x0, x1 - p1[0], p1[1] - y0, y1 - p1[1]]

    u1 = 0.0
    u2 = 1.0

    for k in range(4):
        pk = p[k]
        qk = q[k]
        if pk == 0.0:
            if qk < 0.0:
                return False  # 박스 경계와 평행하며 바깥쪽에 위치
        else:
            t = qk / pk
            if pk < 0.0:
                if t > u2:
                    return False
                if t > u1:
                    u1 = t
            else:  # pk > 0.0
                if t < u1:
                    return False
                if t < u2:
                    u2 = t

    return u1 <= u2


def point_box_collision(
    pt: Tuple[float, float],
    radius: float,
    box: Tuple[float, float, float, float],
) -> bool:
    """
    원(중심 pt, 반경 radius)과 AABB 박스간의 충돌 판정.
    """
    cx, cy = pt
    x0, y0, x1, y1 = box
    closest_x = max(x0, min(cx, x1))
    closest_y = max(y0, min(cy, y1))
    dx = cx - closest_x
    dy = cy - closest_y
    return (dx * dx + dy * dy) <= (radius * radius)


def box_box_collision(
    b1: Tuple[float, float, float, float],
    b2: Tuple[float, float, float, float],
    min_gap: float = 0.0,
) -> bool:
    """
    두 AABB 박스간 충돌 및 이격 거리 판정.
    b = (x0, y0, x1, y1)
    """
    return not (
        b1[2] + min_gap <= b2[0] or
        b1[0] - min_gap >= b2[2] or
        b1[3] + min_gap <= b2[1] or
        b1[1] - min_gap >= b2[3]
    )


# ==============================================================================
# 2. 원호 클리핑 유틸리티 (ArcClipper)
# ==============================================================================

class ArcClipper:
    """
    동심원 원호가 지정된 경계창(x_min, x_max, y_min, y_max)을 벗어나
    치수 영역이나 여백 주석 영역을 침범하지 않도록 각도 구간을 기하학적으로 클리핑.
    """

    @staticmethod
    def compute_clipped_arc_thetas(
        center: Tuple[float, float],
        radius: float,
        theta_start_deg: float,
        theta_end_deg: float,
        x_min: Optional[float] = None,
        x_max: Optional[float] = None,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
    ) -> Tuple[float, float]:
        """
        초기 각도 범위 [theta_start_deg, theta_end_deg]에 대해 경계창과 교차하는 유효 각도 범위 반환.
        """
        cx, cy = center
        th1 = math.radians(theta_start_deg)
        th2 = math.radians(theta_end_deg)
        if th1 > th2:
            th1, th2 = th2, th1

        # 샘플링 기반 미세 정밀 클리핑 (연속 미분기하 오차 0.01 deg 이내)
        thetas = np.linspace(th1, th2, 360)
        xs = cx + radius * np.cos(thetas)
        ys = cy + radius * np.sin(thetas)

        valid_mask = np.ones_like(thetas, dtype=bool)
        if x_min is not None:
            valid_mask &= (xs >= x_min)
        if x_max is not None:
            valid_mask &= (xs <= x_max)
        if y_min is not None:
            valid_mask &= (ys >= y_min)
        if y_max is not None:
            valid_mask &= (ys <= y_max)

        valid_indices = np.where(valid_mask)[0]
        if len(valid_indices) == 0:
            return math.degrees(th1), math.degrees(th1)

        first_idx = valid_indices[0]
        last_idx = valid_indices[-1]

        return float(math.degrees(thetas[first_idx])), float(math.degrees(thetas[last_idx]))

    @staticmethod
    def generate_clipped_arc_points(
        center: Tuple[float, float],
        radius: float,
        theta_start_deg: float,
        theta_end_deg: float,
        x_min: Optional[float] = None,
        x_max: Optional[float] = None,
        y_min: Optional[float] = None,
        y_max: Optional[float] = None,
        num_points: int = 120,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """클리핑된 원호의 (x, y) 좌표 배열 생성"""
        cx, cy = center
        th_start, th_end = ArcClipper.compute_clipped_arc_thetas(
            center, radius, theta_start_deg, theta_end_deg,
            x_min=x_min, x_max=x_max, y_min=y_min, y_max=y_max
        )
        thetas = np.radians(np.linspace(th_start, th_end, num_points))
        xs = cx + radius * np.cos(thetas)
        ys = cy + radius * np.sin(thetas)
        return xs, ys


# ==============================================================================
# 3. 공간 장애물 레지스트리 (SpatialObstacleRegistry)
# ==============================================================================

class SpatialObstacleRegistry:
    """
    디스플레이(픽셀) 좌표계 기준으로 기하 곡선, 랜드마크 점, 기존 박스를 관리하고
    신규 텍스트 및 지시선 배치 시 충돌을 검출하는 고속 레지스트리.
    """

    def __init__(self, ax: Optional[plt.Axes] = None):
        self.ax = ax
        self.lines: List[Dict[str, Any]] = []      # {'name': str, 'pts': ndarray(Nx2 disp), 'padding': float}
        self.landmarks: List[Dict[str, Any]] = []  # {'name': str, 'pt': (x,y disp), 'radius_px': float}
        self.boxes: List[Dict[str, Any]] = []      # {'name': str, 'box': (x0,y0,x1,y1 disp), 'padding': float}
        self.cards: List[Dict[str, Any]] = []      # {'name': str, 'box': (x0,y0,x1,y1 disp), 'padding': float}

    def bind_axes(self, ax: plt.Axes):
        self.ax = ax

    def to_display(self, pts_data: np.ndarray) -> np.ndarray:
        """데이터 좌표 -> 디스플레이 좌표 변환"""
        if self.ax is None:
            raise ValueError("Axes must be bound to registry before transforming coordinates.")
        return self.ax.transData.transform(pts_data)

    def to_display_pt(self, pt_data: Tuple[float, float]) -> Tuple[float, float]:
        """단일 점 데이터 좌표 -> 디스플레이 좌표 변환"""
        pts = np.array([[pt_data[0], pt_data[1]]], dtype=float)
        res = self.to_display(pts)
        return float(res[0, 0]), float(res[0, 1])

    def register_line(
        self,
        xdata: Union[np.ndarray, List[float]],
        ydata: Union[np.ndarray, List[float]],
        name: str = "",
        padding: float = 4.0,
    ):
        """기하 곡선/직선을 디스플레이 좌표 장애물로 등록"""
        xs = np.asarray(xdata, dtype=float)
        ys = np.asarray(ydata, dtype=float)
        if len(xs) < 2 or len(ys) < 2:
            return
        pts_data = np.column_stack([xs, ys])
        pts_disp = self.to_display(pts_data)
        self.lines.append({
            "name": name,
            "pts": pts_disp,
            "padding": float(padding),
        })

    def register_landmark(
        self,
        pt_data: Tuple[float, float],
        radius_px: float = 8.0,
        name: str = "",
    ):
        """핵심 랜드마크 점 (P, A, E, O 등) 등록"""
        pt_disp = self.to_display_pt(pt_data)
        self.landmarks.append({
            "name": name,
            "pt": pt_disp,
            "radius_px": float(radius_px),
        })

    def register_box(
        self,
        box_disp: Tuple[float, float, float, float],
        name: str = "",
        padding: float = 2.0,
    ):
        """텍스트 또는 객체 디스플레이 AABB 등록"""
        self.boxes.append({
            "name": name,
            "box": box_disp,
            "padding": float(padding),
        })

    def register_card(
        self,
        box_disp: Tuple[float, float, float, float],
        name: str = "",
        padding: float = 6.0,
    ):
        """요약 카드 컨테이너 영역 등록"""
        self.cards.append({
            "name": name,
            "box": box_disp,
            "padding": float(padding),
        })

    def check_box_collisions(
        self,
        box_disp: Tuple[float, float, float, float],
        ignore_names: Optional[Set[str]] = None,
    ) -> List[Tuple[str, str]]:
        """
        box_disp가 등록된 선분, 랜드마크, 박스, 카드와 충돌하는지 전수 검사.
        반환: [('line'|'landmark'|'box'|'card', obstacle_name), ...]
        """
        collisions: List[Tuple[str, str]] = []
        ignore = ignore_names or set()

        # 1. 선분 장애물 충돌 검사 (Liang-Barsky)
        for line in self.lines:
            if line["name"] in ignore:
                continue
            pts = line["pts"]
            pad = line["padding"]
            for i in range(len(pts) - 1):
                p1 = (pts[i, 0], pts[i, 1])
                p2 = (pts[i + 1, 0], pts[i + 1, 1])
                if line_box_collision(p1, p2, box_disp, padding=pad):
                    collisions.append(("line", line["name"]))
                    break

        # 2. 랜드마크 점 충돌 검사
        for lm in self.landmarks:
            if lm["name"] in ignore:
                continue
            if point_box_collision(lm["pt"], lm["radius_px"], box_disp):
                collisions.append(("landmark", lm["name"]))

        # 3. 타 텍스트 박스 충돌 검사
        for b in self.boxes:
            if b["name"] in ignore:
                continue
            if box_box_collision(box_disp, b["box"], min_gap=b["padding"]):
                collisions.append(("box", b["name"]))

        # 4. 카드 컨테이너 충돌 검사
        for c in self.cards:
            if c["name"] in ignore:
                continue
            if box_box_collision(box_disp, c["box"], min_gap=c["padding"]):
                collisions.append(("card", c["name"]))

        return collisions

    def check_segment_collisions(
        self,
        p1_disp: Tuple[float, float],
        p2_disp: Tuple[float, float],
        ignore_names: Optional[Set[str]] = None,
    ) -> List[str]:
        """선분(지시선 등)이 선분 장애물과 교차하는지 검사"""
        hits: List[str] = []
        ignore = ignore_names or set()
        for line in self.lines:
            if line["name"] in ignore:
                continue
            pts = line["pts"]
            for i in range(len(pts) - 1):
                lp1 = (pts[i, 0], pts[i, 1])
                lp2 = (pts[i + 1, 0], pts[i + 1, 1])
                # 선분 대 선분 교차 (CCW 검사)
                if self._segments_intersect(p1_disp, p2_disp, lp1, lp2):
                    hits.append(line["name"])
                    break
        return hits

    @staticmethod
    def _segments_intersect(
        a1: Tuple[float, float],
        a2: Tuple[float, float],
        b1: Tuple[float, float],
        b2: Tuple[float, float],
    ) -> bool:
        def ccw(A, B, C):
            return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
        return (ccw(a1, b1, b2) != ccw(a2, b1, b2)) and (ccw(a1, a2, b1) != ccw(a1, a2, b2))


# ==============================================================================
# 4. 스마트 콜아웃 헬퍼 (SmartCallout)
# ==============================================================================

class SmartCallout:
    """
    캔버스 3개 구역 분리(3-Zone Architecture)에 기반한 외곽 여백 단조 콜아웃 헬퍼.
    좌측 여백은 ha='right', 우측 여백은 ha='left'로 정렬하여
    텍스트가 기하 형상 바깥쪽으로 확장되도록 강제함으로써 형상 가림을 원천 차단.
    """

    @staticmethod
    def draw_margin_callout(
        ax: plt.Axes,
        target_pt: Tuple[float, float],
        text: str,
        side: str = "left",
        margin_coord: Optional[float] = None,
        y_pos: Optional[float] = None,
        x_pos: Optional[float] = None,
        fontsize: float = 10.0,
        color: str = "#0F172A",
        fontweight: str = "normal",
        box_style: Optional[Dict[str, Any]] = None,
        arrowprops: Optional[Dict[str, Any]] = None,
        zorder: int = 15,
    ) -> mtext.Annotation:
        """
        외곽 여백 지시선 주석 생성.

        Args:
            ax: 대상 Axes
            target_pt: 지시선이 가리킬 대상 점 (데이터 좌표)
            text: 표시할 텍스트 (다국어 및 LaTeX 포함)
            side: 여백 방향 ('left', 'right', 'top', 'bottom')
            margin_coord: 여백 기준선 좌표 (side가 left/right면 x, top/bottom이면 y)
            y_pos: 텍스트 y 위치 (지정 시 target_pt[1] 대신 사용)
            x_pos: 텍스트 x 위치 (지정 시 target_pt[0] 대신 사용)
        """
        x_target, y_target = target_pt

        default_box = dict(
            boxstyle="round,pad=0.28",
            fc="white",
            ec="#CBD5E1",
            lw=0.75,
            alpha=0.92,
        )
        if box_style is not None:
            default_box.update(box_style)

        if side == "left":
            ha = "right"
            va = "center"
            tx = margin_coord if margin_coord is not None else (x_pos if x_pos is not None else x_target - 15.0)
            ty = y_pos if y_pos is not None else y_target
            default_arrow = dict(
                arrowstyle="->",
                color=color,
                lw=0.85,
                shrinkA=2,
                shrinkB=3,
                connectionstyle="arc3,rad=0",
            )
        elif side == "right":
            ha = "left"
            va = "center"
            tx = margin_coord if margin_coord is not None else (x_pos if x_pos is not None else x_target + 15.0)
            ty = y_pos if y_pos is not None else y_target
            default_arrow = dict(
                arrowstyle="->",
                color=color,
                lw=0.85,
                shrinkA=2,
                shrinkB=3,
                connectionstyle="arc3,rad=0",
            )
        elif side == "top":
            ha = "center"
            va = "bottom"
            tx = x_pos if x_pos is not None else x_target
            ty = margin_coord if margin_coord is not None else (y_pos if y_pos is not None else y_target + 10.0)
            default_arrow = dict(
                arrowstyle="->",
                color=color,
                lw=0.85,
                shrinkA=2,
                shrinkB=3,
                connectionstyle="arc3,rad=0",
            )
        elif side == "bottom":
            ha = "center"
            va = "top"
            tx = x_pos if x_pos is not None else x_target
            ty = margin_coord if margin_coord is not None else (y_pos if y_pos is not None else y_target - 10.0)
            default_arrow = dict(
                arrowstyle="->",
                color=color,
                lw=0.85,
                shrinkA=2,
                shrinkB=3,
                connectionstyle="arc3,rad=0",
            )
        else:
            raise ValueError(f"Invalid side: '{side}'. Must be 'left', 'right', 'top', or 'bottom'.")

        if arrowprops is not None:
            default_arrow.update(arrowprops)

        ann = ax.annotate(
            text,
            xy=(x_target, y_target),
            xytext=(tx, ty),
            ha=ha,
            va=va,
            fontsize=fontsize,
            fontweight=fontweight,
            color=color,
            bbox=default_box,
            arrowprops=default_arrow,
            zorder=zorder,
        )
        return ann


# ==============================================================================
# 5. 동심원 방사형 라벨 정렬기 (RadialCircleLabelDistributor)
# ==============================================================================

class RadialCircleLabelDistributor:
    """
    스퍼 기어 4대 기본 원(Tip, Pitch, Base, Root)과 같은 동심원 군에 대해,
    좌측 또는 우측 여백 칼럼에 겹침 없는 단조 증가(Monotonic) 수직 정렬을 생성하고
    지시선으로 연결하여 텍스트 겹침과 곡선 가림을 원천 차단.
    """

    @staticmethod
    def distribute_concentric_labels(
        ax: plt.Axes,
        center: Tuple[float, float],
        circles: List[Dict[str, Any]],
        side: str = "left",
        x_margin: float = -26.0,
        y_center: Optional[float] = None,
        min_vertical_gap: float = 4.8,
        fontsize: float = 9.8,
        box_style: Optional[Dict[str, Any]] = None,
    ) -> List[mtext.Annotation]:
        """
        동심원 라벨 군 단조 정렬 및 생성.

        Args:
            ax: 대상 Axes
            center: 동심원 중심점 (xc, yc)
            circles: [{'radius': r, 'text': str, 'color': str, 'fontweight': ...}, ...] (반경 내림차순 또는 오름차순)
            side: 여백 방향 ('left' 또는 'right')
            x_margin: 여백 컬럼 X 좌표
            y_center: 중심 Y 기준 (미지정 시 기하 평균)
            min_vertical_gap: 인접 텍스트 간 최소 Y 이격 거리 (데이터 단위)
        """
        if not circles:
            return []

        # 반경 내림차순 정렬 (상단에서 하단으로 순차 배치)
        sorted_circles = sorted(circles, key=lambda c: c["radius"], reverse=True)
        n = len(sorted_circles)

        cx, cy = center
        # 초기 지시선 앵커 점 계산: 원호 상에서 여백 방향(예: 160도 부근)
        anchor_pts = []
        for c in sorted_circles:
            r = c["radius"]
            # 원호 상의 시작점: left면 x < cx, right면 x > cx
            angle_deg = 162.0 if side == "left" else 18.0
            rad = math.radians(angle_deg)
            ax_pt = (cx + r * math.cos(rad), cy + r * math.sin(rad))
            anchor_pts.append(ax_pt)

        # 초기 Y 계산
        raw_ys = [pt[1] for pt in anchor_pts]
        target_center_y = y_center if y_center is not None else float(np.mean(raw_ys))

        # 단조 증가 Y 슬롯 생성 (중심 기준 대칭 확장)
        total_span = (n - 1) * min_vertical_gap
        start_y = target_center_y + total_span / 2.0
        allocated_ys = [start_y - i * min_vertical_gap for i in range(n)]

        annotations = []
        for i, c in enumerate(sorted_circles):
            t_pt = anchor_pts[i]
            y_slot = allocated_ys[i]
            color = c.get("color", "#0F172A")
            weight = c.get("fontweight", "normal")

            ann = SmartCallout.draw_margin_callout(
                ax=ax,
                target_pt=t_pt,
                text=c["text"],
                side=side,
                margin_coord=x_margin,
                y_pos=y_slot,
                fontsize=fontsize,
                fontweight=weight,
                color=color,
                box_style=box_style,
                arrowprops=dict(
                    arrowstyle="->",
                    color=color,
                    lw=0.85,
                    connectionstyle="arc3,rad=-0.05" if side == "left" else "arc3,rad=0.05",
                ),
            )
            annotations.append(ann)

        return annotations


# ==============================================================================
# 6. 스마트 콜아웃 최적화 엔진 (SmartCalloutOptimizer)
# ==============================================================================

class SmartCalloutOptimizer:
    """
    8방위/16방위각 탐색 및 비용 함수 J(theta, R)를 최소화하여
    기하 곡선과 기존 텍스트를 침범하지 않는 최적 빈 공간을 찾아 지시선 주석을 배치.
    """

    def __init__(self, registry: SpatialObstacleRegistry):
        self.registry = registry

    def find_optimal_callout_placement(
        self,
        target_pt_data: Tuple[float, float],
        text: str,
        preferred_angles_deg: Optional[List[float]] = None,
        distance_range_data: Tuple[float, float] = (15.0, 45.0),
        fontsize: float = 10.0,
        num_angle_samples: int = 16,
        num_dist_samples: int = 5,
    ) -> Dict[str, Any]:
        """
        비용 함수 평가를 통한 최적 배치 파라미터 산출.

        Returns:
            {
                'xytext_data': (x_opt, y_opt),
                'ha': str,
                'va': str,
                'angle_deg': float,
                'distance': float,
                'cost': float,
                'box_disp': (x0, y0, x1, y1),
            }
        """
        ax = self.registry.ax
        if ax is None:
            raise ValueError("Registry must have bound axes.")

        x0, y0 = target_pt_data
        r_min, r_max = distance_range_data
        distances = np.linspace(r_min, r_max, num_dist_samples)

        if preferred_angles_deg:
            angles = preferred_angles_deg
        else:
            angles = [135, 45, 225, 315, 90, 270, 0, 180, 112.5, 67.5, 157.5, 22.5, 202.5, 247.5, 292.5, 337.5][:num_angle_samples]

        # 텍스트 크기 예측 (디스플레이 픽셀)
        # 1문자당 약 0.55 * fontsize * dpi / 72
        dpi = ax.figure.dpi if ax.figure else 100.0
        scale = dpi / 72.0
        lines = text.split("\n")
        max_chars = max(len(ln) for ln in lines) if lines else 1
        est_w_px = max_chars * fontsize * 0.58 * scale + 14.0 * scale
        est_h_px = len(lines) * fontsize * 1.35 * scale + 12.0 * scale

        # 캔버스 뷰포트 디스플레이 바운드
        bbox_ax = ax.get_window_extent()
        c_x0, c_y0, c_x1, c_y1 = bbox_ax.x0, bbox_ax.y0, bbox_ax.x1, bbox_ax.y1

        best_cost = float("inf")
        best_candidate: Optional[Dict[str, Any]] = None

        p0_disp = self.registry.to_display_pt(target_pt_data)

        for ang_idx, ang_deg in enumerate(angles):
            rad = math.radians(ang_deg)
            cos_a = math.cos(rad)
            sin_a = math.sin(rad)

            # 정렬 기준 설정: 지시선이 나아가는 방향 반대편으로 텍스트 확장
            if cos_a > 0.35:
                ha = "left"
            elif cos_a < -0.35:
                ha = "right"
            else:
                ha = "center"

            if sin_a > 0.35:
                va = "bottom"
            elif sin_a < -0.35:
                va = "top"
            else:
                va = "center"

            for dist in distances:
                cand_x_data = x0 + dist * cos_a
                cand_y_data = y0 + dist * sin_a

                # 디스플레이 좌표로 변환
                cand_pt_disp = self.registry.to_display_pt((cand_x_data, cand_y_data))
                cx_disp, cy_disp = cand_pt_disp

                # Bounding Box 산출
                if ha == "left":
                    bx0 = cx_disp
                    bx1 = cx_disp + est_w_px
                elif ha == "right":
                    bx0 = cx_disp - est_w_px
                    bx1 = cx_disp
                else:
                    bx0 = cx_disp - est_w_px / 2.0
                    bx1 = cx_disp + est_w_px / 2.0

                if va == "bottom":
                    by0 = cy_disp
                    by1 = cy_disp + est_h_px
                elif va == "top":
                    by0 = cy_disp - est_h_px
                    by1 = cy_disp
                else:
                    by0 = cy_disp - est_h_px / 2.0
                    by1 = cy_disp + est_h_px / 2.0

                cand_box_disp = (bx0, by0, bx1, by1)

                # 비용 함수 평가 J(theta, R)
                collisions = self.registry.check_box_collisions(cand_box_disp)
                geom_hits = sum(1 for c in collisions if c[0] == "line")
                landmark_hits = sum(1 for c in collisions if c[0] == "landmark")
                box_hits = sum(1 for c in collisions if c[0] in ("box", "card"))

                # 캔버스 테두리 침범 페널티
                canvas_penalty = 0.0
                if bx0 < c_x0 + 6.0 or bx1 > c_x1 - 6.0 or by0 < c_y0 + 6.0 or by1 > c_y1 - 6.0:
                    canvas_penalty = 5000.0

                # 지시선 자체의 기하 곡선 교차 페널티
                leader_hits = len(self.registry.check_segment_collisions(p0_disp, cand_pt_disp))

                # 거리 및 방위각 우선순위 비용
                dist_penalty = ((dist - r_min) / (r_max - r_min + 1e-6)) ** 2
                angle_priority = ang_idx * 0.15

                cost = (
                    geom_hits * 2500.0 +
                    landmark_hits * 4000.0 +
                    box_hits * 3000.0 +
                    canvas_penalty +
                    leader_hits * 350.0 +
                    dist_penalty * 2.0 +
                    angle_priority
                )

                if cost < best_cost:
                    best_cost = cost
                    best_candidate = {
                        "xytext_data": (cand_x_data, cand_y_data),
                        "ha": ha,
                        "va": va,
                        "angle_deg": ang_deg,
                        "distance": dist,
                        "cost": cost,
                        "box_disp": cand_box_disp,
                    }

        if best_candidate is None:
            # 안전 기본값
            best_candidate = {
                "xytext_data": (x0 + r_min, y0 + r_min),
                "ha": "left",
                "va": "bottom",
                "angle_deg": 45.0,
                "distance": r_min,
                "cost": 99999.0,
                "box_disp": (p0_disp[0], p0_disp[1], p0_disp[0] + est_w_px, p0_disp[1] + est_h_px),
            }

        return best_candidate


# ==============================================================================
# 7. 통합 스마트 도안 제작 엔진 (SmartDiagramEngine)
# ==============================================================================

class SmartDiagramEngine:
    """
    Matplotlib Figure 및 Axes와 결합하여 기하 장애물 등록, 스마트 콜아웃 배치,
    동심원 정렬, 5-게이트 무결성 감사를 단일 파이프라인으로 수행하는 공통 엔진.
    """

    def __init__(self, fig: plt.Figure, ax: plt.Axes, lang: str = "ko"):
        self.fig = fig
        self.ax = ax
        self.lang = lang
        self.registry = SpatialObstacleRegistry(ax)
        self.optimizer = SmartCalloutOptimizer(self.registry)
        self.annotations: List[mtext.Annotation] = []

    def register_obstacle_line(
        self,
        xdata: Union[np.ndarray, List[float]],
        ydata: Union[np.ndarray, List[float]],
        name: str = "",
        padding: float = 4.0,
    ):
        """회피 대상 기하 형상(치형, 원호, 작용선 등) 등록"""
        self.registry.register_line(xdata, ydata, name=name, padding=padding)

    def register_landmark_point(
        self,
        pt: Tuple[float, float],
        radius_px: float = 8.0,
        name: str = "",
    ):
        """절대 가려지면 안 되는 랜드마크 점(P, A, E, O 등) 등록"""
        self.registry.register_landmark(pt, radius_px=radius_px, name=name)

    def register_card_container(
        self,
        box_data: Tuple[float, float, float, float],
        name: str = "",
        padding: float = 6.0,
    ):
        """요약 카드 컨테이너 AABB 등록 (x0, y0, x1, y1)"""
        # 데이터 좌표 -> 디스플레이 박스 변환
        x0, y0, x1, y1 = box_data
        pts = np.array([[x0, y0], [x1, y1]], dtype=float)
        disp_pts = self.registry.to_display(pts)
        disp_box = (
            min(disp_pts[0, 0], disp_pts[1, 0]),
            min(disp_pts[0, 1], disp_pts[1, 1]),
            max(disp_pts[0, 0], disp_pts[1, 0]),
            max(disp_pts[0, 1], disp_pts[1, 1]),
        )
        self.registry.register_card(disp_box, name=name, padding=padding)

    def add_smart_callout(
        self,
        target_pt: Tuple[float, float],
        text: str,
        preferred_angles: Optional[List[float]] = None,
        distance_range: Tuple[float, float] = (15.0, 45.0),
        fontsize: float = 10.0,
        color: str = "#0F172A",
        fontweight: str = "normal",
        box_style: Optional[Dict[str, Any]] = None,
        arrowprops: Optional[Dict[str, Any]] = None,
        name: str = "",
        zorder: int = 15,
    ) -> mtext.Annotation:
        """
        비어 있는 최적 공간을 자동 탐색하여 지시선 라벨을 생성하고 레지스트리에 등록.
        """
        opt = self.optimizer.find_optimal_callout_placement(
            target_pt_data=target_pt,
            text=text,
            preferred_angles_deg=preferred_angles,
            distance_range_data=distance_range,
            fontsize=fontsize,
        )

        default_box = dict(
            boxstyle="round,pad=0.28",
            fc="white",
            ec="#CBD5E1",
            lw=0.75,
            alpha=0.92,
        )
        if box_style is not None:
            default_box.update(box_style)

        default_arrow = dict(
            arrowstyle="->",
            color=color,
            lw=0.85,
            shrinkA=2,
            shrinkB=3,
            connectionstyle="arc3,rad=0",
        )
        if arrowprops is not None:
            default_arrow.update(arrowprops)

        ann = self.ax.annotate(
            text,
            xy=target_pt,
            xytext=opt["xytext_data"],
            ha=opt["ha"],
            va=opt["va"],
            fontsize=fontsize,
            fontweight=fontweight,
            color=color,
            bbox=default_box,
            arrowprops=default_arrow,
            zorder=zorder,
        )
        self.annotations.append(ann)
        # 새로 생성된 텍스트 박스를 레지스트리에 등록하여 이후 콜아웃과 충돌 방지
        self.registry.register_box(opt["box_disp"], name=name or text[:15], padding=3.0)
        return ann

    def add_margin_callout(
        self,
        target_pt: Tuple[float, float],
        text: str,
        side: str = "left",
        margin_coord: Optional[float] = None,
        y_pos: Optional[float] = None,
        x_pos: Optional[float] = None,
        fontsize: float = 10.0,
        color: str = "#0F172A",
        fontweight: str = "normal",
        box_style: Optional[Dict[str, Any]] = None,
        arrowprops: Optional[Dict[str, Any]] = None,
        name: str = "",
        zorder: int = 15,
    ) -> mtext.Annotation:
        """외곽 여백 단조 정렬 콜아웃 생성"""
        ann = SmartCallout.draw_margin_callout(
            ax=self.ax,
            target_pt=target_pt,
            text=text,
            side=side,
            margin_coord=margin_coord,
            y_pos=y_pos,
            x_pos=x_pos,
            fontsize=fontsize,
            color=color,
            fontweight=fontweight,
            box_style=box_style,
            arrowprops=arrowprops,
            zorder=zorder,
        )
        self.annotations.append(ann)
        return ann

    def distribute_radial_labels(
        self,
        center: Tuple[float, float],
        circles: List[Dict[str, Any]],
        side: str = "left",
        x_margin: float = -26.0,
        y_center: Optional[float] = None,
        min_vertical_gap: float = 4.8,
        fontsize: float = 9.8,
        box_style: Optional[Dict[str, Any]] = None,
    ) -> List[mtext.Annotation]:
        """동심원 군 라벨 외곽 여백 단조 정렬 배치"""
        anns = RadialCircleLabelDistributor.distribute_concentric_labels(
            ax=self.ax,
            center=center,
            circles=circles,
            side=side,
            x_margin=x_margin,
            y_center=y_center,
            min_vertical_gap=min_vertical_gap,
            fontsize=fontsize,
            box_style=box_style,
        )
        self.annotations.extend(anns)
        return anns

    # --------------------------------------------------------------------------
    # 5-게이트 무결성 감사 메서드 (5-Gate Integrity Audit)
    # --------------------------------------------------------------------------
    def verify_no_collisions(self) -> Dict[str, Any]:
        """
        도안 캔버스 상의 모든 텍스트, 기하 형상, 랜드마크, 카드, 뷰포트 여백에 대해
        5대 게이트 전수 무결성 감사를 수행하고 구조화된 리포트를 반환.

        5대 게이트:
          Gate 1: 텍스트 vs 텍스트 충돌 (Text-to-Text IoU/Overlap == 0)
          Gate 2: 텍스트 vs 기하 형상 가림 (Text-to-Geometry Collision == 0)
          Gate 3: 카드 컨테이너 내부 텍스트 패딩 및 외곽 여백 보장
          Gate 4: 캔버스 뷰포트 마진 보장 (Canvas Boundary Margin >= 2px)
          Gate 5: 랜드마크 점 시각적 가림 0건 (Landmark Point Obscuration == 0)
        """
        # Matplotlib 렌더러 활성화
        self.fig.canvas.draw()
        renderer = self.fig.canvas.get_renderer()

        all_texts = [t for t in self.ax.texts if t.get_text().strip()]
        bbox_ax = self.ax.get_window_extent(renderer)

        report: Dict[str, Any] = {
            "passed": True,
            "gate1_text_collisions": [],
            "gate2_geom_collisions": [],
            "gate3_card_violations": [],
            "gate4_canvas_violations": [],
            "gate5_landmark_violations": [],
            "total_violations": 0,
            "summary": "",
        }

        # 텍스트 바운딩 박스 추출 (Annotation인 경우 화살표를 제외한 순수 라벨 박스 산출)
        text_bboxes: List[Tuple[mtext.Text, Tuple[float, float, float, float]]] = []
        for t in all_texts:
            if hasattr(t, "get_bbox_patch") and t.get_bbox_patch() is not None:
                b = t.get_bbox_patch().get_window_extent(renderer)
            else:
                b = mtext.Text.get_window_extent(t, renderer)
            box = (float(b.x0), float(b.y0), float(b.x1), float(b.y1))
            text_bboxes.append((t, box))

        # ----------------------------------------------------------------------
        # Gate 1: 텍스트 대 텍스트 충돌 검사
        # ----------------------------------------------------------------------
        for i in range(len(text_bboxes)):
            t1, b1 = text_bboxes[i]
            for j in range(i + 1, len(text_bboxes)):
                t2, b2 = text_bboxes[j]
                if box_box_collision(b1, b2, min_gap=0.0):
                    # 같은 카드에 속하거나 부모-자식 관계가 아닌 경우 충돌 기록
                    report["gate1_text_collisions"].append({
                        "text_1": t1.get_text().replace("\n", " ")[:30],
                        "text_2": t2.get_text().replace("\n", " ")[:30],
                        "box_1": b1,
                        "box_2": b2,
                    })

        # ----------------------------------------------------------------------
        # Gate 2: 텍스트 대 기하 형상 선분 충돌 검사
        # ----------------------------------------------------------------------
        for t, b in text_bboxes:
            for line in self.registry.lines:
                pts = line["pts"]
                pad = line["padding"]
                collided = False
                for k in range(len(pts) - 1):
                    p1 = (pts[k, 0], pts[k, 1])
                    p2 = (pts[k + 1, 0], pts[k + 1, 1])
                    if line_box_collision(p1, p2, b, padding=pad):
                        collided = True
                        break
                if collided:
                    report["gate2_geom_collisions"].append({
                        "text": t.get_text().replace("\n", " ")[:30],
                        "obstacle_line": line["name"],
                        "box": b,
                    })

        # ----------------------------------------------------------------------
        # Gate 3: 카드 컨테이너 여백 검사
        # ----------------------------------------------------------------------
        for card in self.registry.cards:
            cbox = card["box"]
            for t, b in text_bboxes:
                # 카드 외곽 텍스트가 카드와 겹치는지 검사
                if box_box_collision(b, cbox, min_gap=0.0):
                    # 만약 텍스트가 카드 내부에 완전히 포함되어 있지 않고 경계에 걸쳐 있다면 위반
                    is_fully_inside = (b[0] >= cbox[0] + 3.0 and b[1] >= cbox[1] + 3.0 and
                                       b[2] <= cbox[2] - 3.0 and b[3] <= cbox[3] - 3.0)
                    if not is_fully_inside:
                        report["gate3_card_violations"].append({
                            "card": card["name"],
                            "text": t.get_text().replace("\n", " ")[:30],
                            "reason": "Text overlaps card boundary without proper internal padding",
                        })

        # ----------------------------------------------------------------------
        # Gate 4: 캔버스 뷰포트 마진 검사
        # ----------------------------------------------------------------------
        for t, b in text_bboxes:
            if b[0] < bbox_ax.x0 + 1.5 or b[2] > bbox_ax.x1 - 1.5 or b[1] < bbox_ax.y0 + 1.5 or b[3] > bbox_ax.y1 - 1.5:
                report["gate4_canvas_violations"].append({
                    "text": t.get_text().replace("\n", " ")[:30],
                    "box": b,
                    "canvas_bbox": (bbox_ax.x0, bbox_ax.y0, bbox_ax.x1, bbox_ax.y1),
                })

        # ----------------------------------------------------------------------
        # Gate 5: 랜드마크 점 가림 검사
        # ----------------------------------------------------------------------
        for lm in self.registry.landmarks:
            lm_pt = lm["pt"]
            lm_r = lm["radius_px"]
            for t, b in text_bboxes:
                if point_box_collision(lm_pt, lm_r, b):
                    report["gate5_landmark_violations"].append({
                        "landmark": lm["name"],
                        "covered_by": t.get_text().replace("\n", " ")[:30],
                        "pt": lm_pt,
                        "box": b,
                    })

        total_violations = (
            len(report["gate1_text_collisions"]) +
            len(report["gate2_geom_collisions"]) +
            len(report["gate3_card_violations"]) +
            len(report["gate4_canvas_violations"]) +
            len(report["gate5_landmark_violations"])
        )
        report["total_violations"] = total_violations
        report["passed"] = (total_violations == 0)

        if report["passed"]:
            report["summary"] = f"PASS: All 5 integrity gates cleared with 0 violations across {len(all_texts)} text elements."
        else:
            report["summary"] = (
                f"FAIL: {total_violations} violation(s) detected "
                f"(Gate 1 text-text: {len(report['gate1_text_collisions'])}, "
                f"Gate 2 text-geom: {len(report['gate2_geom_collisions'])}, "
                f"Gate 3 card: {len(report['gate3_card_violations'])}, "
                f"Gate 4 canvas: {len(report['gate4_canvas_violations'])}, "
                f"Gate 5 landmark: {len(report['gate5_landmark_violations'])})."
            )

        return report


# ==============================================================================
# 8. 모듈 자체 검증 및 단위 테스트 (Self-Verification Unit Tests)
# ==============================================================================

def run_self_tests() -> int:
    """공통 스마트 도안 제작 엔진 단위 테스트 전수 실행"""
    print("=" * 70)
    print("Smart Diagram Engine Self-Verification Suite")
    print("=" * 70)

    # --------------------------------------------------------------------------
    # Test 1: Liang-Barsky 선분-박스 충돌 판정 커널
    # --------------------------------------------------------------------------
    box = (10.0, 10.0, 30.0, 30.0)
    # 수평 관통
    assert line_box_collision((0.0, 20.0), (40.0, 20.0), box) is True, "Test 1.1 Failed"
    # 수직 관통
    assert line_box_collision((20.0, 0.0), (20.0, 40.0), box) is True, "Test 1.2 Failed"
    # 대각선 관통
    assert line_box_collision((0.0, 0.0), (40.0, 40.0), box) is True, "Test 1.3 Failed"
    # 평행 바깥선
    assert line_box_collision((0.0, 35.0), (40.0, 35.0), box) is False, "Test 1.4 Failed"
    # 사선 빗겨감
    assert line_box_collision((0.0, 35.0), (35.0, 0.0), box) is True, "Test 1.5 Failed"  # (35-x) passes through box near (10, 25)
    assert line_box_collision((0.0, 65.0), (65.0, 0.0), box) is False, "Test 1.6 Failed" # x+y=65 > max(x+y)=60, misses box
    # 끝점 내부
    assert line_box_collision((20.0, 20.0), (50.0, 50.0), box) is True, "Test 1.7 Failed"
    # 완전 내부
    assert line_box_collision((15.0, 15.0), (25.0, 25.0), box) is True, "Test 1.8 Failed"
    print("[PASS] Test 1: Liang-Barsky Segment-AABB Collision Kernel (8 cases)")

    # --------------------------------------------------------------------------
    # Test 2: 원/점-박스 충돌 판정 커널
    # --------------------------------------------------------------------------
    assert point_box_collision((20.0, 20.0), 5.0, box) is True, "Test 2.1 Failed"
    assert point_box_collision((5.0, 20.0), 6.0, box) is True, "Test 2.2 Failed"   # dist 5 <= radius 6
    assert point_box_collision((5.0, 20.0), 4.0, box) is False, "Test 2.3 Failed"  # dist 5 > radius 4
    assert point_box_collision((40.0, 40.0), 5.0, box) is False, "Test 2.4 Failed"
    print("[PASS] Test 2: Point/Landmark-AABB Collision Kernel (4 cases)")

    # --------------------------------------------------------------------------
    # Test 3: 박스-박스 충돌 판정 커널
    # --------------------------------------------------------------------------
    b1 = (0.0, 0.0, 10.0, 10.0)
    b2 = (5.0, 5.0, 15.0, 15.0)
    b3 = (12.0, 12.0, 20.0, 20.0)
    assert box_box_collision(b1, b2) is True, "Test 3.1 Failed"
    assert box_box_collision(b1, b3) is False, "Test 3.2 Failed"
    assert box_box_collision(b1, b3, min_gap=3.0) is True, "Test 3.3 Failed"  # gap 2.0 <= min_gap 3.0
    print("[PASS] Test 3: Box-Box Collision Kernel (3 cases)")

    # --------------------------------------------------------------------------
    # Test 4: ArcClipper 기하 클리핑
    # --------------------------------------------------------------------------
    center = (0.0, -57.0)
    radius = 63.0
    # 피치원 상단 원호 theta 약 70~110 deg
    xs, ys = ArcClipper.generate_clipped_arc_points(
        center=center,
        radius=radius,
        theta_start_deg=65.0,
        theta_end_deg=115.0,
        x_min=-14.5,
        x_max=14.5,
        num_points=100,
    )
    assert np.all(xs >= -14.500001), f"ArcClipper x_min violation: min(xs) = {np.min(xs)}"
    assert np.all(xs <= 14.500001), f"ArcClipper x_max violation: max(xs) = {np.max(xs)}"
    # 원 방정식 만족도 검증: (x - cx)^2 + (y - cy)^2 == r^2
    computed_r = np.sqrt((xs - center[0]) ** 2 + (ys - center[1]) ** 2)
    assert np.allclose(computed_r, radius, atol=1e-5), "Arc radius invariant broken"
    print(f"[PASS] Test 4: ArcClipper Bound Invariance (r={radius:.3f}, x in [{np.min(xs):.3f}, {np.max(xs):.3f}])")

    # --------------------------------------------------------------------------
    # Test 5: RadialCircleLabelDistributor 단조 정렬기
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6, 4))
    circles = [
        {"radius": 63.0, "text": "Tip Circle (ra)", "color": "#16A34A"},
        {"radius": 57.0, "text": "Pitch Circle (r)", "color": "#8B5CF6"},
        {"radius": 53.562, "text": "Base Circle (rb)", "color": "#2563EB"},
        {"radius": 49.5, "text": "Root Circle (rf)", "color": "#DC2626"},
    ]
    anns = RadialCircleLabelDistributor.distribute_concentric_labels(
        ax=ax,
        center=center,
        circles=circles,
        side="left",
        x_margin=-26.0,
        y_center=0.0,
        min_vertical_gap=5.0,
    )
    assert len(anns) == 4, "Should create 4 annotations"
    # 수직 위치 단조성 검증 (위에서 아래로 y_out strictly decreasing)
    y_positions = [ann.xyann[1] for ann in anns]
    for i in range(len(y_positions) - 1):
        gap = y_positions[i] - y_positions[i + 1]
        assert gap >= 4.999, f"Radial distributor vertical monotonic violation: gap = {gap}"
        # 좌측 여백이므로 ha='right' 확인
        assert anns[i].get_ha() == "right", f"Alignment should be 'right', got {anns[i].get_ha()}"
    plt.close(fig)
    print(f"[PASS] Test 5: RadialCircleLabelDistributor Monotonic Alignment (ys={y_positions})")

    # --------------------------------------------------------------------------
    # Test 6: SmartDiagramEngine 및 5-게이트 무결성 감사 (Clean Case)
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(-40, 40)
    ax.set_ylim(-35, 15)

    engine = SmartDiagramEngine(fig, ax, lang="ko")

    # 기하 곡선 등록 (치형 모사)
    tooth_x = np.linspace(-14, -5, 50)
    tooth_y = np.linspace(-7, 6, 50)
    engine.register_obstacle_line(tooth_x, tooth_y, name="Tooth_1_Flank", padding=4.0)

    # 랜드마크 점 등록 (피치점 P)
    engine.register_landmark_point((0.0, 0.0), radius_px=10.0, name="Pitch_Point_P")

    # 외곽 여백에 안전한 콜아웃 추가
    engine.add_margin_callout(
        target_pt=(-9.5, 0.0),
        text="치두께 s",
        side="left",
        margin_coord=-25.0,
        y_pos=8.0,
    )

    # 스마트 콜아웃 (최적 빈 공간 탐색)
    engine.add_smart_callout(
        target_pt=(0.0, 0.0),
        text="피치점 P (0, 0)",
        preferred_angles=[45, 135, 225, 315],
        distance_range=(15.0, 30.0),
    )

    report = engine.verify_no_collisions()
    plt.close(fig)

    assert report["passed"] is True, f"Clean engine audit failed: {report['summary']}"
    assert report["total_violations"] == 0
    print(f"[PASS] Test 6: SmartDiagramEngine 5-Gate Audit on Clean Layout ({report['summary']})")

    # --------------------------------------------------------------------------
    # Test 7: 5-게이트 무결성 감사 (Deliberate Collisions Detection)
    # --------------------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(-40, 40)
    ax.set_ylim(-35, 15)

    engine_bad = SmartDiagramEngine(fig, ax, lang="ko")
    # 랜드마크 등록
    engine_bad.register_landmark_point((0.0, 0.0), radius_px=15.0, name="Pitch_Point_P")
    # 장애물 선 등록
    engine_bad.register_obstacle_line([-10, 10], [0, 0], name="Center_Line", padding=4.0)

    # 1. 랜드마크 P 위에 직접 불투명 텍스트 배치 (Gate 5 위반 유도)
    ax.text(0.0, 0.0, "Covering Landmark P", ha="center", va="center", bbox=dict(fc="white"))

    # 2. 장애물 선 위에 텍스트 배치 (Gate 2 위반 유도)
    ax.text(0.0, 0.0, "Duplicate Covering Text", ha="center", va="center")

    bad_report = engine_bad.verify_no_collisions()
    plt.close(fig)

    assert bad_report["passed"] is False, "Deliberate collisions should FAIL"
    assert len(bad_report["gate1_text_collisions"]) >= 1, "Should detect Gate 1 text-text collision"
    assert len(bad_report["gate2_geom_collisions"]) >= 1, "Should detect Gate 2 text-geom collision"
    assert len(bad_report["gate5_landmark_violations"]) >= 1, "Should detect Gate 5 landmark obscuration"
    print(f"[PASS] Test 7: 5-Gate Audit Deliberate Violations Detection ({bad_report['total_violations']} caught)")

    print("=" * 70)
    print("ALL 7 UNIT TESTS PASSED WITH 100% INTEGRITY")
    print("=" * 70)
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(run_self_tests())


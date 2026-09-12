"""
TEAM ZERODAY Module 4: Lunar Correspondence Graph
Constructs a structural Delaunay topological graph over correspondence points
to analyze terrain deformation, relative geometry, and neighborhood consistency.
"""
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Tuple
import numpy as np
from scipy.spatial import Delaunay


@dataclass
class GraphNode:
    id: int
    match_id: int
    src_x: float
    src_y: float
    ref_x: float
    ref_y: float


@dataclass
class GraphEdge:
    source_node: int
    target_node: int
    src_length_px: float
    ref_length_px: float
    length_ratio: float
    strain_index: float  # [0.0, 1.0] deviation from median stretch
    is_topologically_sound: bool


@dataclass
class LunarGraphRepresentation:
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    mean_strain: float
    topological_inversion_count: int
    structural_integrity_score: float  # [0.0, 1.0]


class LunarCorrespondenceGraph:
    """Builds and analyzes the structural correspondence topology over lunar terrain."""

    @staticmethod
    def build_graph(
        src_points: np.ndarray,  # N x 2
        ref_points: np.ndarray,  # N x 2
        match_ids: np.ndarray | None = None,
        max_nodes: int = 150
    ) -> LunarGraphRepresentation:
        """
        Constructs Delaunay triangulation graphs and evaluates structural strain.
        """
        n = len(src_points)
        if n < 4:
            return LunarGraphRepresentation(
                nodes=[],
                edges=[],
                mean_strain=0.0,
                topological_inversion_count=0,
                structural_integrity_score=1.0
            )

        # Subsample if too many nodes to ensure smooth rendering
        if n > max_nodes:
            step = n // max_nodes
            sub_indices = np.arange(0, n, step)[:max_nodes]
            s_pts = src_points[sub_indices]
            r_pts = ref_points[sub_indices]
            node_ids = list(range(len(sub_indices)))
            selected_match_ids = match_ids[sub_indices] if match_ids is not None else np.array(node_ids)
        else:
            s_pts = src_points
            r_pts = ref_points
            node_ids = list(range(n))
            selected_match_ids = match_ids if match_ids is not None else np.arange(n)

        # Delaunay Triangulation on source points
        try:
            tri = Delaunay(s_pts)
        except Exception:
            return LunarGraphRepresentation([], [], 0.0, 0, 1.0)

        nodes = [
            GraphNode(
                id=int(node_ids[i]),
                match_id=int(selected_match_ids[i]),
                src_x=round(float(s_pts[i, 0]), 2),
                src_y=round(float(s_pts[i, 1]), 2),
                ref_x=round(float(r_pts[i, 0]), 2),
                ref_y=round(float(r_pts[i, 1]), 2)
            )
            for i in range(len(s_pts))
        ]

        # Extract unique edges from Delaunay simplices
        edge_set = set()
        inversion_count = 0

        for simplex in tri.simplices:
            # Check triangle orientation (signed area) in source vs reference
            # Source orientation
            p0, p1, p2 = s_pts[simplex[0]], s_pts[simplex[1]], s_pts[simplex[2]]
            area_s = (p1[0] - p0[0]) * (p2[1] - p0[1]) - (p1[1] - p0[1]) * (p2[0] - p0[0])

            # Ref orientation
            r0, r1, r2 = r_pts[simplex[0]], r_pts[simplex[1]], r_pts[simplex[2]]
            area_r = (r1[0] - r0[0]) * (r2[1] - r0[1]) - (r1[1] - r0[1]) * (r2[0] - r0[0])

            # If signs differ, triangle was topologically flipped/inverted
            if (area_s * area_r) < 0:
                inversion_count += 1

            # Add undirected edges
            for u, v in [(simplex[0], simplex[1]), (simplex[1], simplex[2]), (simplex[2], simplex[0])]:
                edge_set.add((min(u, v), max(u, v)))

        # Evaluate edge stretch and strain
        raw_edges = []
        ratios = []
        for u, v in edge_set:
            len_s = float(np.linalg.norm(s_pts[u] - s_pts[v]))
            len_r = float(np.linalg.norm(r_pts[u] - r_pts[v]))
            ratio = len_r / (len_s + 1e-6)
            ratios.append(ratio)
            raw_edges.append((u, v, len_s, len_r, ratio))

        median_ratio = float(np.median(ratios)) if ratios else 1.0

        graph_edges = []
        strains = []
        for u, v, len_s, len_r, ratio in raw_edges:
            strain = abs(ratio - median_ratio) / (median_ratio + 1e-6)
            norm_strain = float(np.clip(strain, 0.0, 1.0))
            strains.append(norm_strain)
            graph_edges.append(GraphEdge(
                source_node=int(node_ids[u]),
                target_node=int(node_ids[v]),
                src_length_px=round(len_s, 2),
                ref_length_px=round(len_r, 2),
                length_ratio=round(ratio, 3),
                strain_index=round(norm_strain, 3),
                is_topologically_sound=(norm_strain < 0.35)
            ))

        mean_strain = float(np.mean(strains)) if strains else 0.0
        integrity = float(np.clip(1.0 - mean_strain - (inversion_count / (len(tri.simplices) + 1e-6)), 0.0, 1.0))

        return LunarGraphRepresentation(
            nodes=nodes,
            edges=graph_edges,
            mean_strain=round(mean_strain, 3),
            topological_inversion_count=inversion_count,
            structural_integrity_score=round(integrity, 3)
        )

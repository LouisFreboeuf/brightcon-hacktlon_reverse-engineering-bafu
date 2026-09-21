"""One factorised technosphere; cumulative inventories and EF 3.1 characterisation on demand."""

from __future__ import annotations

import numpy as np
import scipy.sparse.linalg as spl
import bw2calc as bc
import bw2data as bd

from .db import methods


class System:
    """Build the matrices once for a demand and reuse the LU factorisation for every column."""

    def __init__(self, demand_activity):
        self.methods = methods()
        self.lca = bc.LCA({demand_activity.id: 1}, self.methods[0])
        self.lca.lci()
        self.A = self.lca.technosphere_matrix.tocsc()
        self.B = self.lca.biosphere_matrix.tocsr()
        self.lu = spl.splu(self.A)
        self.n_flows = self.B.shape[0]
        self._cf: np.ndarray | None = None

    def cumulative(self, activity_ids: list[int]) -> np.ndarray:
        """B A^-1 e_j for each activity: columns of cumulative elementary flows."""
        D = np.zeros((self.A.shape[1], len(activity_ids)))
        for j, i in enumerate(activity_ids):
            D[self.lca.dicts.activity[i], j] = 1.0
        return np.asarray(self.B @ self.lu.solve(D))

    @property
    def cf(self) -> np.ndarray:
        """Characterisation factors, one row per EF 3.1 category (n_methods x n_flows)."""
        if self._cf is None:
            rows = []
            for m in self.methods:
                self.lca.switch_method(m)
                self.lca.lcia()
                rows.append(np.asarray(self.lca.characterization_matrix.diagonal()).ravel())
            self._cf = np.array(rows)
        return self._cf

    def scores(self, inventory: np.ndarray) -> np.ndarray:
        return self.cf @ inventory

    def flow_weights(self, target: np.ndarray, category_weights: dict[str, float] | None = None) -> np.ndarray:
        """Row weights so that every category counts equally (or as ``category_weights`` says, keyed
        by EF category name, default 1). Each category is normalised by the sum of the absolute
        characterised contributions in the target, not by its net score: a net score can be tiny
        through cancellation (biogenic CO2 uptake vs release) and would blow the weights up to 1e20,
        after which the fit only cares about that one category."""
        w = np.zeros(self.n_flows)
        cw = category_weights or {}
        for m, c in zip(self.methods, self.cf):
            total = float(np.abs(c * target).sum())
            if total > 0:
                w += cw.get(m[2], 1.0) * np.abs(c) / total
        return w

    def flow_key(self, row: int) -> tuple[str, str]:
        node = bd.get_node(id=self.lca.dicts.biosphere.reversed[row])
        return node["database"], node["code"]

    def flow_label(self, row: int) -> str:
        node = bd.get_node(id=self.lca.dicts.biosphere.reversed[row])
        cats = node.get("categories") or ()
        return f"{node['name']} [{'/'.join(str(c) for c in cats[:2])}] ({node.get('unit', '')})"

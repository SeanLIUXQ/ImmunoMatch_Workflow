from __future__ import annotations

from pathlib import Path

import pandas as pd

from .cache import ModelCache, PairScoreCache, score_batch


class ImprovedImmunoMatchScorer:
    def __init__(self, model_root: Path, device: str = "cpu") -> None:
        self.model_root = Path(model_root)
        self.device = device
        self.model_cache = ModelCache()
        self.pair_cache = PairScoreCache()

    @staticmethod
    def _split_by_locus(df: pd.DataFrame, locus_col: str) -> tuple[pd.DataFrame, pd.DataFrame]:
        kappa = df.loc[df[locus_col].astype(str).str.contains("IGK", na=False)].copy()
        lam = df.loc[df[locus_col].astype(str).str.contains("IGL", na=False)].copy()
        return kappa, lam

    def _score_subset(self, subset: pd.DataFrame, locus_col: str, hseq_col: str, lseq_col: str, model_name: str) -> pd.DataFrame:
        if subset.empty:
            return subset.assign(pairing_scores=[])

        bundle = self.model_cache.get(self.model_root, model_name)
        subset = subset.copy()
        subset["_cache_key"] = [self.pair_cache.make_key(str(r[hseq_col]), str(r[lseq_col]), str(r[locus_col]), model_name) for _, r in subset.iterrows()]

        unique_mask = ~subset["_cache_key"].duplicated()
        unique_rows = subset.loc[unique_mask, [hseq_col, lseq_col, locus_col, "_cache_key"]].copy()

        missing = unique_rows.loc[~unique_rows["_cache_key"].map(self.pair_cache.has)]
        if not missing.empty:
            scores = score_batch(
                bundle.tokenizer,
                bundle.model,
                missing[hseq_col].tolist(),
                missing[lseq_col].tolist(),
                device=self.device,
            )
            for key, score in zip(missing["_cache_key"].tolist(), scores, strict=False):
                self.pair_cache.set(key, score)

        subset["pairing_scores"] = subset["_cache_key"].map(self.pair_cache.get)
        return subset.drop(columns=["_cache_key"])

    def score_dataframe(self, data: pd.DataFrame, hseq_col: str, lseq_col: str, locus_col: str) -> pd.DataFrame:
        kappa, lam = self._split_by_locus(data, locus_col)
        scored_k = self._score_subset(kappa, locus_col, hseq_col, lseq_col, "immunomatch-kappa")
        scored_l = self._score_subset(lam, locus_col, hseq_col, lseq_col, "immunomatch-lambda")
        scored = pd.concat([scored_k, scored_l], ignore_index=False)
        return scored.sort_index().reset_index(drop=True)

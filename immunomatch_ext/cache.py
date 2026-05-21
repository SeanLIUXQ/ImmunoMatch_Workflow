from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import torch
from transformers import RoFormerForSequenceClassification, RoFormerTokenizer


@dataclass
class ModelBundle:
    tokenizer: RoFormerTokenizer
    model: RoFormerForSequenceClassification


class ModelCache:
    def __init__(self) -> None:
        self._bundles: Dict[Tuple[str, str], ModelBundle] = {}

    def get(self, model_root: Path, model_name: str) -> ModelBundle:
        key = (str(model_root.resolve()), model_name)
        if key not in self._bundles:
            model_dir = model_root / model_name
            tokenizer = RoFormerTokenizer.from_pretrained(model_dir)
            model = RoFormerForSequenceClassification.from_pretrained(model_dir)
            model.eval()
            self._bundles[key] = ModelBundle(tokenizer=tokenizer, model=model)
        return self._bundles[key]


class PairScoreCache:
    def __init__(self) -> None:
        self._scores: Dict[Tuple[str, str, str, str], float] = {}

    @staticmethod
    def make_key(vh: str, vl: str, locus: str, model_name: str) -> Tuple[str, str, str, str]:
        return (vh, vl, locus, model_name)

    def has(self, key: Tuple[str, str, str, str]) -> bool:
        return key in self._scores

    def get(self, key: Tuple[str, str, str, str]) -> float:
        return self._scores[key]

    def set(self, key: Tuple[str, str, str, str], value: float) -> None:
        self._scores[key] = float(value)


def score_batch(tokenizer, model, h_values, l_values, device: str = "cpu", batch_size: int = 64) -> list[float]:
    scores: list[float] = []
    with torch.no_grad():
        for start in range(0, len(h_values), batch_size):
            end = start + batch_size
            h_batch = [" ".join(list(str(seq))) for seq in h_values[start:end]]
            l_batch = [" ".join(list(str(seq))) for seq in l_values[start:end]]
            encoded = tokenizer(
                h_batch,
                l_batch,
                padding="max_length",
                truncation=True,
                max_length=256,
                return_tensors="pt",
            )
            encoded = {k: v.to(device) for k, v in encoded.items()}
            logits = model(**encoded).logits
            probs = torch.softmax(logits, dim=1)[:, 1].detach().cpu().tolist()
            scores.extend(float(x) for x in probs)
    return scores

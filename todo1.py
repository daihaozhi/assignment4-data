
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import fasttext


def _candidate_model_paths() -> list[Path]:
    env_path = os.environ.get("FASTTEXT_LID_MODEL")
    candidates = [
        Path(env_path) if env_path else None,
        Path("lid.176.bin"),
        Path("lid.176.ftz"),
        Path("/data/lid.176.bin"),
        Path("/data/lid.176.ftz"),
    ]
    return [p for p in candidates if p is not None]


@lru_cache(maxsize=1)
def _load_lid_model() -> Any:
    for path in _candidate_model_paths():
        if path.exists():
            return fasttext.load_model(str(path))
    raise FileNotFoundError(
        "Cannot find fastText language ID model. "
        "Set FASTTEXT_LID_MODEL or place lid.176.bin/lid.176.ftz in current directory."
    )


def run_identify_language(text: str) -> tuple[Any, float]:
    normalized = text.strip().replace("\n", " ")
    if not normalized:
        return "unk", 0.0

    model = _load_lid_model()
    labels, scores = model.predict(normalized, k=1)
    label = labels[0].removeprefix("__label__") if labels else "unk"
    score = float(scores[0]) if scores else 0.0
    return label, score

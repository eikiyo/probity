import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "engine"))
from runner import run_leaf, FAST_SET  # noqa: E402
if __name__ == "__main__":
    run_leaf(Path(__file__).parent, model_set=FAST_SET)

import os
from pathlib import Path


def resolve_seed_data_path() -> Path:
    """Resolves the path to the stadium_seed_data.json file.
    
    Checks:
    1. DEMO__SEED_DATA_PATH environment variable.
    2. Package-relative path inside atlas_core.
    3. Monorepo directory parents lookup.
    
    Raises:
        FileNotFoundError: If the seed data file cannot be found anywhere.
    """
    # 1. Configurable environment variable
    env_path = os.getenv("DEMO__SEED_DATA_PATH")
    if env_path:
        p = Path(env_path)
        if not p.exists():
            raise FileNotFoundError(
                f"Stadium seed data file not found at path configured via DEMO__SEED_DATA_PATH: {p.resolve()}"
            )
        return p

    # 2. Package-relative path inside atlas_core
    try:
        import atlas_core
        package_dir = Path(atlas_core.__file__).resolve().parent
        p = package_dir / "resources" / "stadium_seed_data.json"
        if p.exists():
            return p
    except Exception:
        pass

    # 3. Monorepo folder parent lookup (local development/tests fallback)
    current_dir = Path(__file__).resolve()
    for parent in current_dir.parents:
        p = parent / "packages" / "atlas-core" / "src" / "atlas_core" / "resources" / "stadium_seed_data.json"
        if p.exists():
            return p
        # Also check root data or config if any
        p_root = parent / "stadium_seed_data.json"
        if p_root.exists():
            return p_root

    raise FileNotFoundError(
        "Stadium seed data file (stadium_seed_data.json) could not be resolved. "
        "Ensure the file exists in the package resources directory or define DEMO__SEED_DATA_PATH."
    )

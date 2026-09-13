import os
import shutil

def create_latest_symlink(target_path: str) -> str:
    """Creates or updates a 'latest.json' symlink pointing to target_path within its directory."""
    directory = os.path.dirname(target_path)
    target_basename = os.path.basename(target_path)
    symlink_path = os.path.join(directory, "latest.json") if directory else "latest.json"
    
    if os.path.lexists(symlink_path):
        os.remove(symlink_path)
        
    os.symlink(target_basename, symlink_path)
    return symlink_path

def reconstitute(kg_path: str, output_path: str) -> str:
    """
    Mock reconstitution phase: copies the winning KG across the boundary to the secure
    reconstituted zone and maintains a 'latest.json' symlink pointing to the newest KG.
    """
    if not os.path.exists(kg_path):
        raise FileNotFoundError(f"Source knowledge graph not found: {kg_path}")

    out_dir = os.path.dirname(output_path)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)

    shutil.copy2(kg_path, output_path)
    create_latest_symlink(output_path)
    return output_path

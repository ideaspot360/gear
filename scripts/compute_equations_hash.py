"""
Compute SHA-256 hash of KaTeX equation blocks in an MDX file.
Used for frontmatter equations_hash invariant verification.
"""
import hashlib
import re
import sys
from pathlib import Path

def compute_hash(mdx_path: Path) -> str:
    content = mdx_path.read_text(encoding='utf-8')
    # Find all $$ display math blocks
    display_blocks = re.findall(r'\$\$(.*?)\$\$', content, re.DOTALL)
    normalized = "\n---\n".join(b.strip() for b in display_blocks)
    return hashlib.sha256(normalized.encode('utf-8')).hexdigest()

if __name__ == '__main__':
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("blog/src/content/docs/ko/part01-kinematics/01-why-gears.mdx")
    h = compute_hash(target)
    print(f"Equations hash: {h}")

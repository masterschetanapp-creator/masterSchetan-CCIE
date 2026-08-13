import os

FORBIDDEN_PATTERNS = [
    "p_val = 50.0",
    "i_val = 25.0",
    "fii_pct = i_val * 0.70",
    "dii_pct = i_val * 0.30",
    "45.2%",
    "2026-10-27"
]

def test_no_forbidden_fallbacks_in_source():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dirs = ["ui", "data", "core", "analysis"]
    
    for d in target_dirs:
        dir_path = os.path.join(repo_dir, d)
        if not os.path.exists(dir_path):
            continue
        for fname in os.listdir(dir_path):
            if fname.endswith(".py"):
                fpath = os.path.join(dir_path, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                    for pat in FORBIDDEN_PATTERNS:
                        assert pat not in content, f"Forbidden fallback '{pat}' found in {fpath}"

if __name__ == "__main__":
    test_no_forbidden_fallbacks_in_source()
    print("test_no_fabricated_fallbacks PASSED")

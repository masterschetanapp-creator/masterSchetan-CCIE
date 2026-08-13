import os

def test_renderers_do_not_reclassify_sectors():
    repo_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for fname in ["ui/common_man_view.py", "ui/simple_view.py"]:
        fpath = os.path.join(repo_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()
            assert "classify_company_type(" not in content, f"Renderer {fname} must not call classify_company_type"

if __name__ == "__main__":
    test_renderers_do_not_reclassify_sectors()
    print("test_renderer_integrity PASSED")

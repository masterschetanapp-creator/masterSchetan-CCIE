from core.entity_resolver import resolve_stock

def test_entity_resolution():
    res1 = resolve_stock("PNB")
    assert res1 is not None
    assert res1["symbol"] == "PNB.NS"

    res2 = resolve_stock("BAJFINANCE")
    assert res2 is not None
    assert res2["symbol"] == "BAJFINANCE.NS"

    res3 = resolve_stock("SUZLON")
    assert res3 is not None
    assert res3["symbol"] == "SUZLON.NS"

    res_invalid = resolve_stock("ABCXYZ")
    assert res_invalid is None

if __name__ == "__main__":
    test_entity_resolution()
    print("test_entity_resolution PASSED")

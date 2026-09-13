def test_pydantic_installed():
    try:
        import pydantic
        assert True
    except ImportError:
        assert False, "Pydantic is not installed"

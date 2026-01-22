import pytest

class TestMain:
    def test_import_main(self):
        import main
        assert hasattr(main, "app")

    def test_cookiecutter_fields(self):
        from main import COOKIECUTTER_FIELDS
        assert len(COOKIECUTTER_FIELDS) > 0
        assert "crewai_project_name" in COOKIECUTTER_FIELDS

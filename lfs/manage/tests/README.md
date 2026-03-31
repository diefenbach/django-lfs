# LFS Manage Package Tests

Test suite für das LFS Manage Package mit pytest.

## Struktur

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Pytest fixtures und Konfiguration
├── test_static_blocks_views.py  # Tests für StaticBlock Views
├── test_utils.py            # Tests für Utility-Funktionen
└── README.md               # Diese Datei
```

## Fixtures

### Benutzer-Fixtures
- `manage_user`: Benutzer mit `manage_shop` Berechtigung
- `regular_user`: Normaler Benutzer ohne besondere Berechtigungen

### Daten-Fixtures
- `static_block`: Ein einzelner StaticBlock für Tests
- `multiple_static_blocks`: Mehrere StaticBlocks für Listen-Tests

### Request-Fixtures
- `request_factory`: Django RequestFactory
- `authenticated_request`: Factory für authentifizierte Requests

## Tests ausführen

### Alle Tests im manage Package
```bash
cd src/lfs/lfs/manage
pytest
```

### Spezifische Test-Datei
```bash
pytest tests/test_static_blocks_views.py
```

### Mit Coverage
```bash
pytest --cov=lfs.manage --cov-report=html
```

### Nur schnelle Tests
```bash
pytest -m "not slow"
```

## Test-Kategorien

### Unit Tests
- Testen einzelne Funktionen/Methoden isoliert
- Verwenden Mocks für Abhängigkeiten
- Schnell und deterministisch

### Integration Tests
- Testen Zusammenspiel mehrerer Komponenten
- Verwenden echte Datenbank (mit Fixtures)
- Langsamer aber realistischer

## TDD Prinzipien

Folge den Regeln aus den `.cursor/rules`:

1. **Red → Green → Refactor**
   - Schreibe zuerst einen fehlschlagenden Test
   - Schreibe minimalen Code zum Bestehen
   - Refaktoriere nur bei grünen Tests

2. **Test-Qualität**
   - Teste Verhalten, nicht Implementation
   - Klare, beschreibende Test-Namen
   - Ein Assert pro Test (wenn praktikabel)
   - Arrange-Act-Assert Struktur

3. **Test-Organisation**
   - Gruppiere verwandte Tests in Klassen
   - Verwende aussagekräftige Docstrings
   - Tests sollen unabhängig voneinander laufen

## Beispiele

### Einfacher Unit Test
```python
def test_static_block_tab_mixin_returns_correct_object(self, static_block):
    """Should return the StaticBlock for given id."""
    mixin = StaticBlockTabMixin()
    mixin.kwargs = {"id": static_block.id}
    
    result = mixin.get_static_block()
    
    assert result == static_block
```

### Integration Test
```python
def test_data_view_form_submission_saves_changes(self, authenticated_request, static_block):
    """Should save changes when valid form is submitted to data view."""
    form_data = {"name": "Updated Name"}
    request = authenticated_request("POST", f"/static-block/{static_block.id}/", data=form_data)
    
    view = StaticBlockDataView.as_view()
    response = view(request, id=static_block.id)
    
    assert response.status_code == 302
    static_block.refresh_from_db()
    assert static_block.name == "Updated Name"
```

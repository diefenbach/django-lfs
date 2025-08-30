# Flatpickr Integration für LFS Management

## Übersicht

Flatpickr v4.6.13 ist als moderner Date/Time Picker in das LFS Management System integriert.

## Dateien

```
lfs/manage/static/lfs/
├── css/
│   └── flatpickr.min.css          # Flatpickr Styles
├── js/
│   ├── flatpickr.min.js           # Flatpickr Core
│   ├── flatpickr-de.js            # Deutsche Lokalisierung
│   └── management/
│       └── flatpickr-init.js      # Auto-Initialisierung
```

## Verwendung in Templates

### 1. CSS und JS einbinden

```django
{% load static %}

<!-- Im <head> Bereich -->
<link rel="stylesheet" href="{% static 'lfs/css/flatpickr.min.css' %}">

<!-- Vor </body> -->
<script src="{% static 'lfs/js/flatpickr.min.js' %}"></script>
<script src="{% static 'lfs/js/flatpickr-de.js' %}"></script>
<script src="{% static 'lfs/js/management/flatpickr-init.js' %}"></script>
```

### 2. Automatische Initialisierung

Die folgenden CSS-Klassen werden automatisch erkannt:

```html
<!-- Nur Datum -->
<input type="text" class="date-picker" name="start_date">

<!-- Datum und Zeit -->
<input type="text" class="datetime-picker" name="created_at">

<!-- Nur Zeit -->
<input type="text" class="time-picker" name="opening_time">
```

### 3. Django Form Fields

Felder mit "date" im Namen werden automatisch erkannt:

```python
# In forms.py
class VoucherForm(forms.Form):
    start_date = forms.DateField()      # Wird automatisch zu date-picker
    end_date = forms.DateField()        # Wird automatisch zu date-picker
    created_at = forms.DateTimeField()  # Manuell datetime-picker Klasse hinzufügen
```

## Konfiguration

### Standard-Einstellungen

- **Datumsformat**: `d.m.Y` (31.12.2023)
- **Datetime-Format**: `d.m.Y H:i` (31.12.2023 14:30)
- **Zeit-Format**: `H:i` (14:30)
- **Sprache**: Deutsch
- **24h-Format**: Ja
- **Eingabe erlaubt**: Ja

### Manuelle Initialisierung

```javascript
// Benutzerdefinierte Konfiguration
flatpickr('.my-date-field', {
    dateFormat: "Y-m-d",
    locale: "de",
    minDate: "today",
    maxDate: new Date().fp_incr(30) // 30 Tage in der Zukunft
});
```

## Themes

Zusätzliche Themes können hinzugefügt werden:

```html
<!-- Material Design Theme -->
<link rel="stylesheet" href="{% static 'lfs/css/flatpickr-material.css' %}">
```

## HTMX Kompatibilität

Flatpickr wird automatisch nach HTMX-Swaps re-initialisiert:

```javascript
// Automatisch nach htmx:afterSwap Event
document.addEventListener('htmx:afterSwap', function(event) {
    initializeFlatpickr(event.detail.target);
});
```

## Utility Funktionen

```javascript
// Datum aus Flatpickr-Feld holen
const date = getFlatpickrValue(document.querySelector('.date-picker'));

// Datum in Flatpickr-Feld setzen
setFlatpickrValue(document.querySelector('.date-picker'), new Date());
```

## Beispiel: Voucher Form

```django
<!-- voucher_form.html -->
{% load static crispy_forms_tags %}

<form method="post">
    {% csrf_token %}
    
    <div class="row">
        <div class="col-md-6">
            <label for="id_start_date">{% trans "Start Date" %}</label>
            <input type="text" 
                   class="form-control date-picker" 
                   name="start_date" 
                   id="id_start_date">
        </div>
        <div class="col-md-6">
            <label for="id_end_date">{% trans "End Date" %}</label>
            <input type="text" 
                   class="form-control date-picker" 
                   name="end_date" 
                   id="id_end_date">
        </div>
    </div>
    
    <button type="submit" class="btn btn-primary">
        {% trans "Save" %}
    </button>
</form>

<!-- Scripts -->
<script src="{% static 'lfs/js/flatpickr.min.js' %}"></script>
<script src="{% static 'lfs/js/flatpickr-de.js' %}"></script>
<script src="{% static 'lfs/js/management/flatpickr-init.js' %}"></script>
```

## Troubleshooting

### Doppelte Initialisierung verhindern

```javascript
if (!element._flatpickr) {
    flatpickr(element, options);
}
```

### Custom Event Handling

```javascript
flatpickr('.date-picker', {
    onChange: function(selectedDates, dateStr, instance) {
        console.log('Datum geändert:', dateStr);
    },
    onReady: function(selectedDates, dateStr, instance) {
        console.log('Flatpickr bereit');
    }
});
```

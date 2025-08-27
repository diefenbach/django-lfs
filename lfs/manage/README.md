# Technik: Tab-basierte Edit-Views in Django

## Motivation

- Ein komplexes Objekt (z. B. Produkt, Kategorie, StaticBlock) hat mehrere unterschiedliche Datenbereiche (Tabs: Stammdaten, Preise, SEO, Dateien, …).
- Jeder Tab soll separat gespeichert werden (POST verarbeitet nur ein Formular), damit Validierungsfehler eines Tabs die anderen nicht blockieren.
- Die UI zeigt alle Tabs im selben Shell-Template mit Navigation. Der Tab-Inhalt wird über `{% include %}` eingeblendet.

---

## Architektur

### 1. Shell-Template (Rahmen)

- Enthält die Tab-Navigation (`tabs`)
- Enthält einen Bereich `#tab-content`
- Basiert auf einer Variablen `active_tab`, die steuert, welches Partial eingebunden wird.

**Beispiel: `templates/products/product_edit.html`**

```django
<h1>Produkt bearbeiten: {{ product.name }}</h1>

<nav class="tabs">
  {% for key, url in tabs %}
    <a href="{{ url }}" class="{% if active_tab == key %}active{% endif %}">
      {{ key|title }}
    </a>
  {% endfor %}
</nav>

<div id="tab-content">
  {% if active_tab == "data" %}
    {% include "products/tabs/_data.html" %}
  {% elif active_tab == "seo" %}
    {% include "products/tabs/_seo.html" %}
  {% elif active_tab == "files" %}
    {% include "products/tabs/_files.html" %}
  {% endif %}
</div>
```

---

### 2. Partials (Tab-Inhalte)

Jeder Tab hat ein Partial-Template, das ein Formular rendert.  
Diese bekommen ihren Kontext direkt von der View.

**Beispiel: `products/tabs/_data.html`**

```django
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Daten speichern</button>
</form>
```

**Beispiel: `products/tabs/_seo.html`**

```django
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">SEO speichern</button>
</form>
```

---

### 3. Gemeinsames Mixin

Ein Mixin baut den gemeinsamen Kontext für alle Tabs: aktiver Tab, Navigation, Produktobjekt.

**Beispiel: `views_mixins.py`**

```python
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Product

class ProductTabMixin:
    template_name = "products/product_edit.html"
    tab_name = None  # wird in Subclass gesetzt: "data", "seo", ...

    def get_product(self):
        return get_object_or_404(Product, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = getattr(self, "object", None) or self.get_product()
        ctx["product"] = product
        ctx["active_tab"] = self.tab_name
        ctx["tabs"] = [
            ("data", reverse("products:edit_data", args=[product.pk])),
            ("seo",  reverse("products:edit_seo", args=[product.pk])),
            ("files", reverse("products:edit_files", args=[product.pk])),
        ]
        return ctx
```

---

### 4. Views pro Tab

#### Tab 1: Stammdaten (einfaches UpdateView)

```python
from django.views.generic import UpdateView
from django.urls import reverse
from .forms import ProductForm

class ProductDataView(ProductTabMixin, UpdateView):
    model = Product
    form_class = ProductForm
    tab_name = "data"

    def get_success_url(self):
        return reverse("products:edit_data", args=[self.object.pk])
```

#### Tab 2: SEO (OneToOne-Relation, UpdateView mit get_object)

```python
from .models import SEO
from .forms import SEOForm

class ProductSEOView(ProductTabMixin, UpdateView):
    model = SEO
    form_class = SEOForm
    tab_name = "seo"

    def get_object(self, queryset=None):
        product = self.get_product()
        seo, _ = SEO.objects.get_or_create(product=product)
        return seo

    def get_success_url(self):
        return reverse("products:edit_seo", args=[self.object.product.pk])
```

#### Tab 3: Dateien (Upload + Liste, daher FormView)

```python
from django.views.generic import FormView
from django.db import transaction
from .models import StaticBlockFile
from .forms import FileForm

class ProductFilesView(ProductTabMixin, FormView):
    form_class = FileForm
    tab_name = "files"

    def get_success_url(self):
        return reverse("products:edit_files", args=[self.kwargs["pk"]])

    def form_valid(self, form):
        block = self.get_product()
        with transaction.atomic():
            file = form.save(commit=False)
            file.block = block
            file.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["files"] = self.get_product().files.all()
        return ctx
```

---

### 5. URLs

**Beispiel: `urls.py`**

```python
from django.urls import path
from .views import ProductDataView, ProductSEOView, ProductFilesView

app_name = "products"

urlpatterns = [
    path("<int:pk>/edit/data/", ProductDataView.as_view(), name="edit_data"),
    path("<int:pk>/edit/seo/", ProductSEOView.as_view(), name="edit_seo"),
    path("<int:pk>/edit/files/", ProductFilesView.as_view(), name="edit_files"),
]
```

---

## Ablauf für den Benutzer

1. Klick auf „Daten“ → `/edit/data/`  
   → rendert Shell + _data.html
2. Klick auf „SEO“ → `/edit/seo/`  
   → rendert Shell + _seo.html
3. Klick auf „Dateien“ → `/edit/files/`  
   → rendert Shell + _files.html

- Immer gleiche Shell, nur `active_tab` wechselt.
- POST verarbeitet nur das Formular des aktiven Tabs.

---

## Vorteile der Technik

- Nur **eine zentrale View** für das gesamte Objekt
- Gute Erweiterbarkeit um weitere Tabs
- Tab-Wechsel löst einen vollen Request aus (kein JS notwendig)
- Flexibles Markup über `{% include %}`

---

## Optional

- Tabs auch als URLs definieren: `/edit/?tab=data`, `/edit/?tab=files`
- Formularvalidierung pro Tab
- Integration von Formsets oder zusätzlichen Kontextdaten pro Tab

---

## Hinweis

Wenn Tabs **komplexer werden** (z. B. viele abhängige Felder, dynamische Datei-Uploads etc.), kannst du später zu `htmx` oder echten `FormView`-Unterkomponenten wechseln.  
Der hier gezeigte Aufbau eignet sich gut als skalierbare Basis für späteren Ausbau.
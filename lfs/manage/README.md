# Technique: Tab-based Edit Views in Django

## Motivation

- A complex object (e.g. Product, Category, StaticBlock) has multiple different data areas (tabs: master data, prices, SEO, files, …).
- Each tab should be saved separately (POST processes only one form), so validation errors in one tab don't block the others.
- The UI shows all tabs in the same shell template with navigation. Tab content is included via `{% include %}`.

---

## Architecture

### 1. Shell Template (Framework)

- Contains tab navigation (`tabs`)
- Contains a `#tab-content` area
- Based on an `active_tab` variable that controls which partial is included.

**Example: `templates/products/product_edit.html`**

```django
<h1>Edit Product: {{ product.name }}</h1>

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

### 2. Partials (Tab Contents)

Each tab has a partial template that renders a form.  
These receive their context directly from the view.

**Example: `products/tabs/_data.html`**

```django
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Save Data</button>
</form>
```

**Example: `products/tabs/_seo.html`**

```django
<form method="post">
  {% csrf_token %}
  {{ form.as_p }}
  <button type="submit">Save SEO</button>
</form>
```

---

### 3. Shared Mixin

A mixin builds the common context for all tabs: active tab, navigation, product object.

**Example: `views_mixins.py`**

```python
from django.urls import reverse
from django.shortcuts import get_object_or_404
from .models import Product

class ProductTabMixin:
    template_name = "products/product_edit.html"
    tab_name = None  # set in subclass: "data", "seo", ...

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

### 4. Views per Tab

#### Tab 1: Master Data (simple UpdateView)

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

#### Tab 2: SEO (OneToOne Relation, UpdateView with get_object)

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

#### Tab 3: Files (Upload + List, therefore FormView)

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

**Example: `urls.py`**

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

## User Flow

1. Click on "Data" → `/edit/data/`  
   → renders Shell + _data.html
2. Click on "SEO" → `/edit/seo/`  
   → renders Shell + _seo.html
3. Click on "Files" → `/edit/files/`  
   → renders Shell + _files.html

- Always the same shell, only `active_tab` changes.
- POST processes only the form of the active tab.

---

## Advantages of this Technique

- Only **one central view** for the entire object
- Good extensibility for additional tabs
- Tab switching triggers a full request (no JS necessary)
- Flexible markup via `{% include %}`

---

## Optional

- Define tabs as URLs too: `/edit/?tab=data`, `/edit/?tab=files`
- Form validation per tab
- Integration of formsets or additional context data per tab

---

## Modal System

### Overview

The management interface uses a size-specific modal system to provide optimal user experience. Instead of resizing modals dynamically (which causes visual flicker), we use dedicated modal snippets for different content types.

### Modal Snippets

**Structure: `templates/manage/snippets/modals/`**

```
modals/
├── modal-sm.html     # Small modals (confirmations, alerts)
├── modal-lg.html     # Large modals (forms, data entry)
└── modal-xl.html     # Extra large modals (previews, complex content)
```

**Example: `modal-lg.html`**

```django
{% load i18n %}
<div class="modal" id="lfs-modal-lg" tabindex="-1" aria-hidden="true">
    <div class="modal-dialog modal-lg">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title" id="modal-title-lg"></h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="{% trans 'Close' %}"></button>
            </div>
            <div class="modal-body" id="modal-body-lg"></div>
        </div>
    </div>
</div>
```

### JavaScript Integration

**File: `static/lfs/js/management/shared.js`**

```javascript
document.addEventListener('htmx:afterSwap', evt => {
    const targetId = evt.detail.target?.id;
    let modalEl;
    
    // Target-based modal selection
    if (targetId === "modal-body-sm") {
        modalEl = document.getElementById('lfs-modal-sm');
    } else if (targetId === "modal-body-lg") {
        modalEl = document.getElementById('lfs-modal-lg');
    } else if (targetId === "modal-body-xl") {
        modalEl = document.getElementById('lfs-modal-xl');
    }
    
    if (modalEl) {
        let modalInstance = bootstrap.Modal.getInstance(modalEl);
        if (!modalInstance) {
            modalInstance = new bootstrap.Modal(modalEl);
        }
        if (!modalEl.classList.contains('show')) {
            modalInstance.show();
        }
    }
});
```

### Usage in Templates

**Button targeting specific modal size:**

```django
<!-- For forms/data entry -->
<button hx-get="{% url 'add_static_block' %}" 
        hx-target="#modal-body-lg"
        hx-swap="innerHTML">
    Add Static Block
</button>

<!-- For previews/large content -->
<button hx-get="{% url 'preview_static_block' pk %}" 
        hx-target="#modal-body-xl"
        hx-swap="innerHTML">
    Preview
</button>
```

**Including modals in templates:**

```django
{% extends "manage/base.html" %}

{% block content %}
    <!-- Your page content -->
    
    <!-- Include required modal sizes -->
    {% include 'manage/snippets/modals/modal-lg.html' %}
    {% include 'manage/snippets/modals/modal-xl.html' %}
{% endblock %}
```

**Modal content templates:**

```django
<!-- add_static_block.html -->
{% load i18n crispy_forms_tags %}

<h5 id="modal-title-lg" class="modal-title" hx-swap-oob="true">
    {% trans 'Add Static Block' %}
</h5>
<form method="post" hx-post="{% url 'add_static_block' %}" hx-target="#modal-body-lg">
    {% csrf_token %}
    {{ form|crispy }}
    <div class="mt-3">
        <button type="submit" class="btn btn-primary">{% trans 'Save' %}</button>
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">
            {% trans 'Cancel' %}
        </button>
    </div>
</form>
```

### Advantages

**1. No Visual Flicker**
- Fixed modal sizes prevent resize animations
- Better user experience with instant, stable modals

**2. Semantic Sizing**
- Each modal size has a clear purpose:
  - `modal-sm`: Quick confirmations, alerts
  - `modal-lg`: Standard forms, data entry
  - `modal-xl`: Content-heavy previews, complex displays

**3. Performance**
- No JavaScript modal resizing overhead
- Modals initialize with final dimensions immediately

**4. Maintainability**
- Reusable modal snippets across templates
- Centralized modal logic in `shared.js`
- Clear separation of concerns

**5. Extensibility**
- Easy to add new modal sizes
- Simple button-to-modal mapping via `hx-target`
- Consistent pattern across the application

### Implementation Notes

- Each modal has unique IDs (`lfs-modal-sm`, `lfs-modal-lg`, `lfs-modal-xl`)
- Modal titles use size-specific IDs (`modal-title-sm`, `modal-title-lg`, `modal-title-xl`)
- HTMX `hx-swap-oob="true"` updates modal titles dynamically
- JavaScript automatically detects target and shows appropriate modal

This approach scales well and provides a consistent, flicker-free modal experience throughout the management interface.

---

## Note

When tabs **become more complex** (e.g. many dependent fields, dynamic file uploads etc.), you can later switch to `htmx` or real `FormView` subcomponents.  
The structure shown here works well as a scalable foundation for future expansion.
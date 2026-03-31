# Product Management Forms

## Manual Form Rendering Decision

Product management forms are rendered manually field by field to display parent product values alongside variant input fields. This approach enables clear visualization of inherited vs. overridden values in product variants.

### Rationale
- Crispy Forms helper proved insufficiently flexible for this specific UI requirement
- Manual rendering provides better control over the variant/parent value display layout
- Future evaluation of alternative form rendering libraries may be considered

### Implementation Details
- Forms use Bootstrap grid system (col-md-8 for inputs, col-md-4 for parent values)
- Parent values are displayed using `form-control-plaintext` class
- Variant-specific checkboxes control field inheritance behavior

# TODOS

## Code Architecture & UI Consistency

**Prerequisites**: Complete implementation of all management views to identify common patterns and requirements.

**Refactoring Tasks**:
- **Pagination Standardization**: Implement consistent pagination UI/UX across all list views with unified parameter handling
- **Checkbox Management**: Standardize bulk selection interfaces and state management across admin views
- **Drag-and-Drop (DnD) Implementation**: Create unified DnD functionality for list reordering and item positioning

## Add Product

**Issue**: When the add product form validation fails (e.g., duplicate slug exists), the modal closes and validation errors are displayed outside the modal context.

**Expected Behavior**: Validation errors should remain visible within the modal.

**Proposed Solution**: Implement HTMX handling to keep the modal open and display form errors within the modal during validation failures.
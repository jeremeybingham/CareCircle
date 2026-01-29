### Standardized Food Data Fields for Reporting
 
**Goal**: Coordinate field types and data storage across forms for meals so that identical data (food intake, mood, activities, etc.) is captured consistently, enabling future analytics and reporting.
 
**Why This Matters**:
- Currently, different forms may capture similar data in different formats
- Example: "dinner" in overnight form vs "lunch" in schoolday form use similar portion options but may have inconsistent field names or choices
- Standardization enables: trend analysis, pattern recognition, IEP progress reports, health tracking
 
**Areas Needing Standardization**:
 
#### Food/Meal Intake
- **Current**: `PORTION_CHOICES` in `constants.py` (All of it, Most of it, Half, Some, None)
- **Ensure**: All meal-related fields across all forms use identical choices: USE THESE: ["None", "Some", "Most", "All"] + not specified where applicable
- **Ensure**: the above portion choices should always be followed by an optional text field for "Type of Food" 
- **Field naming**: Use consistent names like `breakfast_portion`, `lunch_portion`, `dinner_portion`, `snack_portion`
- **Use Radio Buttons for Input**: Since there's always exactly 4 same choices, dropdown on mobile is clunky, use radio instead
 

**Implementation Steps**:
- [x] Audit all existing forms for overlapping data fields
- [x] Document current field names and choice values
- [x] Design standardized field schema for each data category
- [x] Update `timeline/forms/constants.py` with all standardized choices
- [x] Create standardized form field mixins or base classes
- [x] Migrate existing forms to use standardized fields
- [x] Update display templates to handle standardized data
- [ ] Consider data migration for existing entries (optional, complex)
- [x] Document field standards for future form development
 
**Files to Create/Modify**:
- `timeline/forms/constants.py` - Expand with all standardized choices
- `timeline/forms/mixins.py` - NEW (reusable form field groups)
- `timeline/forms/*.py` - Update all forms to use standardized fields
- `docs/DATA_STANDARDS.md` - NEW (document field conventions)
 
**Example Standardized Constants**:
```python
# timeline/forms/constants.py
 
# Food/Meal Intake constants for radio with not specified option

PORTION_CHOICES= [
    ('', 'Not specified'),
    ('None', 'None'),
    ('Some', 'Some'),
    ('Most', 'Most'),
    ('All', 'All'),
]
```
 
---

**Implementation Complete**:

The three inconsistent `PORTION_CHOICES_*` constants have been replaced with a single
standardized `PORTION_CHOICES` in `constants.py`:

```python
PORTION_CHOICES = [
    ('', 'Not specified'),
    ('None', 'None'),
    ('Some', 'Some'),
    ('Most', 'Most'),
    ('All', 'All'),
]
```

A `MealFieldMixin` was created in `mixins.py` that dynamically injects standardized
meal fields into any form. Each meal gets:
- `{meal}_portion` — RadioSelect using `PORTION_CHOICES`
- `{meal}_food` — Optional text field for "Type of Food"

**Forms updated**:

| Form | `meal_fields` | Custom Labels |
|------|---------------|---------------|
| OvernightForm | `['dinner', 'breakfast']` | `dinner` → "Dinner Last Night" |
| SchoolDayForm | `['snack', 'lunch']` | `snack` → "Snacks", `lunch` → "Lunch from Home" |
| PickupForm | `['lunch']` | `lunch` → "Lunch/Snack" |

**Field name mapping (old → new)**:
- `dinner` → `dinner_portion` + `dinner_food`
- `breakfast` → `breakfast_portion` + `breakfast_food`
- `snacks` → `snack_portion` + `snack_food`
- `lunch_from_home` → `lunch_portion` + `lunch_food`
- `had_lunch` (boolean) → removed (replaced by "Not specified" option)
- `lunch_notes` → `lunch_food` (type of food text field)

**Templates updated**: `entry_overnight.html`, `entry_schoolday.html`, `entry_pickup.html`
now reference the new `*_portion` and `*_food` field names and display food type inline
with the portion value (e.g., "Most — pasta and chicken").

**Note**: Existing entries stored with old field names will not display their food data
in the updated templates. A data migration could be written to rename the JSON keys
in existing entries if needed.


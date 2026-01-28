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
- [ ] Audit all existing forms for overlapping data fields
- [ ] Document current field names and choice values
- [ ] Design standardized field schema for each data category
- [ ] Update `timeline/forms/constants.py` with all standardized choices
- [ ] Create standardized form field mixins or base classes
- [ ] Migrate existing forms to use standardized fields
- [ ] Update display templates to handle standardized data
- [ ] Consider data migration for existing entries (optional, complex)
- [ ] Document field standards for future form development
 
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
Currently: 

```python
# =============================================================================
# Portion/Consumption Choices TODO: FIX this
# =============================================================================

# Full portion choices with blank option (for dropdown/select fields)
PORTION_CHOICES_WITH_BLANK = [
    ('', '-- Select --'),
    ('None', 'None'),
    ('Some', 'Some'),
    ('Most', 'Most'),
    ('All', 'All'),
]

# Simple portion choices without "Most" (for radio buttons)
PORTION_CHOICES_SIMPLE = [
    ('None', 'None'),
    ('Some', 'Some'),
    ('All', 'All'),
]

# Portion choices with "Not specified" blank (for optional radio buttons)
PORTION_CHOICES_RADIO = [
    ('', 'Not specified'),
    ('None', 'None'),
    ('Some', 'Some'),
    ('All', 'All'),
]
```


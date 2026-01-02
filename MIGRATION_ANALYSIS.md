# EasyCrystallography Migration Analysis - Phase 1

## Executive Summary

This document contains the impact analysis for migrating EasyCrystallography
from the old corelib architecture (`ObjBase`, `CollectionBase`) to the new
architecture (`ModelBase`, `ModelCollection`, `CalculatorFactoryBase`).

**Note:** EasyCrystallography is a simpler case than EasyReflectometryLib as it
does not have its own calculator implementations. The `interface` parameter
exists on objects but is passed through for downstream applications (like
EasyDiffraction) to use.

---

## 1. Inheritance Tree Analysis

### Current Architecture (Before Migration)

```
ObjBase (corelib - deprecated)
├── Lattice (Components/Lattice.py)
│   └── PeriodicLattice
├── Site (Components/Site.py)
│   └── PeriodicSite
├── AdpBase (Components/AtomicDisplacement.py)
│   ├── Anisotropic
│   ├── Isotropic
│   ├── AnisotropicBij
│   └── IsotropicB
├── AtomicDisplacement (Components/AtomicDisplacement.py)
├── SpaceGroup (Components/SpaceGroup.py)
├── MSPBase (Components/Susceptibility.py)
│   ├── Cani
│   └── Ciso
├── MagneticSusceptibility (Components/Susceptibility.py)
└── Phase (Structures/Phase.py)

CollectionBase (corelib - deprecated)
├── Atoms (Components/Site.py)
│   └── PeriodicAtoms
└── Phases (Structures/Phase.py)

Other Classes (no migration needed):
├── Specie (extends DescriptorStr)
├── Twin (plain Python class)
├── SymmOp (extends SerializerComponent)
├── SymmetryGroup/PointGroup/SpaceGroup (Symmetry groups - abstract/metaclass)
└── IO classes (template, parser, star classes)
```

### Target Architecture (After Migration)

```
ModelBase (corelib - new)
├── BaseCore (new compatibility layer)
│   ├── Lattice
│   │   └── PeriodicLattice
│   ├── Site
│   │   └── PeriodicSite
│   ├── AdpBase
│   │   ├── Anisotropic
│   │   ├── Isotropic
│   │   ├── AnisotropicBij
│   │   └── IsotropicB
│   ├── AtomicDisplacement
│   ├── SpaceGroup
│   ├── MSPBase
│   │   ├── Cani
│   │   └── Ciso
│   ├── MagneticSusceptibility
│   └── Phase

ModelCollection (corelib - new)
├── BaseCollection (new compatibility layer)
│   ├── Atoms
│   │   └── PeriodicAtoms
│   └── Phases
```

---

## 2. Calculator/Interface Analysis

### Current Pattern

Unlike EasyReflectometryLib, EasyCrystallography does **not** have its own
calculator implementations. The `interface` parameter is:

1. **Accepted** by constructors on most classes (Lattice, Site, Phase, etc.)
2. **Stored** on the object as `self.interface`
3. **Used minimally** - only `Site.add_adp()` calls
   `self.interface.generate_bindings(self)` (line 205)
4. **Passed through** to downstream applications like EasyDiffraction

### Migration Approach

Since there's no CalculatorFactory in EasyCrystallography:

1. **No PR2 equivalent needed** - No calculator refactoring required
2. **Interface parameter** should be made optional with `None` default
3. **generate_bindings calls** in `Site.add_adp()` should be made conditional or
   removed
4. The `interface` can remain as a passthrough for downstream compatibility

---

## 3. Breaking Changes Inventory

| Component             | Old API                     | New API                                         | Breaking Change       | Mitigation                     |
| --------------------- | --------------------------- | ----------------------------------------------- | --------------------- | ------------------------------ |
| All `ObjBase` classes | Inherits `ObjBase`          | Inherits `ModelBase` via `BaseCore`             | Constructor signature | Add compatibility `__init__`   |
| `name` property       | Direct from `ObjBase`       | Maps to `display_name`                          | Property access       | Property wrapper in `BaseCore` |
| `interface` property  | Direct property             | Keep for downstream compat                      | None                  | Keep as optional parameter     |
| `Atoms`, `Phases`     | Inherits `CollectionBase`   | Inherits `ModelCollection` via `BaseCollection` | Constructor signature | Add compatibility `__init__`   |
| Serialization         | `as_dict()` custom patterns | `to_dict()` from SerializerBase                 | Method names          | Alias methods                  |
| Object creation       | `name` parameter            | `unique_name` + `display_name`                  | Parameter naming      | Map in constructor             |
| Parameter access      | `self.kwarg_name` magic     | Explicit or via `_kwargs`                       | Attribute access      | Custom `__getattr__`           |

---

## 4. Files Affected by Migration

### Core Files to Modify (PR1: Base Class Replacements)

| File                               | Current Base                | Target Base                  | Changes Required                                      |
| ---------------------------------- | --------------------------- | ---------------------------- | ----------------------------------------------------- |
| `Components/Lattice.py`            | `ObjBase`                   | `BaseCore`                   | Update import, change base class                      |
| `Components/Site.py`               | `ObjBase`, `CollectionBase` | `BaseCore`, `BaseCollection` | Update imports, change base classes, handle interface |
| `Components/AtomicDisplacement.py` | `ObjBase`                   | `BaseCore`                   | Update import, change base class                      |
| `Components/SpaceGroup.py`         | `ObjBase`                   | `BaseCore`                   | Update import, change base class                      |
| `Components/Susceptibility.py`     | `ObjBase`                   | `BaseCore`                   | Update import, change base class                      |
| `Structures/Phase.py`              | `ObjBase`, `CollectionBase` | `BaseCore`, `BaseCollection` | Update imports, change base classes                   |

### New Files to Create

| File                                              | Purpose                                                     |
| ------------------------------------------------- | ----------------------------------------------------------- |
| `Components/base_core.py`                         | Compatibility layer between `ModelBase` and legacy patterns |
| `Components/base_collection.py` (or in same file) | Compatibility layer for collections                         |

### Files with Minor Changes

| File                     | Changes Required                  |
| ------------------------ | --------------------------------- |
| `Components/__init__.py` | Export new base classes if needed |
| `Structures/__init__.py` | Export new base classes if needed |

---

## 5. Class-by-Class Migration Details

### 5.1 Lattice (Components/Lattice.py)

**Current:**

```python
from easyscience import ObjBase as BaseObj

class Lattice(BaseObj):
    def __init__(self, ..., interface: Optional[iF] = None, ...):
        super().__init__('lattice', length_a=..., ...)
        self.interface = interface
```

**Target:**

```python
from easycrystallography.Components.base_core import BaseCore

class Lattice(BaseCore):
    def __init__(self, ..., interface=None, ...):
        super().__init__('lattice', interface=interface,
                         length_a=..., ...)
```

### 5.2 Site (Components/Site.py)

**Current:**

```python
from easyscience import ObjBase as BaseObj
from easyscience.base_classes import CollectionBase

class Site(BaseObj): ...
class Atoms(CollectionBase): ...
```

**Target:**

```python
from easycrystallography.Components.base_core import BaseCore
from easycrystallography.Components.base_collection import BaseCollection

class Site(BaseCore): ...
class Atoms(BaseCollection): ...
```

**Special handling:**

- `Site.add_adp()` has `self.interface.generate_bindings(self)` - make
  conditional

### 5.3 AtomicDisplacement (Components/AtomicDisplacement.py)

**Classes to migrate:** `AdpBase`, `Anisotropic`, `Isotropic`, `AnisotropicBij`,
`IsotropicB`, `AtomicDisplacement`

### 5.4 SpaceGroup (Components/SpaceGroup.py)

**Current:**

```python
from easyscience import ObjBase as BaseObj

class SpaceGroup(BaseObj):
    def __init__(self, ..., interface: Optional[iF] = None):
        super(SpaceGroup, self).__init__('space_group', ...)
        self.interface = interface
```

### 5.5 Susceptibility (Components/Susceptibility.py)

**Classes to migrate:** `MSPBase`, `Cani`, `Ciso`, `MagneticSusceptibility`

### 5.6 Phase (Structures/Phase.py)

**Current:**

```python
from easyscience import ObjBase as BaseObj
from easyscience.base_classes import CollectionBase

class Phase(BaseObj): ...
class Phases(CollectionBase): ...
```

---

## 6. Pull Request Strategy

### PR1: Base Class Replacements

| Task                                                            | Files Modified                       |
| --------------------------------------------------------------- | ------------------------------------ |
| Create `BaseCore` class (based on EasyReflectometryLib pattern) | New: `Components/base_core.py`       |
| Create `BaseCollection` class                                   | New: `Components/base_collection.py` |
| Migrate `Lattice`, `PeriodicLattice`                            | `Components/Lattice.py`              |
| Migrate `Site`, `PeriodicSite`, `Atoms`, `PeriodicAtoms`        | `Components/Site.py`                 |
| Migrate `AdpBase` and subclasses, `AtomicDisplacement`          | `Components/AtomicDisplacement.py`   |
| Migrate `SpaceGroup`                                            | `Components/SpaceGroup.py`           |
| Migrate `MSPBase`, `Cani`, `Ciso`, `MagneticSusceptibility`     | `Components/Susceptibility.py`       |
| Migrate `Phase`, `Phases`                                       | `Structures/Phase.py`                |
| Update imports and exports                                      | `__init__.py` files                  |
| Fix tests                                                       | `tests/unit_tests/`                  |

### PR2: Calculator Refactor

**Not applicable** - EasyCrystallography does not have its own calculators.

### PR3: Interface Removal/Simplification

| Task                                                 | Files Modified       |
| ---------------------------------------------------- | -------------------- |
| Make `interface` parameter optional (default `None`) | All migrated files   |
| Make `generate_bindings` a no-op or conditional      | `Components/Site.py` |
| Document interface as passthrough for downstream use | Docstrings           |

---

## 7. Migration Strategy Assessment

| Aspect                 | Assessment                              | Risk Level | Notes                                   |
| ---------------------- | --------------------------------------- | ---------- | --------------------------------------- |
| Backward Compatibility | Should be maintained                    | Medium     | Library used by EasyDiffraction         |
| Class Hierarchy        | Moderate complexity                     | Low        | Fewer classes than EasyReflectometryLib |
| Calculator Refactor    | Not needed                              | None       | No calculators in this package          |
| Interface Pattern      | Passthrough only                        | Low        | Simplify, don't remove                  |
| Test Coverage          | Limited (5 test files)                  | Medium     | May need to add tests                   |
| Serialization          | Custom `as_dict` patterns               | Medium     | Follow EasyReflectometryLib pattern     |
| Parameter Dependencies | Used in `PeriodicLattice.enforce_sym()` | Low        | Should work with new architecture       |

---

## 8. Dependencies and Impact

### Upstream Dependencies

- `easyscience` (corelib) - Must have `ModelBase`, `ModelCollection` available

### Downstream Dependencies

- **EasyDiffraction** - Primary consumer of EasyCrystallography
  - Uses `Phase`, `Phases`, `Lattice`, `Site`, `Atoms`, `SpaceGroup`
  - Provides its own calculator/interface that uses these objects
  - Migration should maintain interface compatibility

---

## 9. Implementation Checklist

### Phase 1: Preparation

- [ ] Verify corelib has required classes (`ModelBase`, `ModelCollection`)
- [ ] Review EasyReflectometryLib implementation for patterns
- [ ] Set up test environment

### Phase 2: Core Migration (PR1)

- [ ] Create `BaseCore` compatibility class
- [ ] Create `BaseCollection` compatibility class
- [ ] Migrate `Lattice.py` classes
- [ ] Migrate `Site.py` classes
- [ ] Migrate `AtomicDisplacement.py` classes
- [ ] Migrate `SpaceGroup.py`
- [ ] Migrate `Susceptibility.py` classes
- [ ] Migrate `Phase.py` classes
- [ ] Update all `__init__.py` exports
- [ ] Fix all tests
- [ ] Run full test suite

### Phase 3: Interface Simplification (PR3)

- [ ] Make interface optional on all classes
- [ ] Make `generate_bindings` conditional/no-op
- [ ] Update documentation
- [ ] Verify downstream compatibility

---

## 10. Test Requirements

### Existing Tests to Update

- `tests/unit_tests/components/test_Atoms.py`
- `tests/unit_tests/components/test_Lattice.py`
- `tests/unit_tests/components/test_Site.py`
- `tests/unit_tests/components/test_SpaceGroup.py`
- `tests/unit_tests/io/test_star.py`

### New Tests to Add

- Serialization round-trip tests (`as_dict` → `from_dict`)
- Copy tests (`__copy__`, `__deepcopy__`)
- Parameter dependency tests (for `PeriodicLattice`)
- Collection manipulation tests

---

## 11. Notes and Considerations

### Key Differences from EasyReflectometryLib

1. **No calculators** - Simpler migration, no PR2 equivalent
2. **Interface is passthrough** - Keep for downstream compatibility
3. **Fewer tests** - May need to add tests during migration
4. **Used by EasyDiffraction** - Must maintain API compatibility

### Potential Issues

1. **PeriodicLattice symmetry constraints** - Uses `make_dependent_on()` for
   parameter dependencies
2. **SpaceGroup complexity** - Complex class with many properties and class
   methods
3. **Dynamic property addition** - `AtomicDisplacement` and
   `MagneticSusceptibility` use `addProp`/`removeProp`

### Implementation Notes

1. **`_get_symops_value` function in SpaceGroup.py** - Added to fix a line
   length linting error. The original code was a single-line lambda that
   exceeded the project's 127-character limit:

   ```python
   # Before (141 characters - too long)
   _D_REDIRECT['value'] = lambda obj: ';'.join([r.as_xyz_string() for r in (obj.value.tolist() if hasattr(obj.value, 'tolist') else obj.value)])

   # After (extracted to named function)
   def _get_symops_value(obj):
       ops = obj.value.tolist() if hasattr(obj.value, 'tolist') else obj.value
       return ';'.join([r.as_xyz_string() for r in ops])
   _D_REDIRECT['value'] = _get_symops_value
   ```

### Corelib Changes Required

The same change made for EasyReflectometryLib should apply:

**File:** `corelib/src/easyscience/base_classes/collection_base.py`

```python
# Before
if not isinstance(item, (BasedBase, DescriptorBase)):
    raise TypeError(...)

# After
if not isinstance(item, (BasedBase, DescriptorBase, NewBase)):
    raise TypeError(...)
```

This allows `ModelCollection` to accept objects that inherit from `ModelBase`.

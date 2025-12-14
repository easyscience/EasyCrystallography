# SPDX-FileCopyrightText: 2024 EasyCrystallography contributors
# SPDX-License-Identifier: BSD-3-Clause
# © 2022-2024 Contributors to the EasyCrystallography project <https://github.com/EasyScience/EasyCrystallography>

from __future__ import annotations

from typing import TYPE_CHECKING
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from easyscience import global_object
from easyscience.base_classes import ModelBase
from easyscience.io.serializer_base import SerializerBase
from easyscience.variable import Parameter
from easyscience.variable.descriptor_base import DescriptorBase

if TYPE_CHECKING:
    from easyscience.fitting.calculators import InterfaceFactoryTemplate


class BaseCore(ModelBase):
    """Base class for all EasyCrystallography model objects.

    This class bridges the new ModelBase API with the legacy 'name' patterns
    used throughout EasyCrystallography. The 'name' property maps to 'display_name'
    in the new architecture.

    Interface Pattern
    -----------------
    The 'interface' parameter is a **passthrough for downstream applications**
    (e.g., EasyDiffraction) and is not actively used within EasyCrystallography itself.

    EasyCrystallography does not have its own calculator implementations. The interface
    allows downstream applications to:

    - Inject their own calculator/interface that works with these crystallography objects
    - Call `generate_bindings()` when objects are modified to sync with their calculators
    - Access the interface via the `interface` property on any model object

    When `interface` is `None` (the default), all binding-related methods are no-ops.

    Example usage in downstream applications::

        # In EasyDiffraction or similar
        phase = Phase(...)
        phase.interface = my_diffraction_calculator
        phase.generate_bindings()  # Syncs with calculator
    """

    def __init__(
        self,
        name: str,
        interface: Optional[InterfaceFactoryTemplate] = None,
        unique_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the base core object.

        :param name: Display name for the object
        :param interface: Optional interface for downstream calculator bindings.
            This is a passthrough parameter - EasyCrystallography does not use it
            internally, but downstream applications (like EasyDiffraction) can set
            their own calculator interface here.
        :param unique_name: Optional unique identifier
        :param kwargs: Additional keyword arguments (parameters, descriptors, sub-objects)
        """
        if unique_name is None:
            unique_name = global_object.generate_unique_name(self.__class__.__name__)
        super().__init__(unique_name=unique_name, display_name=name)

        # Store kwargs for parameter access (compatibility with ObjBase pattern)
        self._kwargs = kwargs
        for key, value in kwargs.items():
            # Register components with the global object map
            if hasattr(value, 'unique_name'):
                self._global_object.map.add_edge(self, value)
                self._global_object.map.reset_type(value, 'created_internal')

        # Interface is kept for downstream compatibility
        self._interface = interface

    def __getattr__(self, name: str):
        """Forward attribute access to _kwargs for ObjBase compatibility."""
        # Check if the name exists in _kwargs (handles both regular and underscore-prefixed kwargs)
        if '_kwargs' in self.__dict__ and name in self._kwargs:
            return self._kwargs[name]
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

    def __setattr__(self, name: str, value) -> None:
        """Handle attribute setting for ObjBase compatibility."""
        # During initialization, use normal setting
        if '_kwargs' not in self.__dict__:
            super().__setattr__(name, value)
            return
        # If name is in _kwargs, update the value (for Parameters, set .value)
        if name in self._kwargs:
            existing = self._kwargs[name]
            if isinstance(existing, DescriptorBase) and not isinstance(value, DescriptorBase):
                existing.value = value
            else:
                # Replace the component
                if hasattr(existing, 'unique_name'):
                    self._global_object.map.prune_vertex_from_edge(self, existing)
                self._kwargs[name] = value
                if hasattr(value, 'unique_name'):
                    self._global_object.map.add_edge(self, value)
                    self._global_object.map.reset_type(value, 'created_internal')
        else:
            super().__setattr__(name, value)

    @property
    def name(self) -> str:
        """Get the name of the object (maps to display_name)."""
        return self.display_name

    @name.setter
    def name(self, new_name: str) -> None:
        """Set the name of the object."""
        self.display_name = new_name

    @property
    def interface(self) -> Optional[InterfaceFactoryTemplate]:
        """Get the current interface of the object.

        The interface is a passthrough for downstream applications (e.g., EasyDiffraction).
        EasyCrystallography does not use this internally.

        :return: The current interface, or None if not set.
        """
        return self._interface

    @interface.setter
    def interface(self, new_interface: Optional[InterfaceFactoryTemplate]) -> None:
        """Set the interface for downstream calculator bindings.

        :param new_interface: The calculator interface from a downstream application,
            or None to clear the interface.
        """
        self._interface = new_interface

    def generate_bindings(self) -> None:
        """Generate or re-generate bindings to an interface.

        This method is a passthrough for downstream applications. When called:

        - If interface is None: This is a no-op
        - If interface is set: Calls interface.generate_bindings(self) to sync
          the object state with the downstream calculator

        Downstream applications (like EasyDiffraction) should call this after
        modifying objects to ensure their calculators stay synchronized.
        """
        if self._interface is not None and hasattr(self._interface, 'generate_bindings'):
            self._interface.generate_bindings(self)

    def _add_component(self, key: str, component) -> None:
        """Dynamically add a component to the class."""
        self._kwargs[key] = component
        self._global_object.map.add_edge(self, component)
        self._global_object.map.reset_type(component, 'created_internal')

    def _get_linkable_attributes(self) -> List[DescriptorBase]:
        """Get all objects which can be linked against as a list.

        :return: List of `Descriptor`/`Parameter` objects.
        """
        item_list = []
        for key, item in self._kwargs.items():
            if hasattr(item, '_get_linkable_attributes'):
                item_list = [*item_list, *item._get_linkable_attributes()]
            elif isinstance(item, DescriptorBase):
                item_list.append(item)
        return item_list

    def get_parameters(self) -> List[Parameter]:
        """Get all parameter objects as a list.

        :return: List of `Parameter` objects.
        """
        par_list = []
        for key, item in self._kwargs.items():
            if hasattr(item, 'get_parameters'):
                par_list = [*par_list, *item.get_parameters()]
            elif isinstance(item, Parameter):
                par_list.append(item)
        return par_list

    def get_fit_parameters(self) -> List[Parameter]:
        """Get all objects which can be fitted (and are not fixed) as a list.

        :return: List of `Parameter` objects which can be used in fitting.
        """
        fit_list = []
        for key, item in self._kwargs.items():
            if hasattr(item, 'get_fit_parameters'):
                fit_list = [*fit_list, *item.get_fit_parameters()]
            elif isinstance(item, Parameter):
                if item.independent and not item.fixed:
                    fit_list.append(item)
        return fit_list

    def __repr__(self) -> str:
        """String representation of the object."""
        return f'{self.__class__.__name__} `{self.name}`'

    def as_dict(self, skip: Optional[List[str]] = None) -> dict:
        """Produces a cleaned dict using a custom as_dict method.
        The resulting dict matches the parameters in __init__.

        :param skip: List of keys to skip, defaults to `None`.
        :return: Dictionary representation of the object.
        """
        if skip is None:
            skip = []

        # Always skip unique_name for nested Parameters to avoid collisions during from_dict
        param_skip = list(skip) + ['unique_name'] if 'unique_name' not in skip else list(skip)

        result = {
            '@module': self.__class__.__module__,
            '@class': self.__class__.__name__,
            '@version': None,
        }

        # Add name if not default
        if 'name' not in skip:
            result['name'] = self.name

        # Add unique_name if not default
        if 'unique_name' not in skip and not self._default_unique_name:
            result['unique_name'] = self.unique_name

        # Check for _REDIRECT class attribute (used by SpaceGroup and similar classes)
        redirect = getattr(self.__class__, '_REDIRECT', {})

        # Serialize kwargs - use param_skip for nested objects
        for key, value in self._kwargs.items():
            # Strip leading underscore from key for serialization
            key_name = key.lstrip('_') if key.startswith('_') else key
            if key_name in skip or key in skip:
                continue

            # Check if this key has a redirect function
            if key_name in redirect:
                result[key_name] = redirect[key_name](self)
            elif hasattr(value, 'as_dict'):
                result[key_name] = value.as_dict(skip=param_skip)
            elif hasattr(value, 'to_dict'):
                result[key_name] = value.to_dict(skip=param_skip)
            else:
                result[key_name] = value

        # Add interface for backwards compatibility (always None in EasyCrystallography)
        if 'interface' not in skip:
            result['interface'] = None

        return result

    def to_dict(self, skip: Optional[List[str]] = None) -> dict:
        """Convert to dictionary for serialization (alias for as_dict).

        This overrides NewBase.to_dict to use our custom serialization.

        :param skip: List of keys to skip, defaults to `None`.
        :return: Dictionary representation of the object.
        """
        return self.as_dict(skip=skip)

    @classmethod
    def from_dict(cls, obj_dict: Dict[str, Any]) -> 'BaseCore':
        """
        Re-create an object from a dictionary.

        :param obj_dict: Dictionary containing the serialized contents.
        :return: Reformed object.
        """
        if not SerializerBase._is_serialized_easyscience_object(obj_dict):
            raise ValueError('Input must be a dictionary representing an EasyScience object.')

        # Deserialize all values
        kwargs = {}
        for key, value in obj_dict.items():
            if key.startswith('@'):
                continue
            if isinstance(value, dict) and SerializerBase._is_serialized_easyscience_object(value):
                kwargs[key] = SerializerBase._deserialize_value(value)
            else:
                kwargs[key] = value

        # Create instance
        return cls(**kwargs)

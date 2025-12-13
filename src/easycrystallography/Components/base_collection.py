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
from easyscience.base_classes import ModelCollection as EasyModelCollection
from easyscience.io.serializer_base import SerializerBase
from easyscience.variable import Parameter

if TYPE_CHECKING:
    from easyscience.fitting.calculators import InterfaceFactoryTemplate


class BaseCollection(EasyModelCollection):
    """Base class for all EasyCrystallography collection objects.

    This class bridges the new ModelCollection API with the legacy patterns
    used throughout EasyCrystallography.
    """

    def __init__(
        self,
        name: str,
        *args,
        interface: Optional[InterfaceFactoryTemplate] = None,
        unique_name: Optional[str] = None,
        **kwargs,
    ):
        """
        Initialize the base collection.

        :param name: Name for the collection
        :param args: Items to add to the collection
        :param interface: Optional interface for downstream calculator bindings
        :param unique_name: Optional unique identifier
        :param kwargs: Additional keyword arguments
        """
        if unique_name is None:
            unique_name = global_object.generate_unique_name(self.__class__.__name__)

        # Handle legacy pattern where items are passed as kwargs with numeric string keys
        # e.g., {'0': item1, '1': item2} - convert these to positional args
        numeric_items = []
        remaining_kwargs = {}
        for key, value in kwargs.items():
            if key.isdigit():
                numeric_items.append((int(key), value))
            else:
                remaining_kwargs[key] = value

        # Sort by numeric key and extract values
        if numeric_items:
            numeric_items.sort(key=lambda x: x[0])
            extra_items = [item[1] for item in numeric_items]
            args = args + tuple(extra_items)

        super().__init__(name, *args, interface=interface, unique_name=unique_name)

        # Needed to ensure an empty list is created when saving and instantiating the object as_dict -> from_dict
        # Else collisions might occur in global_object.map
        self.populate_if_none = remaining_kwargs.get('populate_if_none', False)

    def get_parameters(self) -> List[Parameter]:
        """Get all parameter objects as a list.

        This is an alias for get_all_parameters to maintain backwards compatibility.

        :return: List of `Parameter` objects.
        """
        par_list = []
        for item in self:
            if hasattr(item, 'get_parameters'):
                par_list.extend(item.get_parameters())
        return par_list

    def __repr__(self) -> str:
        """String representation of the collection."""
        return f'{self.__class__.__name__} `{self.name}` of length {len(self)}'

    @property
    def names(self) -> list:
        """
        :returns: list of names for the elements in the collection.
        """
        return [i.name for i in self]

    def move_up(self, index: int):
        """Move the element at the given index up in the collection.

        :param index: Index of the element to move up.
        """
        if index == 0:
            return
        self.insert(index - 1, self.pop(index))

    def move_down(self, index: int):
        """Move the element at the given index down in the collection.

        :param index: Index of the element to move down.
        """
        if index == len(self) - 1:
            return
        self.insert(index + 1, self.pop(index))

    def remove(self, index: int):
        """
        Remove an element from the elements.

        :param index: Index of the element to remove
        """
        self.pop(index)

    def as_dict(self, skip: Optional[List[str]] = None) -> dict:
        """
        Create a dictionary representation of the collection.

        :return: A dictionary representation of the collection
        """
        if skip is None:
            skip = []

        # Always skip unique_name for nested Parameters to avoid collisions during from_dict
        param_skip = list(skip) + ['unique_name'] if 'unique_name' not in skip else list(skip)

        this_dict = {
            '@module': self.__class__.__module__,
            '@class': self.__class__.__name__,
            '@version': None,
            'name': self.name,
        }

        # Add unique_name if not default
        if 'unique_name' not in skip and not self._default_unique_name:
            this_dict['unique_name'] = self.unique_name

        this_dict['data'] = []
        for collection_element in self:
            if hasattr(collection_element, 'as_dict'):
                this_dict['data'].append(collection_element.as_dict(skip=param_skip))
            elif hasattr(collection_element, 'to_dict'):
                this_dict['data'].append(collection_element.to_dict(skip=param_skip))
            else:
                this_dict['data'].append(collection_element)
        this_dict['populate_if_none'] = self.populate_if_none
        return this_dict

    def to_dict(self, skip: Optional[List[str]] = None) -> dict:
        """Convert to dictionary for serialization (alias for as_dict).

        This overrides NewBase.to_dict to use our custom serialization.

        :param skip: List of keys to skip, defaults to `None`.
        :return: Dictionary representation of the collection.
        """
        return self.as_dict(skip=skip)

    def __deepcopy__(self, memo):
        return self.from_dict(self.as_dict(skip=['unique_name']))

    @classmethod
    def from_dict(cls, obj_dict: Dict[str, Any]) -> 'BaseCollection':
        """
        Re-create a collection from a dictionary.

        :param obj_dict: Dictionary containing the serialized contents.
        :return: Reformed collection object.
        """
        if not SerializerBase._is_serialized_easyscience_object(obj_dict):
            raise ValueError('Input must be a dictionary representing an EasyScience object.')

        # Extract data items and deserialize them
        data_items = obj_dict.get('data', [])
        deserialized_items = []
        for item_dict in data_items:
            if isinstance(item_dict, dict) and SerializerBase._is_serialized_easyscience_object(item_dict):
                # Get the class and deserialize
                deserialized_item = SerializerBase._deserialize_value(item_dict)
                deserialized_items.append(deserialized_item)
            else:
                deserialized_items.append(item_dict)

        # Build kwargs without data
        name = obj_dict.get('name', cls.__name__)
        unique_name = obj_dict.get('unique_name', None)
        populate_if_none = obj_dict.get('populate_if_none', False)

        # Create instance with items as positional args
        instance = cls(name, *deserialized_items, unique_name=unique_name, populate_if_none=populate_if_none)
        return instance

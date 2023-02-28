#  SPDX-FileCopyrightText: 2023 easyCrystallography contributors <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2022-2023  Contributors to the easyCore project <https://github.com/easyScience/easyCrystallography>

from __future__ import annotations

__author__ = 'github.com/wardsimon'
__version__ = '0.1.0'

from typing import ClassVar, TYPE_CHECKING, Union, List
from easyCore import np
from easyCore.Objects.Variable import Parameter
from easyCore.Objects.Groups import BaseCollection

if TYPE_CHECKING:
    from easyCore.Utils.typing import iF, BV

class Moment:

    spin: ClassVar[Parameter]
    axis: np.ndarray

    def __init__(self,
                 spin: Union[float, Parameter],
                 moment: Union[List, np.ndarray, ]):
        super().__init__(*args, **kwargs)
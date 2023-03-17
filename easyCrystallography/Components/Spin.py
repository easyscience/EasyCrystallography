from __future__ import annotations
#  SPDX-FileCopyrightText: 2023 easyCrystallography contributors <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2022-2023  Contributors to the easyCore project <https://github.com/easyScience/easyCrystallography>

__author__ = "github.com/wardsimon"
__version__ = "0.1.0"

from easyCore import np
from typing import Union, Optional, TYPE_CHECKING, ClassVar

if TYPE_CHECKING:
    import numpy.typing as npt
    from easyCore.Utils.typing import iF
    from easyCrystallography.Components.SpaceGroup import SpaceGroup

from easyCore.Objects.Variable import Parameter
from easyCore.Objects.ObjectClasses import BaseObj


class Spin(BaseObj):


    s_x: ClassVar[Parameter]
    s_y: ClassVar[Parameter]
    s_z: ClassVar[Parameter]
    m: ClassVar[Parameter]

    def __init__(self,
                 s_x: Optional[Union[Parameter, float]] = None,
                 s_y: Optional[Union[Parameter, float]] = None,
                 s_z: Optional[Union[Parameter, float]] = None,
                 m: Optional[Union[Parameter, float]] = None,
                 normal: Optional[npt.ArrayLike] = None,
                 normalize: bool = True,
                 interface: Optional[iF] = None):

        super().__init__(
            'Sxyz',
            s_x=Parameter('s_x', 0.0, fixed=True),
                         s_y=Parameter('s_y', 0.0, fixed=True),
                         s_z=Parameter('s_z', 1.0, fixed=True),
                         m=Parameter('m', 1.0, fixed=True))

        if normal is None:
            normal = np.array([0, 0, 1])

        self.normal = np.asarray(normal)

        if s_x is not None:
            self.s_x = s_x
        if s_y is not None:
            self.s_y = s_y
        if s_z is not None:
            self.s_z = s_z
        if m is not None:
            self.m = m

        if normalize:
            self.normalize()
        self.interface = interface

    def normalize(self):
        S = np.sqrt(self.s_x.raw_value ** 2 + self.s_y.raw_value ** 2 + self.s_z.raw_value ** 2)
        self.s_x = self.s_x.raw_value / S
        self.s_y = self.s_y.raw_value / S
        self.s_z = self.s_z.raw_value / S

    @property
    def vector(self):
        return np.array([self.s_x.raw_value, self.s_y.raw_value, self.s_z.raw_value])

    @property
    def theta(self):
        theta, phi = xyz_to_theta_phi(self.s_x.raw_value, self.s_y.raw_value, self.s_z.raw_value)
        return theta

    @property
    def phi(self):
        theta, phi = xyz_to_theta_phi(self.s_x.raw_value, self.s_y.raw_value, self.s_z.raw_value)
        return phi

    @property
    def matrix(self):
        theta, phi = xyz_to_theta_phi(self.s_x.raw_value, self.s_y.raw_value, self.s_z.raw_value)
        return np.matmul(Rx(theta), Rz(-phi))

    def images(self, spacegroup: SpaceGroup):
        point = self.vector
        return [self.__class__(image[0], image[1], image[2], self.m.raw_value) for image in spacegroup.get_orbit(point)]



def xyz_to_theta_phi(X, Y, Z):
    if Z > 0:
        theta = np.arctan2(np.sqrt(X ** 2 + Y ** 2), Z)
    elif Z < 0:
        theta = np.pi + np.arctan2(np.sqrt(X ** 2 + Y ** 2), Z)
    elif Z == 0 and X != 0 and Y != 0:
        theta = np.pi / 2
    else:
        theta = np.pi / 2
    if X > 0:
        phi = np.arctan2(Y, X)
    elif X < 0 <= Y:
        phi = np.pi + np.arctan2(Y, X)
    elif X < 0 and Y < 0:
        phi = -np.pi + np.arctan2(Y, X)
    elif X == 0 and Y > 0:
        phi = np.pi / 2
    elif X == 0 and Y < 0:
        phi = -np.pi / 2
    else:
        phi = 0
    return theta, phi
def Rx(theta):
    """
    Rotation matrix about the x-axis.
    Args:
        theta: Rotation angle in radians.
    Returns: Rotation matrix.
    """
    return np.array([[1, 0, 0],
                      [0, np.cos(theta), -np.sin(theta)],
                      [0, np.sin(theta), np.cos(theta)]])


def Ry(theta):
    """
    Rotation matrix about the y-axis.
    Args:
        theta: Rotation angle in radians.
    Returns: Rotation matrix.
    """
    return np.array([[np.cos(theta), 0, np.sin(theta)],
                      [0, 1, 0],
                      [-np.sin(theta), 0, np.cos(theta)]])


def Rz(theta):
    """
    Rotation matrix about the z-axis.
    Args:
        theta: Rotation angle in radians.
    Returns: Rotation matrix.
    """
    return np.array([[np.cos(theta), -np.sin(theta), 0],
                      [np.sin(theta), np.cos(theta), 0],
                      [0, 0, 1]])
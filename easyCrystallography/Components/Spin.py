from __future__ import annotations

#  SPDX-FileCopyrightText: 2023 easyCrystallography contributors <crystallography@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2022-2023  Contributors to the easyCore project <https://github.com/easyScience/easyCrystallography>

__author__ = "github.com/wardsimon"
__version__ = "0.1.0"

from easyCore import np
from typing import Union, Optional, TYPE_CHECKING, ClassVar, Tuple, NoReturn

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
        """
        A spin object for a site defined by a spin vector and a magnetic moment.
        """

        super().__init__(
            'Sxyz',
            s_x=Parameter('s_x', 0.0, fixed=True, description='Spin x component'),
            s_y=Parameter('s_y', 0.0, fixed=True, description='Spin y component'),
            s_z=Parameter('s_z', 1.0, fixed=True, description='Spin z component'),
            m=Parameter('m', 1.0, fixed=True, description='Magnetic moment'))

        if normal is None:
            nx = np.array([1, 0, 0])
            ny = np.array([0, 1, 0])
            nz = np.array([0, 0, 1])
            normal = nz
        else:
            normal = np.asarray(normal)
            nz, nx, ny = self._generate_cart_axes(normal)

        self._normal = normal
        self._cartesian_axes = np.array([nx, ny, nz])

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

    @classmethod
    def from_vector(cls,
                    vector: npt.ArrayLike,
                    m: Optional[Union[Parameter, float]] = None,
                    normal: Optional[npt.ArrayLike] = None):
        """
        Create a spin object from a spin vector
        """
        s_x, s_y, s_z = vector
        return cls(s_x, s_y, s_z, m, normal=normal)

    @classmethod
    def from_angles(cls,
                    theta: Optional[float] = 0,
                    phi: Optional[float] = 0,
                    m: Optional[Union[Parameter, float]] = None,
                    radians: bool = False,
                    normal: Optional[npt.ArrayLike] = None):
        # Set default normal to z-axis
        if normal is None:
            normal = np.array([0, 0, 1])

        # Convert to radians if needed
        if not radians:
            theta = np.radians(theta)
            phi = np.radians(phi)

        # Generate axes from normal
        ax_z, ax_x, ax_y = cls._generate_cart_axes(normal)
        axes = np.array([ax_z, ax_y, ax_x])
        angles = np.array([0, 0, 0])

        matrices = np.array([rotate_about_axis(ax, ang) for ax, ang in zip(axes, angles)])
        matrix = np.matmul(matrices[0], np.matmul(matrices[1], matrices[2]))

        if m is None:
            m = 1.0
        spherical = np.array([m * np.cos(theta) * np.sin(phi),
                              m * np.sin(theta) * np.sin(phi),
                              m * np.cos(phi)])

        sx, sy, sz = np.matmul(matrix, spherical)
        return cls(sx, sy, sz, m, normalize=False, normal=normal)

    @property
    def normal(self) -> np.ndarray:
        return self._normal

    @normal.setter
    def normal(self, value: npt.ArrayLike):
        self._normal = np.asarray(value)
        self._cartesian_axes = np.array(self._generate_cart_axes(self._normal))

    @property
    def axes(self) -> np.ndarray:
        return self._cartesian_axes

    @property
    def XYZ(self) -> np.ndarray:
        return np.matmul(matrix_between_vectors(self.normal, [0, 0, 1]), self.vector)

    @property
    def vector(self) -> np.ndarray:
        """
        Return the spin vector as a numpy array.
        """
        return np.array([self.s_x.raw_value, self.s_y.raw_value, self.s_z.raw_value])

    @vector.setter
    def vector(self, value: npt.ArrayLike):
        self.s_x, self.s_y, self.s_z = value

    @property
    def theta(self) -> float:
        """
        Return the polar angle of the spin vector.
        """
        theta = np.arctan2(self.s_y.raw_value, self.s_x.raw_value)
        return theta

    @property
    def phi(self) -> float:
        """
        Return the azimuthal angle of the spin vector.
        """
        phi = np.arccos(self.s_z.raw_value / np.linalg.norm(self.vector))
        return phi

    @property
    def angles(self) -> Tuple[float, float]:
        """
        Return the Spherical angles of the spin vector.
        """
        return self.theta, self.phi

    @property
    def matrix(self) -> np.ndarray:
        """
        Return the spin vector as a 3x3 rotation matrix.
        """
        theta = self.theta
        phi = self.phi

        # Compute the rotation matrix
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        cos_phi = np.cos(phi)
        sin_phi = np.sin(phi)

        rotation_matrix = np.array([
            [cos_theta * cos_phi, cos_theta * sin_phi, -sin_theta],
            [-sin_phi, cos_phi, 0],
            [sin_theta * cos_phi, sin_theta * sin_phi, cos_theta]
        ])

        return rotation_matrix

    def normalize(self) -> NoReturn:
        """
        Normalise the spin vector to unit length
        """
        vector = self.vector
        s_normalization = np.linalg.norm(vector)
        self.vector = vector / s_normalization

    def apply_matrix(self, matrix: np.ndarray) -> NoReturn:
        """
        Apply a rotation matrix to the spin vector.
        """
        if matrix.shape == (4, 4):
            # Remove the translation component
            matrix = matrix[:3, :3]

        vector = self.vector
        new_vector = np.matmul(matrix, vector)
        self.s_x = new_vector[0]
        self.s_y = new_vector[1]
        self.s_z = new_vector[2]

    def __repr__(self) -> str:
        """
        String representation of the spin object.
        """
        return f'Spin [{self.s_x.raw_value}, {self.s_y.raw_value}, {self.s_z.raw_value}], S = {self.m.raw_value}'

    @staticmethod
    def _generate_cart_axes(n: npt.ArrayLike) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Generate the cartesian axes from a normal vector. The z-axis is the normal vector and the results are
        normalised.
        """
        n = np.asarray(n)
        z = np.array([0, 0, -1])
        y = np.array([0, -1, 0])

        c = np.cross(n, z)
        if np.any(c):
            vy = np.cross(n, z)
        else:
            vy = np.cross(n, y)
        vz = np.cross(n, vy)

        vx = n / np.linalg.norm(n)
        vy = vy / np.linalg.norm(vy)
        vz = vz / np.linalg.norm(vz)
        return vx, vy, vz

    def rotate(self, axis: npt.ArrayLike, angle: float, radians: bool = False) -> NoReturn:
        """
        Rotate the spin vector about an axis by an angle
        """
        axis = np.asarray(axis)
        if not radians:
            angle = np.deg2rad(angle)
        rotation_matrix = rotate_about_axis(axis, angle)
        self.s_x, self.s_y, self.s_z = np.matmul(rotation_matrix,
                                                 np.array([self.s_x.raw_value, self.s_y.raw_value, self.s_z.raw_value]))

    def mirror(self, normal_vector: npt.ArrayLike) -> NoReturn:
        """
        Mirror the spin vector about a plane defined by a normal vector.
        """

        n, u, v = self._generate_cart_axes(normal_vector)
        matrix = np.matmul(np.matmul(np.array([u.T, v.T, n.T]), np.diag([1, 1, -1])),
                           np.array([u.T, v.T, n.T]).T)
        reflected_coords = np.matmul(matrix, self.vector)
        self.vector = reflected_coords

    def euler_angles(self) -> Tuple[float, float, float]:
        """
        Return the Euler angles of the spin vector.
        """
        x, y, z = self.vector
        alpha = np.arctan2(y, x)
        beta = np.arctan2(np.sqrt(x ** 2 + y ** 2), z)
        gamma = self.phi
        return alpha, beta, gamma


def rotate_about_axis(axis: npt.ArrayLike, angle: float) -> np.ndarray:
    """
    Generate a rotation matrix for a rotation about an axis by an angle.
    """
    axis = np.asarray(axis)
    axis = axis / np.linalg.norm(axis)
    a = np.cos(angle / 2)
    b, c, d = axis * np.sin(angle / 2)
    return np.array([[a * a + b * b - c * c - d * d, 2 * (b * c - a * d), 2 * (b * d + a * c)],
                     [2 * (b * c + a * d), a * a + c * c - b * b - d * d, 2 * (c * d - a * b)],
                     [2 * (b * d - a * c), 2 * (c * d + a * b), a * a + d * d - b * b - c * c]])


def matrix_between_vectors(vector1: npt.ArrayLike, vector2: npt.ArrayLike) -> np.ndarray:
    """
    Returns the rotation matrix in order to rotate vector1 to vector2
    """
    vector1 = np.array(vector1)
    vector2 = np.array(vector2)

    # Check if the vectors are co-linear
    v = np.cross(vector1, vector2)
    if np.all(v == 0):
        # The vectors are co-linear, create another vector C which is normal to vector1.
        # Rotate around this vector by pi.
        scale = np.sum(np.abs(vector1))
        if scale == 0:
            return np.eye(3)
        this_vector = vector1 / scale
        if np.abs(this_vector[0]) > np.abs(this_vector[1]):
            this_vector = np.array([this_vector[2], 0, -this_vector[0]])
        else:
            this_vector = np.array([0, this_vector[2], -this_vector[1]])
        return rotate_about_axis(this_vector, np.pi)

    c = np.dot(vector1, vector2)
    h = (1 - c) / (1 - c ** 2)

    vx, vy, vz = v
    matrix = [[c + h * vx ** 2, h * vx * vy - vz, h * vx * vz + vy],
              [h * vx * vy + vz, c + h * vy ** 2, h * vy * vz - vx],
              [h * vx * vz - vy, h * vy * vz + vx, c + h * vz ** 2]]
    return np.array(matrix)

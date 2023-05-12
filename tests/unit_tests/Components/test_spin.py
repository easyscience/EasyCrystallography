#  SPDX-FileCopyrightText: 2023 easyCore contributors  <core@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2023 Contributors to the easyCore project <https://github.com/easyScience/easyCore>

__author__ = "github.com/wardsimon"
__version__ = "0.1.0"

import pytest
from easyCore import np
from easyCrystallography.Components.Spin import Spin, matrix_between_vectors


def test_spin_creation():
    s = Spin()
    assert s.s_x.raw_value == 0.0
    assert s.s_y.raw_value == 0.0
    assert s.s_z.raw_value == 1.0
    assert s.m.raw_value == 1.0


def test_spin_creation_with_values():
    s = Spin(s_x=1, s_y=2, s_z=3, m=4, normalize=False)
    assert s.s_x.raw_value == 1.0
    assert s.s_y.raw_value == 2.0
    assert s.s_z.raw_value == 3.0
    assert s.m.raw_value == 4.0


def test_spin_creation_with_values_and_normalize():
    s = Spin(s_x=1, s_y=2, s_z=3, m=4)

    n = np.sqrt(1 ** 2 + 2 ** 2 + 3 ** 2)

    assert s.s_x.raw_value == pytest.approx(1.0 / n)
    assert s.s_y.raw_value == pytest.approx(2.0 / n)
    assert s.s_z.raw_value == pytest.approx(3.0 / n)
    assert s.m.raw_value == 4.0


@pytest.mark.parametrize('radians', [True, False])
@pytest.mark.parametrize("angles, expected", zip([[0, 0],    [90, 0],   [180, 0],   [0, 90],   [0, 180],  [0, 270],
                                                  [90, 90]],
                                                 [[0, 0, 1], [1, 0, 0], [0, 0, -1], [0, 0, 1], [0, 0, 1], [0, 0, 1],
                                                  [0, 1, 0]]))
def test_spin_along_axis(angles, expected, radians):
    theta, phi = angles
    if radians:
        theta = np.deg2rad(theta)
        phi = np.deg2rad(phi)
    s = Spin.from_angles(theta=theta, phi=phi, radians=radians)
    assert expected == pytest.approx(s.vector)


@pytest.mark.parametrize('radians', [True, False])
@pytest.mark.parametrize('finput, output',
                         zip([[90, [1, 0, 0]], [90, [0, 1, 0]], [90, [0, 0, 1]]], [[0, -1, 0], [1, 0, 0], [0, 0, 1]]))
def test_spin_rotate(finput, output, radians):
    # Create a spin along the z axis
    s = Spin()
    angle, axis = finput
    if radians:
        angle = np.deg2rad(angle)
    # Rotate it by 90 degrees about the x-axis
    s.rotate(axis=axis, angle=angle, radians=radians)
    # Check that it is now along the -y-axis
    assert output == pytest.approx(s.vector)


@pytest.mark.parametrize('radians', [True, False])
@pytest.mark.parametrize("angles, expected", zip([[0, 0], [90, 0], [180, 0], [0, 90], [0, 180], [0, 270], [90, 90]],
                                                 [[0, 0, 1], [1, 0, 0], [0, 0, -1], [1, 0, 0], [0, 0, -1], [-1, 0, 0],
                                                  [0, 1, 0]]))
def test_angles(angles, expected, radians):
    theta, phi = angles
    if radians:
        theta = np.deg2rad(theta)
        phi = np.deg2rad(phi)
    s = Spin.from_angles(theta=theta, phi=phi, radians=radians)

    x, y, z = expected
    theta = np.arctan2(y, x)
    phi = np.arccos(z / np.sqrt(x ** 2 + y ** 2 + z ** 2))

    if np.abs(theta) < 1e-6:
        theta = 0
        # We are rotating around an axis in the xy plane
        phi = 0
    if np.abs(phi) - np.pi < 1e-6:
        # We have a full rotation around the z-axis
        phi = 0
    if np.abs(theta) - np.pi < 1e-6:
        # We have a full rotation around the y-axis
        theta = 0

    assert s.angles == pytest.approx((theta, phi))


@pytest.mark.parametrize('radians', [True, False])
@pytest.mark.parametrize("angles, expected", zip([[0, 0], [90, 0], [180, 0], [0, 90], [0, 180], [0, 270], [90, 90]],
                                                 [[0, 0, -1], [-1, 0, 0], [0, 0, 1], [0, 0, -1], [0, 0, -1], [0, 0, -1],
                                                  [0, 1, 0]]))
def test_XYZ(angles, expected, radians):
    theta, phi = angles
    if radians:
        theta = np.deg2rad(theta)
        phi = np.deg2rad(phi)
    s = Spin.from_angles(theta=theta, phi=phi, radians=radians, normal=[0, 0, -1])
    new_vec = s.XYZ
    assert expected == pytest.approx(new_vec)


@pytest.mark.parametrize("angles, expected", zip([[0, 0],    [90, 0],   [180, 0], [0, 90], [0, 180], [0, 270], [90, 90]],
                                                 [[0, 0, 1], [1, 0, 0], [0, 0, -1], [1, 0, 0], [0, 0, -1], [-1, 0, 0],
                                                  [0, 1, 0]]))
def test_matrices(angles, expected):

    rotation_matrix = matrix_between_vectors([0, 0, 1], expected)
    s = Spin()
    s.apply_matrix(rotation_matrix)
    assert np.array(expected) == pytest.approx(s.vector)
    assert rotation_matrix == pytest.approx(s.matrix)

@pytest.mark.parametrize("start_vector, end_results", zip([[0, 0, 1], [1, 0, 0], [1, 0, 0]],
                                                          [([0, 0, 1], [0, 0, -1]), ([0, 0, 1], [1, 0, 0]), ([0, 1, 0], [1, 0, 0])]
                                                          ))
def test_mirror(start_vector, end_results):
    s = Spin(*start_vector)
    normal, result = end_results
    s.mirror(normal)
    assert result == pytest.approx(s.vector)

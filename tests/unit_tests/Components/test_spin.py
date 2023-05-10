#  SPDX-FileCopyrightText: 2023 easyCore contributors  <core@easyscience.software>
#  SPDX-License-Identifier: BSD-3-Clause
#  © 2023 Contributors to the easyCore project <https://github.com/easyScience/easyCore>

__author__ = "github.com/wardsimon"
__version__ = "0.1.0"

import pytest
from easyCore import np
from easyCrystallography.Components.Spin import Spin


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
@pytest.mark.parametrize("angles, expected", zip([[0, 0], [90, 0], [180, 0], [0, 90], [0, 180], [0, 270], [90, 90]],
                                                 [[0, 0, 1], [0, 0, 1], [0, 0, 1], [1, 0, 0], [0, 0, -1], [-1, 0, 0],
                                                  [0, 1, 0]]))
def test_spin_along_axis(angles, expected, radians):
    theta, phi = angles
    if radians:
        theta = np.deg2rad(theta)
        phi = np.deg2rad(phi)
    sx, sy, sz = expected
    s = Spin.from_angles(theta=theta, phi=phi, radians=radians)
    assert s.s_x.raw_value == pytest.approx(sx)
    assert s.s_y.raw_value == pytest.approx(sy)
    assert s.s_z.raw_value == pytest.approx(sz)


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
    assert s.s_x.raw_value == pytest.approx(output[0])
    assert s.s_y.raw_value == pytest.approx(output[1])
    assert s.s_z.raw_value == pytest.approx(output[2])


@pytest.mark.parametrize('radians', [True, False])
@pytest.mark.parametrize("angles, expected", zip([[0, 0], [90, 0], [180, 0], [0, 90], [0, 180], [0, 270], [90, 90]],
                                                 [[0, 0, 1], [0, 0, 1], [0, 0, 1], [1, 0, 0], [0, 0, -1], [-1, 0, 0],
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
    assert s.angles == pytest.approx((theta, phi))


@pytest.mark.parametrize('radians', [True, False])
@pytest.mark.parametrize("angles, expected", zip([[0, 0], [90, 0], [180, 0], [0, 90], [0, 180], [0, 270], [90, 90]],
                                                 [[0, 0, -1], [0, 0, -1], [0, 0, -1], [-1, 0, 0], [0, 0, 1], [1, 0, 0],
                                                  [0, 1, 0]]))
def test_XYZ(angles, expected, radians):
    theta, phi = angles
    if radians:
        theta = np.deg2rad(theta)
        phi = np.deg2rad(phi)
    s = Spin.from_angles(theta=theta, phi=phi, radians=radians, normal=[0, 0, -1])
    new_vec = s.XYZ
    assert expected == pytest.approx(new_vec)

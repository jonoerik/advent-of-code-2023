import copy
import itertools

import sympy
from sympy import Matrix

class Line:
    def __init__(self, x, y, z, dx, dy, dz):
        """Accept a line of form U + t * V, where U, V are 3-vectors, and t is any real number.
        Convert internally to representing the line by two points on that line (initially U and U+V),
        for easier application of affine transformations.
        Last coordinate should always be 1, and allows for multiplication by an augmented matrix."""
        self.p1 = Matrix([x, y, z, 1])
        self.p2 = Matrix([x + dx, y + dy, z + dz, 1])

    def apply_affine(self, A):
        """Apply affine transformation matrix A to this line."""
        self.p1 = A * self.p1
        self.p2 = A * self.p2

    def apply_affine_inverse(self, A):
        """Apply to this line the inverse affine transformation to
        that given by matrix A."""
        A_inv = A.inv()
        self.p1 = A_inv * self.p1
        self.p2 = A_inv * self.p2

    def __str__(self) -> str:
        return f"({self.p1[0,0]}, {self.p1[1,0]}, {self.p1[2,0]}) -> ({self.p2[0,0]}, {self.p2[1,0]}, {self.p2[2,0]})"


def find_intersecting_line(lines: list[Line]) -> Line | None:
    """Construct a straight line intersecting with all input lines, if one exists.

    Assumes enough of the input lines are skew that a unique solution exists.
    If no intersecting line exists, return None.

    Uses method from section 2 of:
        Zejun Huang, Chi-Kwong Li, Nung-Sing Sze,
        Constructing a straight line intersecting four lines,
        Linear Algebra and its Applications,
        Volume 683, 2024, Pages 201-210,
        ISSN 0024-3795,
        https://doi.org/10.1016/j.laa.2023.11.024.
        (https://www.sciencedirect.com/science/article/pii/S0024379523004445)"""

    def affine_rotation_x(theta):
        """Return an affine transformation matrix that rotates around the x-axis
        by theta radians."""
        return Matrix([[1, 0, 0, 0],
                       [0, sympy.cos(theta), -sympy.sin(theta), 0],
                       [0, sympy.sin(theta), sympy.cos(theta), 0],
                       [0, 0, 0, 1]])

    def affine_rotation_y(theta):
        """Return an affine transformation matrix that rotates around the y-axis
        by theta radians."""
        return Matrix([[sympy.cos(theta), 0, sympy.sin(theta), 0],
                       [0, 1, 0, 0],
                       [-sympy.sin(theta), 0, sympy.cos(theta), 0],
                       [0, 0, 0, 1]])

    def affine_translation(x, y, z):
        """Return an affine transformation matrix that translates each dimension
        by the given parameter."""
        return Matrix([[1, 0, 0, x],
                       [0, 1, 0, y],
                       [0, 0, 1, z],
                       [0, 0, 0, 1]])

    def affine_scale(x, y, z):
        """Return an affine transformation matrix that scales each dimension by the
        given parameter."""
        return Matrix([[x, 0, 0, 0],
                       [0, y, 0, 0],
                       [0, 0, z, 0],
                       [0, 0, 0, 1]])

    def affine_shear_x_by_z(scale):
        """Return an affine transformation matrix that shears in the direction of the x-axis,
        proportional to distance in z, multiplied by scale."""
        return Matrix([[1, 0, scale, 0],
                       [0, 1, 0, 0],
                       [0, 0, 1, 0],
                       [0, 0, 0, 1]])

    def check_lines_skew(l1: Line, l2: Line):
        """Return True iff lines l1 and l2 are skew; i.e. none of these situations are true:
        * l1 and l2 are the same line
        * l1 and l2 are parallel
        * l1 and l2 lie in parallel planes"""
        # Uses Lemma 1.2 from the paper.
        u1 = l1.p1[:3, 0]
        v1 = l1.p2[:3, 0] - l1.p1[:3, 0]
        u2 = l2.p1[:3, 0]
        v2 = l2.p2[:3, 0] - l2.p1[:3, 0]
        M1 = Matrix.hstack(v1, v2, u2)
        M2 = Matrix.hstack(v1, v2, u1)
        return M1.det() != M2.det()

    original_lines = copy.deepcopy(lines)

    # Choose first 4 lines that are all skew.
    skew_lines = []
    for l_candidate in lines:
        if all([check_lines_skew(l1, l2) for l1, l2 in itertools.combinations(skew_lines + [l_candidate], 2)]):
            skew_lines.append(l_candidate)
        if len(skew_lines) >= 4:
            break
    if len(skew_lines) < 4:
        return None
    for l1, l2 in itertools.combinations(skew_lines, 2):
        assert check_lines_skew(l1, l2)
    lines = skew_lines

    all_transforms = Matrix.eye(4, 4)
    def all_affine(A):
        for l in lines:
            l.apply_affine(A)

        nonlocal all_transforms
        all_transforms = A * all_transforms

    a = lines[0]
    b = lines[1]

    all_affine(affine_translation(-a.p1[0,0], -a.p1[1,0], -a.p1[2,0]))
    assert a.p1[1,0] == 0 and a.p1[2,0] == 0
    if a.p2[1,0] != 0:
        all_affine(affine_rotation_x(sympy.atan(a.p2[1,0] / a.p2[2,0])))
    if a.p2[2,0] != 0:
        all_affine(affine_rotation_y(sympy.atan(a.p2[2,0] / a.p2[0,0])))
    assert a.p2[1,0] == 0 and a.p2[2,0] == 0
    assert a.p1[0,0] != a.p2[0,0]
    # a == e_1, a is the X axis.

    all_affine(affine_translation(-b.p1[0,0], 0, 0))
    if b.p1[2,0] != 0:
        all_affine(affine_rotation_x(sympy.atan(-b.p1[2,0] / b.p1[1,0])))
    assert b.p1[2,0] == 0
    if b.p2[0,0] != 0:
        all_affine(affine_shear_x_by_z(-b.p2[0,0] / b.p2[2,0]))
    assert b.p2[0,0] == 0
    if b.p1[2,0] != b.p2[2,0]:
        all_affine(affine_rotation_x(sympy.atan((b.p2[2,0] - b.p1[2,0]) / (b.p1[1,0] - b.p2[1,0]))))
    assert b.p1[2,0] == b.p2[2,0]
    if b.p1[2,0] != 1:
        all_affine(affine_scale(1, 1, 1 / b.p1[2,0]))
    # b == e_2 + t * e_3, b is parallel to the Z axis, offset by 1 in the direction of the Y axis.

    # Lines a and b are now known lines, as we've applied the 'suitable affine transformation' required at the start
    # of theorem 2.1 of the paper.

    u_31 = lines[2].p1[0,0]
    u_32 = lines[2].p1[1,0]
    u_33 = lines[2].p1[2,0]
    v_31 = lines[2].p2[0,0] - lines[2].p1[0,0]
    v_32 = lines[2].p2[1,0] - lines[2].p1[1,0]
    v_33 = lines[2].p2[2,0] - lines[2].p1[2,0]
    u_41 = lines[3].p1[0,0]
    u_42 = lines[3].p1[1,0]
    u_43 = lines[3].p1[2,0]
    v_41 = lines[3].p2[0,0] - lines[3].p1[0,0]
    v_42 = lines[3].p2[1,0] - lines[3].p1[1,0]
    v_43 = lines[3].p2[2,0] - lines[3].p1[2,0]

    a_3 = v_32 * u_33 - u_32 * v_33
    b_3 = u_31 * v_33 - v_31 * u_33
    c_3 = v_31 * u_32 - u_31 * v_32
    a_4 = v_42 * u_43 - u_42 * v_43
    b_4 = u_41 * v_43 - v_41 * u_43
    c_4 = v_41 * u_42 - u_41 * v_42

    # Find the polynomial p(z) in the form p(z) = az^2 + bz + c.
    p_z_a = v_33 * a_4 - v_33 * v_42 - v_43 * a_3 + v_43 * v_32
    p_z_b = v_33 * c_4 + b_3 * a_4 - b_3 * v_42 - v_43 * c_3 - b_4 * a_3 + b_4 * v_32
    p_z_c = b_3 * c_4 - b_4 * c_3

    # Polynomial should have two roots.
    if p_z_a == 0:
        return None
    if (p_z_b ** 2) - (4 * p_z_a * p_z_c) <= 0:
        return None

    L_0_original = None

    # Find root that gives the line that intersects with all required lines.
    for t_1 in ((-p_z_b + sympy.sqrt((p_z_b ** 2) - (4 * p_z_a * p_z_c))) / (2 * p_z_a),
                (-p_z_b - sympy.sqrt((p_z_b ** 2) - (4 * p_z_a * p_z_c))) / (2 * p_z_a)):
        assert p_z_a * (t_1 ** 2) + p_z_b * t_1 + p_z_c == 0
        if v_33 * t_1 + b_3 == 0:
            continue
        if v_43 * t_1 + b_4 == 0:
            continue
        t_2 = -((a_3 - v_32) * t_1 + c_3) / (v_33 * t_1 + b_3)
        assert t_2 == -(((a_4 - v_42) * t_1 + c_4) / (v_43 * t_1 + b_4))

        L_0 = Line(-t_1, 0, 0, t_1, t_2, 1)

        # Check that L_0 intersects all given lines.
        def min_distance(l1: Line, l2: Line):
            n = Matrix.cross((l1.p2 - l1.p1)[:3, 0], (l2.p2 - l2.p1)[:3, 0])
            return abs(Matrix.dot(n, l1.p1[:3, 0] - l2.p1[:3, 0])) / n.norm()
        for l in lines:
            if min_distance(l, L_0) != 0:
                return None

        L_0_original = copy.deepcopy(L_0)
        L_0_original.apply_affine_inverse(all_transforms)

        # L_0 should intersect with all original lines.
        if all([min_distance(original_line, L_0_original) == 0 for original_line in original_lines]):
            break
    else:
        # One of the two options for t_1 should have worked.
        return None

    return L_0_original

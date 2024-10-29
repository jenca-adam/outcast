from .cCore import Matrix, Vec3

"""import math
DEPTH = 255

def linear_to_gamma(linear):
    if linear > 0:
        return linear ** (0.5)
    return 0


class Vec3:
    def __init__(self, x, y, z = 0):
        self.x = self.r = x
        self.y = self.g = y
        self.z = self.b = z
        self.e = (x,y,z)
        self._normalized = None
    @classmethod
    def from_matrix(cls, ma):
        return cls(
            int(ma[0][0] / ma[3][0]),
            int(ma[1][0] / ma[3][0]),
            -int(ma[2][0] / ma[3][0]),
        )

    @classmethod
    def from_matrix3(cls, ma):
        return cls(ma[0][0], ma[1][0], ma[2][0])

    @property
    def length(self):
        return self.length_squared**0.5

    @property
    def length_squared(self):
        return self.x**2 + self.y**2 + self.z**2

    def cross(self, v):
        return Vec3(
            self.e[1] * v.e[2] - self.e[2] * v.e[1],
            self.e[2] * v.e[0] - self.e[0] * v.e[2],
            self.e[0] * v.e[1] - self.e[1] * v.e[0],
        )

    def apply_3d_rotation(self, vec):
        v = Matrix.from_vector(vec)
        v = Matrix.rotx(self.x) @ v
        v = Matrix.roty(self.y) @ v
        v = Matrix.rotz(self.z) @ v
        return Vec3.from_matrix3(v)

    def __len__(self):
        return 3

    def __add__(self, v):
        return Vec3(self.x + v.x, self.y + v.y, self.z + v.z)

    def __sub__(self, v):
        return self + (-v)

    def __truediv__(self, s):
        return self * (1 / s)

    def __floordiv__(self, s):
        return Vec3(self.x // s, self.y // s, self.z // s)

    def __neg__(self):
        return Vec3(-self.x, -self.y, -self.z)

    def __mul__(self, s):
        return Vec3(self.x * s, self.y * s, self.z * s)

    def __rmul__(self, s):
        return self * s

    def __repr__(self):
        return f"Vec3({self.x:.2f}, {self.y:.2f}, {self.z:.2f})"

    def __iter__(self):
        return iter((self.x, self.y, self.z))

    def __getitem__(self, i):
        return self.x if i == 0 else (self.y if i == 1 else (self.z))

    def asrgb(self):
        return Vec3(int(self.x * 256), int(self.y * 256), int(self.z * 256))

    def _normalize(self):
        if self.length == 0:
            return Vec3(0, 0, 0)
        return self / self.length
    def normalized(self):
        if self._normalized is None:
            self._normalized = self._normalize()
        return self._normalized
    def gamma_corrected(self):
        return Vec3(
            linear_to_gamma(self.x), linear_to_gamma(self.y), linear_to_gamma(self.z)
        )

    def near_zero(self):
        return abs(self.x) < 1e-8 and abs(self.y) < 1e-8 and abs(self.z) < 1e-8

    def item_mul(self, v):
        return Vec3(self.x * v.x, self.y * v.y, self.z * v.z)

    def abs(self):
        return Vec3(abs(self.x), abs(self.y), abs(self.z))

    def dot(self, v):
        return self.x * v.x + self.y * v.y + self.z * v.z


class Matrix:
    def __init__(self, m):
        self.m = m
        self.cols = len(m[0])
        self.rows = len(m)

    def __getitem__(self, i):
        return self.m[i]

    def __matmul__(self, o):
        result = Matrix.empty(self.rows, o.cols)
        for i in range(self.rows):
            for j in range(o.cols):
                for k in range(self.cols):
                    result[i][j] += self[i][k] * o[k][j]
        return result

    def __repr__(self):
        return f"Matrix({self.m})"

    @classmethod
    def empty(cls, rows, cols):
        return cls([[0 for _ in range(cols)] for _ in range(rows)])

    @classmethod
    def identity(cls, d):
        return cls([[1 if i == j else 0 for i in range(d)] for j in range(d)])

    @classmethod
    def viewport(cls, x, y, w, h):
        ma = cls.identity(4)
        ma[0][3] = x + w / 2
        ma[1][3] = y + h / 2
        ma[2][3] = ma[2][2] = DEPTH / 2
        ma[0][0] = w / 2
        ma[1][1] = h / 2
        return ma

    @classmethod
    def from_vector(cls, ve):
        return cls([[i] for i in [*ve, 1]])

    @classmethod
    def rotz(cls, theta):
        ma = cls.identity(3)
        ma[0][0] = math.cos(theta)
        ma[0][1] = -math.sin(theta)
        ma[1][0] = math.sin(theta)
        ma[1][1] = math.cos(theta)
        return ma

    @classmethod
    def roty(cls, theta):
        ma = cls.identity(3)
        ma[0][0] = math.cos(theta)
        ma[0][2] = math.sin(theta)
        ma[2][0] = -math.sin(theta)
        ma[2][2] = math.cos(theta)
        return ma

    @classmethod
    def rotx(cls, theta):
        ma = cls.identity(3)
        ma[1][1] = math.cos(theta)
        ma[1][2] = -math.sin(theta)
        ma[2][1] = math.sin(theta)
        ma[2][2] = math.cos(theta)
        return ma

    def __neg__(self):
        return Matrix([[-i for i in r] for r in self.m])

    def apply_to_vector(self, vec3):
        return Vec3.from_matrix3(self @ Matrix.from_vector(vec3))

    def determinant(self):
        m = self.m
        return (
            m[0][0] * (m[1][1] * m[2][2] - m[1][2] * m[2][1])
            - m[0][1] * (m[1][0] * m[2][2] - m[1][2] * m[2][0])
            + m[0][2] * (m[1][0] * m[2][1] - m[1][1] * m[2][0])
        )

    def inverse(self):
        det = self.determinant()
        if det == 0:
            raise ValueError("Matrix is not invertible (determinant is zero)")

        m = self.m
        inv_det = 1.0 / det

        inv = Matrix(
            [
                [
                    (m[1][1] * m[2][2] - m[1][2] * m[2][1]) * inv_det,
                    -(m[0][1] * m[2][2] - m[0][2] * m[2][1]) * inv_det,
                    (m[0][1] * m[1][2] - m[0][2] * m[1][1]) * inv_det,
                ],
                [
                    -(m[1][0] * m[2][2] - m[1][2] * m[2][0]) * inv_det,
                    (m[0][0] * m[2][2] - m[0][2] * m[2][0]) * inv_det,
                    -(m[0][0] * m[1][2] - m[0][2] * m[1][0]) * inv_det,
                ],
                [
                    (m[1][0] * m[2][1] - m[1][1] * m[2][0]) * inv_det,
                    -(m[0][0] * m[2][1] - m[0][1] * m[2][0]) * inv_det,
                    (m[0][0] * m[1][1] - m[0][1] * m[1][0]) * inv_det,
                ],
            ]
        )

        return inv
"""


def array(a):
    return Vec3(*a)


BLACK = Vec3(0, 0, 0)

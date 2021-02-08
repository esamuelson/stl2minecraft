import sys
import unittest
from enum import Enum
from stl import mesh
import matplotlib.pyplot as plt


class Dimension(Enum):
    X = 0
    Y = 1
    Z = 2


class STL2Minecraft:
    debug_enable = False

    def convert_stl_to_points(self, input_file):
        your_mesh = mesh.Mesh.from_file(input_file)
        all_points = []
        for vector in your_mesh.vectors:
            points = self.create_surface(vector)
            if self.debug_enable:
                self.plot_surface(points, "o")
            for point in points:
                all_points.append(point)
        if self.debug_enable:
            self.plot_surface(all_points, "o")
        return all_points

    def create_surface(self, triangle):
        [p1, p2, p3] = triangle
        self.debug_print(f"{p1}->{p2}->{p3}")
        points = self.connect_points(p1,p2)
        final_points = []
        for point in points:
            final_points.append(point)
        self.debug_print(f"First Line: ...{final_points}...")
        for point in points:
            if self.points_are_different(p3, point):
                to_p3_points = self.connect_points(point, p3)
                self.debug_print(to_p3_points)
                for final_point in to_p3_points:
                    if final_point not in final_points:
                        final_points.append(final_point)
        return final_points

    def connect_points(self, p1, p2):
        most_delta_dimension = self.dimension_with_most_delta(p1, p2)
        points = self.connect_points_helper(self.adjust_for_most_delta_dimension(p1, most_delta_dimension), self.adjust_for_most_delta_dimension(p2, most_delta_dimension))
        return self.swap_x_with_dimension(points, most_delta_dimension)

    @staticmethod
    def connect_points_helper(p1, p2):
        points = []
        [x1, y1, z1] = p1
        [x2, y2, z2] = p2
        if x1 == x2:
            points.append(p1)
            points.append(p2)
            return points
        max_x = max(int(x1), int(x2))
        min_x = min(int(x1), int(x2))
        y_x_slope = (y2-y1)/(x2-x1)
        z_x_slope = (z2-z1)/(x2-x1)
        i = 0
        for x in range(min_x, max_x+1):
            if x1 < x2:
                y = round(y1 + i*y_x_slope)
                z = round(z1 + i*z_x_slope)
            else:
                y = round(y2 + i*y_x_slope)
                z = round(z2 + i*z_x_slope)
            point = [x, y, z]
            points.append(point)
            i = i + 1
        return points

    def dimension_with_most_delta(self, p1, p2):
        [x1, y1, z1] = p1
        [x2, y2, z2] = p2
        x_dim = abs(x1 - x2)
        y_dim = abs(y1 - y2)
        z_dim = abs(z1 - z2)
        if (x_dim > y_dim) and (x_dim > z_dim):
            return Dimension.X
        if y_dim > z_dim:
            return Dimension.Y
        return Dimension.Z

    @staticmethod
    def adjust_for_most_delta_dimension(pt, dimension):
        [x, y, z] = pt
        if dimension == Dimension.X:
            pt_alt = pt
        if dimension == Dimension.Y:
            pt_alt = [y, x, z]
        if dimension == Dimension.Z:
            pt_alt = [z, y, x]
        return pt_alt

    @staticmethod
    def swap_x_with_dimension(points, dimension):
        adjusted_points = []
        for point in points:
            [x, y, z] = point
            final_point = point
            if dimension == Dimension.Y:
                final_point = [y, x, z]
            elif dimension == Dimension.Z:
                final_point = [z, y, x]
            adjusted_points.append(final_point)
        return adjusted_points

    @staticmethod
    def points_are_different(p1, p2):
        [x1, y1, z1] = p1
        [x2, y2, z2] = p2
        if (x1 == x2) and (y1 == y2) and (z1 == z2):
            return False
        return True

    @staticmethod
    def plot_surface(points, marker):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        xs, ys, zs = [], [], []
        for point in points:
            [x, y, z] = point
            xs.append(x)
            ys.append(y)
            zs.append(z)
        ax.scatter(xs, ys, zs, marker=marker)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_zlabel('Z')
        plt.show()

    def points_to_minecraft_function(self, points, texture, output_file):
        f = open(output_file, 'w')
        sys.stdout = f
        for point in points:
            [x, y, z] = point
            print(f"fill {x} {y} {z} {x} {y} {z} {texture}")
        f.close()

    def move_all_points(self, points, offset):
        [x_offset, y_offset, z_offset] = offset
        adjusted_points = []
        for point in points:
            [x, y, z] = point
            new_point = [x+x_offset, y+y_offset, z+z_offset]
            adjusted_points.append(new_point)
        return adjusted_points

    def debug_print(self, msg):
        if self.debug_enable:
            print(msg)

class TestMethods(unittest.TestCase):
    stl_2_minecraft = STL2Minecraft()

    def test_points_are_different(self):
        p1 = [0, 1, 2]
        p2 = [0, 1, 3]
        self.assertTrue(self.stl_2_minecraft.points_are_different(p1, p2))
        self.assertFalse(self.stl_2_minecraft.points_are_different(p1, p1))

    def test_dimension_with_most_delta(self):
        p1 = [10, 30, 60]
        p2 = [11, 33, 66]
        p3 = [15, 29, 61]
        p4 = [11, -25, 60]
        self.assertEqual(self.stl_2_minecraft.dimension_with_most_delta(p1, p2), Dimension.Z)
        self.assertEqual(self.stl_2_minecraft.dimension_with_most_delta(p1, p3), Dimension.X)
        self.assertEqual(self.stl_2_minecraft.dimension_with_most_delta(p1, p4), Dimension.Y)

    def connect_points_checker(self, points, expected_points):
        for point in points:
            self.assertIn(point, expected_points)
        for point in expected_points:
            self.assertIn(point, points)

    def test_connect_points_one_dim(self):
        self.connect_points_checker(self.stl_2_minecraft.connect_points([0, 0, 0], [0, 2, 0]),
                                    [[0, 0, 0], [0, 1, 0], [0, 2, 0]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points([0, 2, 0], [0, 0, 0]),
                                    [[0, 0, 0], [0, 1, 0], [0, 2, 0]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points([0, 0, 0], [0, 0, 2]),
                                    [[0, 0, 0], [0, 0, 1], [0, 0, 2]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points([0, 0, 2], [0, 0, 0]),
                                    [[0, 0, 0], [0, 0, 1], [0, 0, 2]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points([0, 0, 0], [2, 0, 0]),
                                    [[0, 0, 0], [1, 0, 0], [2, 0, 0]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points([2, 0, 0], [0, 0, 0]),
                                    [[0, 0, 0], [1, 0, 0], [2, 0, 0]])

    def test_connect_points_two_dim(self):
        self.connect_points_checker(self.stl_2_minecraft.connect_points([0, 0, 0], [0, 2, 2]),
                                    [[0, 0, 0], [0, 1, 1], [0, 2, 2]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points([0, 2, 2], [0, 0, 0]),
                                    [[0, 0, 0], [0, 1, 1], [0, 2, 2]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points([2, 0, 2], [0, 0, 0]),
                                    [[0, 0, 0], [1, 0, 1], [2, 0, 2]])

    def test_connect_points_helper_one_dim(self):
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([0, 0, 0], [2, 0, 0]),
                                    [[0, 0, 0], [1, 0, 0], [2, 0, 0]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([2, 0, 0], [0, 0, 0]),
                                    [[0, 0, 0], [1, 0, 0], [2, 0, 0]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([0, 0, 0], [-2, 0, 0]),
                                    [[0, 0, 0], [-1, 0, 0], [-2, 0, 0]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([-2, 0, 0], [0, 0, 0]),
                                    [[0, 0, 0], [-1, 0, 0], [-2, 0, 0]])

    def test_connect_points_helper_x_same(self):
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([0, 0, 0], [0, 2, 0]),
                                    [[0, 0, 0], [0, 2, 0]])

    def test_connect_points_helper_two_dim(self):
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([0, 0, 0], [2, 2, 0]),
                                    [[0, 0, 0], [1, 1, 0], [2, 2, 0]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([2, 2, 0], [0, 0, 0]),
                                    [[0, 0, 0], [1, 1, 0],[2, 2, 0]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([2, 0, 2], [0, 0, 0]),
                                    [[0, 0, 0], [1, 0, 1], [2, 0, 2]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([0, 0, 0], [-2, -2, 0]),
                                    [[0, 0, 0], [-1, -1, 0], [-2, -2, 0]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([-2, -2, 0], [0, 0, 0]),
                                    [[0, 0, 0], [-1, -1, 0], [-2, -2, 0]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([-2, 0, -2], [0, 0, 0]),
                                    [[0, 0, 0], [-1, 0, -1], [-2, 0, -2]])

    def test_connect_points_helper_three_dim(self):
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([0, 0, 0], [2, 2, 2]),
                                    [[0, 0, 0], [1, 1, 1], [2, 2, 2]])
        self.connect_points_checker(self.stl_2_minecraft.connect_points_helper([2, 2, 2], [0, 0, 0]),
                                    [[0, 0, 0], [1, 1, 1], [2, 2, 2]])

    def test_move_all_points(self):
        self.assertEqual(self.stl_2_minecraft.move_all_points([[-1, -2, -3]], [3, 2, 1]), [[2, 0, -2]])

texture = "minecraft:oak_planks"
input_file = r'C:\Users\erika\pyramid.stl'
output_file = r'C:\Users\erika\AppData\Roaming\.minecraft\saves\Python Test\datapacks\Creative Utilities\data\esamuelson\functions\crea-util\pyramid.mcfunction'

stl_2_minecraft = STL2Minecraft()
points = stl_2_minecraft.move_all_points(stl_2_minecraft.convert_stl_to_points(input_file), [0, 100, 0])
stl_2_minecraft.plot_surface(points, ".")
stl_2_minecraft.points_to_minecraft_function(points, texture, output_file)

if __name__ == '__main__':
    unittest.main()




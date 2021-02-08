import numpy
import stl
from stl import mesh
from mpl_toolkits import mplot3d
from matplotlib import pyplot
import sys
import matplotlib.pyplot as plt
import unittest


class STL2Minecraft:
    texture = "minecraft:oak_planks"
    input_file = 'C:\\Users\\erika\\pyramid.stl'
    #output_file = f"{input_file}.function"
    output_file = r'C:\Users\erika\AppData\Roaming\.minecraft\saves\Python Test\datapacks\Creative Utilities\data\esamuelson\functions\crea-util\pyramid.mcfunction'
    y_offset = 100
    debug_enable = False

    def dimension_with_most_delta(self, p1, p2):
        [x1, y1, z1] = p1
        [x2, y2, z2] = p2
        x_dim = abs(x1 - x2)
        y_dim = abs(y1 - y2)
        z_dim = abs(z1 - z2)
        if (x_dim > y_dim) and (x_dim > z_dim):
            return "x"
        if (y_dim > z_dim):
            return "y"
        return "z"

    @staticmethod
    def adjust_for_most_delta_dimension(pt, most_delta_dimension):
        [x, y, z] = pt
        if most_delta_dimension == "x":
            pt_alt = pt
        if most_delta_dimension == "y":
            pt_alt = [y, x, z]
        if most_delta_dimension == "z":
            pt_alt = [z, y, x]
        return pt_alt

    @staticmethod
    def get_swap_flags(most_delta_dimension):
        (swap_xy, swap_xz) = False, False
        if most_delta_dimension == "y":
            swap_xy = True
        if most_delta_dimension == "z":
            swap_xz = True
        return swap_xy, swap_xz

    def connect_points(self, p1, p2):
        most_delta_dimension = self.dimension_with_most_delta(p1, p2)
        final_points = []
        (swap_xy, swap_xz) = self.get_swap_flags(most_delta_dimension)
        p1_alt = self.adjust_for_most_delta_dimension(p1, most_delta_dimension)
        p2_alt = self.adjust_for_most_delta_dimension(p2, most_delta_dimension)
        points = self.connect_points_helper(p1_alt, p2_alt)
        for point in points:
            [x, y, z] = point
            final_point = point
            if swap_xy:
                final_point = [y, x, z]
            elif swap_xz:
                final_point = [z, y, x]
            final_points.append(final_point)
        return final_points

    @staticmethod
    def print_point(point):
        [x, y, z] = point
        print(f"X{x} Y{y} Z{z}")

    def connect_points_helper(self, p1, p2):
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
        self.debug_print(f"x in range {min_x}, {max_x}")
        i = 0
        for x in range(min_x, max_x+1):
            self.debug_print(f"x{x}, {y_x_slope}, {z_x_slope}")
            if x1 < x2:
                y = round(y1 + i*y_x_slope)
                z = round(z1 + i*z_x_slope)
            else:
                y = round(y2 + i*y_x_slope)
                z = round(z2 + i*z_x_slope)
            point = [x, y, z]
            self.debug_print(point)
            points.append(point)
            i = i + 1
        return points

    @staticmethod
    def points_are_different(p1, p2):
        [x1, y1, z1] = p1
        [x2, y2, z2] = p2
        if (x1 == x2) and (y1 == y2) and (z1 == z2):
            return False
        return True

    def debug_print(self, msg):
        if self.debug_enable:
            print(msg)

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

    @staticmethod
    def plot_surface(points, marker):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        xs = []
        ys = []
        zs = []
        for point in points:
            [x, y, z] = point
            xs.append(x)
            ys.append(y)
            zs.append(z)
        ax.scatter(xs, ys, zs, marker=marker)
        ax.set_xlabel('X Label')
        ax.set_ylabel('Y Label')
        ax.set_zlabel('Z Label')
        plt.show()

    def test_helper(self, triangle):
        points = self.create_surface(triangle)
        self.plot_surface(points, "o")

    def print_from_stl(self):
        your_mesh = mesh.Mesh.from_file(self.input_file)

        f = open(self.output_file, 'w')
        sys.stdout = f  # Change the standard output to the file we created.

        all_points = []
        for vector in your_mesh.vectors:
            points = self.create_surface(vector)
            self.plot_surface(points, "o")
            for point in points:
                all_points.append(point)
        self.plot_surface(all_points, "o")
        f.close()

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
        self.assertEqual(self.stl_2_minecraft.dimension_with_most_delta(p1, p2), "z")
        self.assertEqual(self.stl_2_minecraft.dimension_with_most_delta(p1, p3), "x")
        self.assertEqual(self.stl_2_minecraft.dimension_with_most_delta(p1, p4), "y")

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

#        self.stl_2_minecraft.debug_enable = True

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

    def test_large(self):
        self.stl_2_minecraft.test_helper([[-30., -10., 20.], [-20., -20., 0.], [-20., 0., 0.]])

    def test_pyramid(self):
        self.stl_2_minecraft.print_from_stl()

#    def test1():
#        test_helper([[0,0,0],[10,0,0],[10,10,0]])
        # test_helper([[10,10,0],[10,0,0],[0,0,0]])
        # test_helper([[10,10,0],[0,0,0],[10,0,0]])


#    def test2():
#        test_helper([[-40.0, -20.0, 0.], [-20., -20., 0.], [-30., -10., 20.]])

#    def test3():
#        test_helper([[-20., 0., 0.], [-20., -20., 0.], [-40., -20., 0.]])


if __name__ == '__main__':
    unittest.main()


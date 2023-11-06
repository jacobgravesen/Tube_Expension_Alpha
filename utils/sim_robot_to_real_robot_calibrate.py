import math

"""This script first defines two functions: calculate_rotation_angle and rotate_point. The calculate_rotation_angle function calculates the rotation angle between two points in different coordinate systems. The rotate_point function rotates a point around the Z-axis by a certain angle.

Then, the script calculates the rotation angle between a point in the robot's coordinate system and the same point in the simulation's coordinate system. It prints the rotation angle.

Finally, the script demonstrates how to use the rotation angle to rotate a point before sending it to the robot. It prints the rotated point.

Please replace point_robot and point_simulation with your actual points. Also, replace point with the point you want to rotate."""

def calculate_rotation_angle(point_robot, point_simulation):
    """
    Calculate the rotation angle between two points in different coordinate systems.

    Args:
    point_robot (list): The [x, y] coordinates of the point in the robot's coordinate system.
    point_simulation (list): The [x, y] coordinates of the point in the simulation's coordinate system.

    Returns:
    float: The rotation angle in degrees.
    """
    # Translate points to origin
    dx_robot, dy_robot = point_robot[0] - point_robot[0], point_robot[1] - point_robot[1]
    dx_sim, dy_sim = point_simulation[0] - point_robot[0], point_simulation[1] - point_robot[1]

    # Calculate angle
    angle_robot = math.atan2(dy_robot, dx_robot)
    angle_sim = math.atan2(dy_sim, dx_sim)

    # Calculate relative rotation angle
    rotation_angle = math.degrees(angle_sim - angle_robot)

    return rotation_angle

def rotate_point(point, angle_degrees):
    """
    Rotate a point around the Z-axis by a certain angle.

    Args:
    point (list): The [x, y, z] coordinates of the point.
    angle_degrees (float): The rotation angle in degrees.

    Returns:
    list: The rotated [x, y, z] coordinates of the point.
    """
    angle_radians = math.radians(angle_degrees)
    x, y = point[0], point[1]
    x_new = x * math.cos(angle_radians) - y * math.sin(angle_radians)
    y_new = x * math.sin(angle_radians) + y * math.cos(angle_radians)
    return [x_new, y_new, point[2]]  # Assuming point[2] is the Z coordinate

# Replace these with your actual points
point_robot = [356.31, 0.56]
point_simulation = [354.944, -0.375]

# Calculate the rotation angle
rotation_angle = calculate_rotation_angle(point_robot, point_simulation)
print(f"The rotation angle is {rotation_angle} degrees.")

# Now you can use the rotation angle to rotate your points before sending them to the robot
point = [272.29, -507.15, -61.27]
rotated_point = rotate_point(point, rotation_angle)
print(f"The rotated point is {rotated_point}.")
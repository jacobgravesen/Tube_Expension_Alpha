from robolink import Robolink, Item, ROBOTCOM_READY, RUNMODE_RUN_ROBOT

class TestMove:
    def __init__(self):
        self.robodk = Robolink()
        self.robot = self.robodk.Item('UR5')

        # Connect to the robot using default IP
        success = self.robot.Connect()  # Try to connect once
        # success = self.robot.ConnectSafe() # Try to connect multiple times
        status, status_msg = self.robot.ConnectedState()
        if status != ROBOTCOM_READY:
            # Stop if the connection did not succeed
            print(status_msg)
            raise Exception("Failed to connect: " + status_msg)

        # This will set to run the API programs on the robot and the simulator (online programming)
        self.robodk.setRunMode(RUNMODE_RUN_ROBOT)


    def move_wrist(self, angle=20, speed=10):
        # Get the current joint positions
        joints = self.robot.Joints().list()

        # Add the angle to the wrist joint (joint 4)
        joints[4] += angle
        self.robot.setSpeed(speed)
        self.robot.MoveJ(joints)

        # Subtract the angle from the wrist joint
        joints[4] -= 2 * angle
        self.robot.MoveJ(joints)

        # Return to the original position
        joints[4] += angle
        self.robot.MoveJ(joints)

if __name__ == "__main__":
    test_move = TestMove()
    test_move.move_wrist()
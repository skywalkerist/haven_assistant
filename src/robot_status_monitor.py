import socket
import json
import time

class RobotInfo:
    """
    A class to connect to the robot and retrieve its status information.
    """
    def __init__(self, host='192.168.10.10', port=31001):
        """
        Initializes the RobotInfo object.

        Args:
            host (str): The IP address of the robot.
            port (int): The port for the robot's API server.
        """
        self.host = host
        self.port = port
        self.sock = None
        self.battery_level = None
        self.position = None
        self.is_charging = None
        self.destination = None

    def connect(self):
        """Establishes a TCP connection to the robot."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(5)  # 5 second timeout
            self.sock.connect((self.host, self.port))
            print(f"Successfully connected to {self.host}:{self.port}")
            return True
        except socket.error as e:
            print(f"Failed to connect to {self.host}:{self.port}. Error: {e}")
            self.sock = None
            return False

    def disconnect(self):
        """Closes the TCP connection."""
        if self.sock:
            self.sock.close()
            self.sock = None
            print("Disconnected from the robot.")

    def get_status(self):
        """Sends the status request command and updates the robot's info."""
        if not self.sock:
            print("Not connected to the robot. Please connect first.")
            return False

        try:
            command = "/api/robot_status\n"  # Add newline as terminator
            self.sock.sendall(command.encode('utf-8'))
            
            # Keep receiving data until a complete JSON object is formed
            response_data = ""
            while True:
                try:
                    chunk = self.sock.recv(4096).decode('utf-8')
                    if not chunk:
                        # Connection closed prematurely
                        break
                    response_data += chunk
                    # Try to parse the accumulated data
                    try:
                        response_json = json.loads(response_data)
                        # If parsing succeeds, we have a complete JSON object
                        self._parse_status_response(response_json)
                        return True
                    except json.JSONDecodeError:
                        # Incomplete data, continue receiving
                        continue
                except socket.timeout:
                    print("Socket timed out while waiting for response.")
                    return False

            print("Failed to receive a complete JSON response.")
            return False

        except socket.error as e:
            print(f"An error occurred while getting status: {e}")
            return False

    def _parse_status_response(self, response):
        """Parses the JSON response from the robot."""
        if response.get("status") == "OK":
            results = response.get("results", {})
            self.battery_level = results.get("power_percent")
            self.is_charging = results.get("charge_state")
            self.position = results.get("current_pose")
            self.destination = results.get("move_target")
            print("Successfully updated robot status.")
        else:
            error_msg = response.get("error_message", "Unknown error")
            print(f"Failed to get robot status. Error: {error_msg}")

    def display_info(self):
        """Prints the current robot information."""
        print("\n--- Robot Status ---")
        print(f"Battery Level: {self.battery_level}%")
        print(f"Is Charging: {'Yes' if self.is_charging else 'No'}")
        if self.position:
            print(f"Position: X={self.position.get('x')}, Y={self.position.get('y')}, Theta={self.position.get('theta')}")
        else:
            print("Position: Not available")
        
        if self.destination:
             print(f"Destination: {self.destination}")
        else:
             print("Destination: Not currently moving to a named target.")
        print("--------------------\n")


def main():
    """Main function to test the RobotInfo class."""
    # NOTE: This script assumes it can connect to the robot at the specified IP.
    # For testing purposes without a real robot, the connect() call will fail.
    # The code is structured to handle this gracefully.
    
    robot_info = RobotInfo()
    
    print("Attempting to connect to the robot...")
    if robot_info.connect():
        print("Fetching robot status...")
        if robot_info.get_status():
            robot_info.display_info()
        else:
            print("Could not retrieve robot status.")
        
        robot_info.disconnect()
    else:
        print("Could not connect to the robot. The script will now exit.")
        print("This is expected if you are not on the same network as the robot.")


if __name__ == '__main__':
    main()

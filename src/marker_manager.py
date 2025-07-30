import socket
import json
import time

class MarkerManager:
    """
    A class to manage the robot's markers.
    """
    def __init__(self, host='192.168.10.10', port=31001):
        """
        Initializes the MarkerManager object.

        Args:
            host (str): The IP address of the robot.
            port (int): The port for the robot's API server.
        """
        self.host = host
        self.port = port
        self.sock = None

    def connect(self):
        """Establishes a TCP connection to the robot."""
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(10)  # 10 second timeout
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

    def _send_command(self, command):
        """
        Sends a command to the robot, waits for a matching response, 
        and ignores other notifications.
        """
        if not self.sock:
            print("Not connected to the robot. Please connect first.")
            return None

        try:
            base_command = command.split('?')[0]
            full_command = command + "\n"
            self.sock.sendall(full_command.encode('utf-8'))
            
            buffer = ""
            while True:
                try:
                    chunk = self.sock.recv(4096).decode('utf-8')
                    if not chunk:
                        print("Connection closed by server.")
                        return None
                    buffer += chunk
                    
                    # Process buffer for complete JSON objects
                    while True:
                        try:
                            response_json, index = json.JSONDecoder().raw_decode(buffer)
                            buffer = buffer[index:].lstrip() # Remove processed part and leading whitespace

                            # Check if it's the response we are looking for
                            if response_json.get("type") == "response" and response_json.get("command") == base_command:
                                return response_json
                            # Ignore notifications and other responses
                            else:
                                print(f"Ignoring message: {response_json}")
                                continue
                        except json.JSONDecodeError:
                            # Not a full JSON object yet, break inner loop to get more data
                            break

                except socket.timeout:
                    print("Socket timed out while waiting for response.")
                    return None
        except socket.error as e:
            print(f"An error occurred: {e}")
            return None

    def insert_marker_at_current_pos(self, name, marker_type=0, num=1):
        """
        Marks a marker at the robot's current position.
        Expected response:
        {
            "type": "response",
            "command": "/api/markers/insert",
            "status": "OK" or "INVALID_REQUEST",
            "error_message": ""
        }
        """
        command = f"/api/markers/insert?name={name}&type={marker_type}&num={num}"
        return self._send_command(command)

    def get_marker_list(self, floor=None):
        """
        Gets the list of markers.
        Expected response:
        {
            "type": "response",
            "command": "/api/markers/query_list",
            "status": "OK",
            "results": {
                "marker_name_1": { ...details... },
                "marker_name_2": { ...details... }
            }
        }
        """
        command = "/api/markers/query_list"
        if floor is not None:
            command += f"?floor={floor}"
        return self._send_command(command)

    def delete_marker(self, name):
        """
        Deletes a specified marker.
        Expected response:
        {
            "type": "response",
            "command": "/api/markers/delete",
            "status": "OK" or "INVALID_REQUEST",
            "error_message": "" or "Marker Not Found"
        }
        """
        command = f"/api/markers/delete?name={name}"
        return self._send_command(command)

    def get_marker_count(self):
        """
        Gets the number of markers.
        Expected response:
        {
            "type": "response",
            "command": "/api/markers/count",
            "status": "OK",
            "results": {
                "count": 2
            }
        }
        """
        command = "/api/markers/count"
        return self._send_command(command)

    def get_marker_brief(self):
        """
        Gets a brief summary of markers.
        Expected response:
        {
            "type": "response",
            "command": "/api/markers/query_brief",
            "status": "OK",
            "results": {
                "marker_name_1": "type-floor",
                "marker_name_2": "type-floor"
            }
        }
        """
        command = "/api/markers/query_brief"
        return self._send_command(command)

    def insert_marker_by_pose(self, name, x, y, theta, floor, marker_type=0, num=1):
        """
        Marks a marker at a specified pose.
        Expected response:
        {
            "type": "response",
            "command": "/api/markers/insert_by_pose",
            "status": "OK" or "INVALID_REQUEST",
            "error_message": ""
        }
        """
        command = f"/api/markers/insert_by_pose?name={name}&x={x}&y={y}&theta={theta}&floor={floor}&type={marker_type}&num={num}"
        return self._send_command(command)

def main():
    """Main function to test the MarkerManager class."""
    manager = MarkerManager()

    if not manager.connect():
        print("Could not connect to the robot. Exiting.")
        return

    while True:
        print("\n--- Marker Management ---")
        print("1. Mark marker at current position")
        print("2. Get marker list")
        print("3. Delete a marker")
        print("4. Get marker count")
        print("5. Get marker brief")
        print("6. Mark marker at specified pose")
        print("0. Exit")
        
        choice = input("Enter your choice (0-6): ")

        if choice == '1':
            name = input("Enter marker name: ")
            m_type = input("Enter marker type (default 0): ")
            m_type = int(m_type) if m_type.isdigit() else 0
            response = manager.insert_marker_at_current_pos(name, m_type)
            print("Response:", json.dumps(response, indent=4))

        elif choice == '2':
            floor = input("Enter floor to query (optional): ")
            floor = int(floor) if floor.isdigit() else None
            response = manager.get_marker_list(floor)
            print("Response:", json.dumps(response, indent=4))

        elif choice == '3':
            name = input("Enter marker name to delete: ")
            if name:
                response = manager.delete_marker(name)
                print("Response:", json.dumps(response, indent=4))
            else:
                print("Marker name cannot be empty.")

        elif choice == '4':
            response = manager.get_marker_count()
            print("Response:", json.dumps(response, indent=4))

        elif choice == '5':
            response = manager.get_marker_brief()
            print("Response:", json.dumps(response, indent=4))

        elif choice == '6':
            name = input("Enter marker name: ")
            x = float(input("Enter X coordinate: "))
            y = float(input("Enter Y coordinate: "))
            theta = float(input("Enter Theta (angle in radians): "))
            floor = int(input("Enter floor number: "))
            m_type = input("Enter marker type (default 0): ")
            m_type = int(m_type) if m_type.isdigit() else 0
            response = manager.insert_marker_by_pose(name, x, y, theta, floor, m_type)
            print("Response:", json.dumps(response, indent=4))
            
        elif choice == '0':
            break
        else:
            print("Invalid choice. Please try again.")

    manager.disconnect()

if __name__ == '__main__':
    main()

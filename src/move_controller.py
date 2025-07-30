import socket
import json
import time
import math

class MoveController:
    """
    A class to control the robot's movement, including navigation to markers,
    patrolling, and direct velocity-based control.
    """
    def __init__(self, host='192.168.10.10', port=31001):
        """
        Initializes the MoveController object.

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
            self.sock.settimeout(10)
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

    def _send_command(self, command, wait_for_response=True):
        """
        Sends a command to the robot.

        Args:
            command (str): The command string to send.
            wait_for_response (bool): If True, waits for a matching response. 
                                      If False, sends the command and returns immediately.
        """
        if not self.sock:
            print("Not connected to the robot. Please connect first.")
            return None

        try:
            base_command = command.split('?')[0]
            full_command = command + "\n"
            self.sock.sendall(full_command.encode('utf-8'))

            if not wait_for_response:
                return {"status": "OK", "info": "Command sent without waiting for response."}

            buffer = ""
            while True:
                try:
                    chunk = self.sock.recv(4096).decode('utf-8')
                    if not chunk:
                        print("Connection closed by server.")
                        return None
                    buffer += chunk
                    
                    while True:
                        try:
                            response_json, index = json.JSONDecoder().raw_decode(buffer)
                            buffer = buffer[index:].lstrip()

                            if response_json.get("type") == "response" and response_json.get("command") == base_command:
                                return response_json
                            else:
                                # Ignore other notifications or callbacks
                                pass
                        except json.JSONDecodeError:
                            break
                except socket.timeout:
                    print("Socket timed out while waiting for response.")
                    return None
        except socket.error as e:
            print(f"An error occurred: {e}")
            return None

    # --- Marker-based Navigation ---

    def get_robot_status(self):
        """
        Retrieves the current status of the robot.

        Returns:
            dict: The JSON response containing the robot's status, or None on failure.
        """
        command = "/api/robot_status"
        # Use a dedicated _send_command call that can handle various message types
        return self._send_command(command)

    def wait_for_move_completion(self, timeout=60):
        """
        等待移动完成，通过轮询机器人状态来判断
        
        Args:
            timeout (int): 等待超时时间（秒）
            
        Returns:
            bool: 移动是否成功完成
        """
        start_time = time.time()
        print("🔄 开始等待移动完成...")
        
        # 先等待一小段时间让机器人开始移动
        time.sleep(1)
        
        consecutive_idle_count = 0  # 连续空闲状态计数
        required_idle_count = 3     # 需要连续N次空闲状态才认为完成
        
        while time.time() - start_time < timeout:
            status_response = self.get_robot_status()
            
            if status_response and status_response.get('status') == 'OK':
                results = status_response.get('results', {})
                move_status = results.get('move_status')
                
                print(f"DEBUG: 当前移动状态: {move_status}")
                
                # 检查各种状态
                if move_status in ['succeeded', 'success', 'completed', 'finished']:
                    print("✅ 移动任务成功完成")
                    return True
                elif move_status in ['failed', 'canceled', 'error']:
                    print(f"❌ 移动任务失败: {move_status}")
                    return False
                elif move_status in ['running', 'moving', 'executing']:
                    print("🔄 机器人移动中...")
                    consecutive_idle_count = 0  # 重置空闲计数
                elif move_status in ['idle', 'ready']:
                    consecutive_idle_count += 1
                    print(f"🔄 机器人空闲状态 ({consecutive_idle_count}/{required_idle_count})")
                    
                    # 连续多次空闲状态，认为移动已完成
                    if consecutive_idle_count >= required_idle_count:
                        print("✅ 检测到连续空闲状态，移动已完成")
                        return True
                else:
                    print(f"⚠️ 未知状态: {move_status}")
                    consecutive_idle_count = 0
            else:
                print("⚠️ 获取状态失败")
                consecutive_idle_count = 0
            
            time.sleep(2)  # 每2秒检查一次状态
        
        print(f"⏰ 移动等待超时 ({timeout}秒)")
        return False

    def move_to_marker(self, marker_name, angle_offset=0.0, wait=True):
        """
        Moves the robot to a specified marker.

        Args:
            marker_name (str): The name of the target marker.
            angle_offset (float): Optional angle offset in radians.
            wait (bool): If True, waits for the movement to complete.

        Returns:
            If wait is True, returns bool indicating success.
            If wait is False, returns the initial command response dict.
        """
        command = f"/api/move?marker={marker_name}&angle_offset={angle_offset}"
        initial_response = self._send_command(command)

        if not wait or not initial_response or initial_response.get('status') != 'OK':
            return initial_response

        print(f"DEBUG: 移动命令响应: {initial_response}")
        # 直接使用状态轮询等待移动完成
        return self.wait_for_move_completion()

    def patrol_markers(self, marker_list, count=-1):
        """
        Makes the robot patrol a list of markers.

        Args:
            marker_list (list): A list of marker names to patrol.
            count (int): The number of patrol cycles. -1 for infinite loop.

        Returns:
            dict: The JSON response from the robot.
        """
        if not isinstance(marker_list, list) or len(marker_list) < 2:
            raise ValueError("marker_list must be a list of at least two marker names.")
        markers_str = ",".join(marker_list)
        command = f"/api/move?markers={markers_str}&count={count}"
        return self._send_command(command)

    def cancel_move(self):
        """
        Cancels the current movement task.

        Returns:
            dict: The JSON response from the robot.
        """
        command = "/api/move/cancel"
        return self._send_command(command)

    # --- Direct Velocity Control ---

    def _execute_joy_control(self, linear_velocity=0.0, angular_velocity=0.0):
        """
        Sends a single, low-level velocity command.

        Args:
            linear_velocity (float): Linear speed in m/s. Positive for forward.
            angular_velocity (float): Angular speed in rad/s. Positive for left turn.
        """
        command = f"/api/joy_control?linear_velocity={linear_velocity}&angular_velocity={angular_velocity}"
        # For joy_control, we send commands rapidly and don't need to wait for each response.
        self._send_command(command, wait_for_response=False)

    def move_linear_for_distance(self, distance, speed=0.2):
        """
        Moves the robot forward or backward for a specific distance.

        Args:
            distance (float): The distance to move in meters. Positive for forward, negative for backward.
            speed (float): The absolute speed in m/s. Defaults to 0.2.
        """
        if speed <= 0:
            print("Speed must be positive.")
            return
        
        duration = abs(distance) / speed
        direction_speed = speed if distance > 0 else -speed
        
        print(f"Moving {'forward' if distance > 0 else 'backward'} for {abs(distance):.2f}m at {speed} m/s (duration: {duration:.2f}s)...")
        
        start_time = time.time()
        while time.time() - start_time < duration:
            self._execute_joy_control(linear_velocity=direction_speed)
            time.sleep(0.1) # Send command every 100ms
            
        self._execute_joy_control(linear_velocity=0.0) # Stop the robot
        print("Movement finished.")

    def move_angular_for_angle(self, angle, speed=0.5):
        """
        Rotates the robot left or right for a specific angle.

        Args:
            angle (float): The angle to rotate in degrees. Positive for left, negative for right.
            speed (float): The absolute angular speed in rad/s. Defaults to 0.5.
        """
        if speed <= 0:
            print("Speed must be positive.")
            return
            
        angle_rad = math.radians(angle)
        duration = abs(angle_rad) / speed
        direction_speed = speed if angle > 0 else -speed

        print(f"Rotating {'left' if angle > 0 else 'right'} for {abs(angle):.2f} degrees at {speed} rad/s (duration: {duration:.2f}s)...")

        start_time = time.time()
        while time.time() - start_time < duration:
            self._execute_joy_control(angular_velocity=direction_speed)
            time.sleep(0.1) # Send command every 100ms

        self._execute_joy_control(angular_velocity=0.0) # Stop the robot
        print("Rotation finished.")


def main():
    """Main function to test the MoveController class."""
    controller = MoveController()

    if not controller.connect():
        print("Could not connect to the robot. Exiting.")
        return

    print("\n--- Robot Move Controller ---")
    print("Enter command and value (e.g., 'w 1.5', 'a 90', 's 1', 'd 45').")
    print("  'w <dist>' - Move forward <dist> meters.")
    print("  's <dist>' - Move backward <dist> meters.")
    print("  'a <angle>' - Rotate left <angle> degrees.")
    print("  'd <angle>' - Rotate right <angle> degrees.")
    print("  'm <marker>' - Move to marker.")
    print("  'p <m1,m2,..>' - Patrol markers.")
    print("  'c' - Cancel current move.")
    print("  'q' - Quit.")
    
    while True:
        try:
            user_input = input("\nEnter command: ").strip().lower()
            if not user_input:
                continue

            parts = user_input.split()
            command = parts[0]
            
            if command == 'q':
                break
            
            elif command == 'c':
                print("Cancelling movement...")
                response = controller.cancel_move()
                print("Response:", json.dumps(response, indent=4))

            elif command in ['w', 's', 'a', 'd']:
                if len(parts) < 2:
                    print("Missing value. Example: 'w 1.5'")
                    continue
                
                try:
                    value = float(parts[1])
                except ValueError:
                    print("Invalid value. Must be a number.")
                    continue

                if command == 'w':
                    controller.move_linear_for_distance(value)
                elif command == 's':
                    controller.move_linear_for_distance(-value)
                elif command == 'a':
                    controller.move_angular_for_angle(value)
                elif command == 'd':
                    controller.move_angular_for_angle(-value)

            elif command == 'm':
                if len(parts) < 2:
                    print("Missing marker name. Example: 'm marker1'")
                    continue
                marker = parts[1]
                print(f"Moving to marker: {marker} and waiting for completion...")
                success = controller.move_to_marker(marker, wait=True)
                if success:
                    print(f"Successfully arrived at {marker}.")
                else:
                    print(f"Failed to arrive at {marker}.")

            elif command == 'p':
                if len(parts) < 2:
                    print("Missing marker list. Example: 'p m1,m2,m3'")
                    continue
                markers = parts[1].split(',')
                print(f"Patrolling markers: {markers}...")
                response = controller.patrol_markers(markers)
                print("Response:", json.dumps(response, indent=4))

            else:
                print("Invalid command. Use 'w', 's', 'a', 'd', 'm', 'p', 'c', or 'q'.")

        except (KeyboardInterrupt, EOFError):
            break
        except Exception as e:
            print(f"An error occurred in the main loop: {e}")

    controller.disconnect()
    print("Program terminated.")

if __name__ == '__main__':
    main()

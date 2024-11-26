import paramiko
import sys

class PowerShellRemoteSession:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.client = None

    def connect(self):
        """Establish an SSH connection to the remote host."""
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            self.client.connect(self.host, port=self.port, username=self.username, password=self.password)
            print(f"Connected to {self.host}")
        except Exception as e:
            print(f"Error connecting to {self.host}: {e}")
            return False
        return True

    def execute_powershell_command(self, command):
        """Execute a PowerShell command remotely and return the output."""
        if not self.client:
            print("No active SSH session.")
            return None

        powershell_command = f"powershell -Command \"{command}\""
        
        try:
            stdin, stdout, stderr = self.client.exec_command(powershell_command)
            
            # Read stdout and stderr to ensure we capture all output
            output = stdout.read().decode("utf-8")
            error_output = stderr.read().decode("utf-8")

            if error_output:
                print(f"Error: {error_output}")
                return None
            
            return output
        except Exception as e:
            print(f"Error executing command: {e}")
            return None

    def close_connection(self):
        """Close the SSH connection."""
        if self.client:
            self.client.close()
            print(f"Connection to {self.host} closed.")
        else:
            print("No active SSH session to close.")

# Function to ask for user input to establish a connection
def get_connection_details():
    host = input("Host (IP or domain): ")
    port = int(input("Port (default 22 for SSH): ") or 22)
    username = input("SSH Username: ")
    password = input("SSH Password: ")
    return host, port, username, password

# Main function for interactive session
def start_remote_session():
    print("PowerShell Remote Session Assistant")
    print("------------------------------------------------------------")
    
    # Get the connection details from the user
    host, port, username, password = get_connection_details()
    
    ps_session = PowerShellRemoteSession(host, port, username, password)
    
    while True:
        # Try to connect to the remote machine
        if ps_session.connect():
            break
        else:
            print("Failed to connect. Please check your connection details.")
            reconnect = input("Would you like to try again? (y/n): ").strip().lower()
            if reconnect != 'y':
                print("Exiting...")
                sys.exit(1)
    
    # Main loop to allow the user to execute commands remotely
    while True:
        command = input("\nEnter a PowerShell command to run (or type 'exit' to close): ")
        if command.lower() == 'exit':
            print("Exiting the remote session.")
            ps_session.close_connection()
            break
        
        # Execute the PowerShell command
        print(f"Executing command: {command}")
        output = ps_session.execute_powershell_command(command)

        if output:
            print(f"Output:\n{output}")
        else:
            print("No output received or command failed.")
        
        # Ask if the user wants to continue
        continue_command = input("Do you want to execute another command? (y/n): ").strip().lower()
        if continue_command != 'y':
            print("Exiting the remote session.")
            ps_session.close_connection()
            break

# Run the session
if __name__ == "__main__":
    start_remote_session()

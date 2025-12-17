import subprocess

if (ping:=subprocess.run(['ping', '8.8.8.8'], capture_output=True)).returncode != 0:
    print(ping.stderr[6:].decode())

# print(subprocess.run(['ping', '8.8.8.8']))
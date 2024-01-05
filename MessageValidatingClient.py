import sys
import socket

def main(servername, serverport, messagefilename,signaturefilename):
    
    messages =[]

    try:
        with open(messagefilename, 'r') as file:
            #for line in file:
            while True:
                length_line = file.readline()

                if not length_line:
                    break
                msg = file.read(int(length_line))
                if msg[-1] != "\n":
                    msg += "\n"
                
                msg = msg.replace('\\', '\\\\').replace('.', '\.')
                msg = (msg + "\n.\n").encode("ascii")
                #msg += "."

                messages.append(msg)
    
  
    except FileNotFoundError:
        print(f"File {messagefilename} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    signatures = []
    try:
        with open(signaturefilename, 'r') as file:
            for line in file.readlines():
                signatures.append(line.strip())
               
    except FileNotFoundError:
        print(f"File {signaturefilename} not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #s.bind((servername, int(serverport)))
        s.connect((servername, serverport))
    except ConnectionRefusedError:
        print(f"Connection to {servername}:{serverport} refused")
 
    s.send("HELLO\n".encode('ascii'))

    msg = s.recv(1024).decode().strip()
    if(msg != "260 OK"):
        print("Error")
        s.close()
        sys.exit()
    

    count = 0

    for message in messages:
        print("260 OK")
        s.send("DATA\n".encode('ascii'))
        s.send(message)
        #s.send(b" \.\r\n") 
        resp = s.recv(1024).decode().strip()

        if(resp != "270 SIG"):
            print("Error")
            s.close()
            sys.exit()
        else:
            print("270 SIG")

    

        line = s.recv(1024).decode().strip()
        #line = line.replace('\\\\', '\\').replace('\\.', '.')
        sig = signatures[count]
        
        if(line == sig):
            s.send("PASS\n".encode('ascii'))
           #print("PASS")
        else:
            s.send("FAIL\n".encode('ascii'))
            #print("FAIL")
        count += 1
        print(line)
        resp = s.recv(1024).decode().strip()
        if resp != "260 OK":
            print("did not receive 260 OK after pass/fail")
            s.close()
            sys.exit(1)   
        #send QUIT message to server
        
    s.send("QUIT\n".encode('ascii'))
    s.close()


if __name__ == "__main__":
    if len(sys.argv) != 5:
        ##print(len(sys.argv))
        print("Usage: python3 client.py <server-name> <server-port> <message-filename> <signature-filename>")
        sys.exit()
    
    ##print(len(sys.argv))

    servername, serverport, messagefilename,signaturefilename = sys.argv[1:5]
    serverport = int(serverport)
    main(servername, serverport, messagefilename,signaturefilename)
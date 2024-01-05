import socket
import sys
import hashlib

def main():

    listen_port, key_file = sys.argv[1:3]
    print(listen_port, key_file)
    keys = []
    with open(key_file, "r") as file:
        for line in file.readlines():
            keys.append(line.strip())

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", int(listen_port)))
    sock.listen()
    (conn, address) = sock.accept()
    hello_msg = conn.recv(1024).decode().strip()
    if hello_msg == "HELLO":
        #print("HELLO", end = "")
        conn.send("260 OK\n".encode('ascii'))
    else:
        print(f"{hello_msg} is not a valid HELLO message")
        sock.close()
        sys.exit(1)
    message_counter = 0
    while True:
        client_command = conn.recv(1024).decode().strip()
        match client_command:
            case "DATA":
                #print("DATA", end = "")
                msg = conn.recv(1024).decode().strip()
                msg_lines = msg.rsplit(sep="\n")

                ##maybe this
                msg_hash = hashlib.sha256()
                for line in msg_lines: #! might need to unescape message here
                    if line == ".":
                        #print("end of message")
                        break
                    #print(line)
                    ## ENCODE ASCII?
                    line = line.replace('\\.', '.').replace('\\\\', '\\')
                    msg_hash.update(line.encode('ascii'))
                #print("hashing with", keys[message_counter].encode("ASCII"))
                msg_hash.update(keys[message_counter].strip().encode('ascii'))
                #print("computing hash")
                message_counter += 1
                
                #print("sending 270 sig")
                conn.send("270 SIG\n".encode('ascii'))
                #print("sending hash", msg_hash.hexdigest())
                conn.send((msg_hash.hexdigest()+ "\n").encode('ascii'))
                
               # print(".")
                pass_or_fail = conn.recv(1024).decode().strip()
                if pass_or_fail != "PASS" and pass_or_fail != "FAIL":
                    #print("invalid: did not recieve pass/fail")
                    sock.close()
                    sys.exit(1)
                #print("recieved pass/fail, sending 260 OK")
                if pass_or_fail == "PASS":
                    print("Test Result: PASS")
                if pass_or_fail == "FAIL":
                    print("Test Result: FAIL")
                conn.send("260 OK\n".encode('ascii'))

                
            case "QUIT":
                print("QUIT")
                sock.close()
                sys.exit(0)
            case _:
                print(f"recieved invalid cmd: {client_command}")
                sock.close()
                sys.exit(1)



if __name__== "__main__":
    main()
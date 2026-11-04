import sys
import threading
import time

import grpc
from google.protobuf import empty_pb2

import chat_pb2
import chat_pb2_grpc

PORT = 50051

# Crea el canal cap al servidor, mante oberta la conexio i la reconecta si cau, insecure != TLS, es podria fer una conexio segura
#channel = grpc.insecure_channel("localhost:50051")
#stub = chat_pb2_grpc.ChatStub(channel)



def poll_chat(stub, nickname):
    shown = 0 #linies impresses
    while True:
        try:
            history = stub.GetChat(empty_pb2.Empty())
            new_line = history.lines[shown:]
            for line in new_line:
                print(f"\r\033[K{line}")
            if new_line:
                # tornem a pintar el prompt perque l'usuari pugi seguir escribint
                print(f"{nickname} --> ", end="", flush=True)
            shown = len(history.lines)
        except grpc.RpcError as e:
            print(f"\r\033[KError llegint el xat: {e.code().name}")
        time.sleep(1)




def main():
    if len(sys.argv) != 3:
        print("Usage: python client.py <chatServerIp> <nickname>")
        sys.exit(1)

    ip = sys.argv[1]
    nikeName = sys.argv[2]
    # Crea el canal cap al servidor, mante oberta la conexio i la reconecta si cau, insecure != TLS, es podria fer una conexio segura
    channel = grpc.insecure_channel(f"{ip}:{PORT}")
    # Crida sincrona, el fill es queda esperant fins la resposta
    # el que rep es un objecte, el que has definit a la classe .proto
    stub = chat_pb2_grpc.ChatStub(channel)

    print(f"===== Welcome {nikeName}! =====")

    t = threading.Thread(target=poll_chat, args=(stub, nikeName),daemon=True) # Creas el thread i li passas la funcio que executarà i els argv que rebra la funcio
    t.start() # Arrancas el thread a partir de poll_chat

    try:
        while True:
            text = input(f"{nikeName} --> ")
            if not text.strip(): # ???
                continue
            try:
                reply = stub.Write(chat_pb2.WriteRequest(nickname=nikeName, text=text))
                if not reply.ok:
                    print("El servidor no ha pogut desar el missatge")
            except grpc.RpcError as e:
                print(f"Error enviado: {e.code().name}")
    except (KeyboardInterrupt, EOFError):
        print("\nAdéu :)")
    finally:
        channel.close()

if __name__ == "__main__":
    main()
from concurrent import futures
import threading

import grpc

import chat_pb2
import chat_pb2_grpc

PORT = 50051
CHAT_FILE = "chat.txt"

class ChatService(chat_pb2_grpc.ChatServicer):

    def __init__(self):
        self.lock = threading.Lock()
        # crea el fitxer si no exixteix
        open(CHAT_FILE, "a", encoding="utf-8").close()

    def Write(self, request, context):
        # request es un chat_pb2.WriteRequest
        line = f"{request.nickname}: {request.text}"
        try:
            with self.lock:
                with open(CHAT_FILE, "a", encoding="utf-8") as f:
                    f.write(line + "\n")
            return chat_pb2.WriteReply(ok=True)
        except Exception as e:
            print(f"Error writing to chat file: {e}")
            return chat_pb2.WriteReply(ok=False)

    def GetChat(self, request, context):
        # request és un Empty, no en fem res
        with self.lock:
            with open(CHAT_FILE, "r", encoding="utf-8") as f:
                lines = f.read().splitlines()
        return chat_pb2.ChatHistory(lines=lines)


def Server():
    # Crea el servidor gRPC. Les peticions s'atenen amb un pool de 10 fils,
    # així pot servir diversos clients alhora.
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Registra la nostra implementació: enllaça les rutes del .proto
    # (/chat.Chat/Write i /chat.Chat/GetChat) amb els mètodes de ChatService.
    chat_pb2_grpc.add_ChatServicer_to_server(ChatService(), server)

    # Escolta al port 50051 a totes les interfícies ([::]), sense TLS.
    server.add_insecure_port(f"[::]:{PORT}")

    # Engega els fils del servidor. No bloqueja: retorna de seguida.
    server.start()
    print(f"Servidor de xat escoltant al port {PORT}")

    try:
        # Bloqueja el fil principal perquè el programa no acabi.
        server.wait_for_termination()
    except KeyboardInterrupt:
        # Ctrl+C: atura el servidor sense esperar les peticions en curs.
        print("\nAturant el servidor")
        server.stop(0)


if __name__ == "__main__":
    Server()
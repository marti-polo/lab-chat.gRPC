# Xat amb gRPC

Mini-lab de Sistemes Distribuïts (La Salle URL). Aplicació de xat client-servidor en Python on la comunicació es fa amb crides a procediments remots (RPC) amb gRPC i els missatges se serialitzen amb protocol buffers.

## Com funciona

El servidor guarda tots els missatges en un fitxer local, `chat.txt`, i publica dos mètodes remots:

- `Write`: rep un nickname i un text i afegeix la línia `nickname: text` al fitxer. Retorna `ok` per confirmar si s'ha desat.
- `GetChat`: retorna totes les línies del fitxer.

El client no guarda cap fitxer. Té dos fils:

- El principal llegeix el que escriu l'usuari i l'envia amb `Write`.
- Un fil secundari crida `GetChat` cada segon i imprimeix només les línies que encara no ha mostrat.

El contracte entre els dos costats és `chat.proto`. A partir d'aquest fitxer, `protoc` genera `chat_pb2.py` (classes dels missatges) i `chat_pb2_grpc.py` (stub del client i classe base del servidor).

## Fitxers

| Fitxer | Contingut |
|---|---|
| `chat.proto` | Definició dels missatges i del servei `Chat` |
| `chat_pb2.py` | Generat per `protoc`: classes dels missatges |
| `chat_pb2_grpc.py` | Generat per `protoc`: `ChatStub`, `ChatServicer` i registre del servei |
| `server.py` | Servidor: implementa `Write` i `GetChat` sobre `chat.txt` |
| `client.py` | Client: envia missatges i consulta el xat cada segon |

## Instal·lació

Provat amb Python 3.14.

```
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # Linux / macOS
pip install -r requirements.txt
```

## Generar els stubs

Només cal si es modifica `chat.proto`:

```
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. chat.proto
```

## Execució

En una terminal, el servidor (escolta al port 50051):

```
python server.py
```

En altres terminals, un client per usuari:

```
python client.py <chatServerIP> <nickname>
```

Exemple amb dos usuaris a la mateixa màquina:

```
python client.py localhost Zipi
python client.py localhost Zape
```

Per sortir del client, Ctrl+C o Ctrl+D. Per aturar el servidor, Ctrl+C.

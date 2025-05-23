import socket
import threading
import json
import time
import random

class Servidor:
    def __init__(self, host, port, id_servidor):
        self.host = host
        self.port = port
        self.id = id_servidor
        self.relogio_logico = 0
        self.relogio_fisico = time.time() + random.uniform(-1, 1)  # relógio com desvio
        self.servidores = []  # Lista de (host, port, id)
        self.coordenador = False
        self.log = []
        self.seguidores = {}  # {usuario: [lista de seguidores]}
        self.inboxes = {}  # {usuario: [mensagens privadas]}

    def iniciar(self):
        threading.Thread(target=self.ouvir_conexoes).start()
        print(f"Servidor {self.id} iniciado em {self.host}:{self.port}")

    def ouvir_conexoes(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((self.host, self.port))
            s.listen()
            while True:
                conn, addr = s.accept()
                threading.Thread(target=self.tratar_conexao, args=(conn,)).start()

    def tratar_conexao(self, conn):
        with conn:
            dados = conn.recv(4096).decode()
            if dados:
                mensagem = json.loads(dados)
                tipo = mensagem.get('tipo')
                if tipo == 'hora':
                    self.enviar_hora(conn)
                elif tipo == 'ajuste':
                    self.ajustar_relogio(mensagem['diferenca'])
                elif tipo == 'seguir':
                    self.adicionar_seguidor(mensagem['origem'], mensagem['alvo'])
                elif tipo == 'mensagem_privada':
                    self.entregar_mensagem_privada(mensagem)
                else:
                    self.atualizar_relogio(mensagem['timestamp'])
                    self.registrar_log(mensagem)
                    print(f"[{self.id}] Mensagem recebida: {mensagem}")
                    if tipo == 'usuario':
                        self.notificar_seguidores(mensagem['origem'], mensagem['conteudo'])

    def atualizar_relogio(self, timestamp):
        self.relogio_logico = max(self.relogio_logico, timestamp) + 1

    def registrar_log(self, mensagem):
        evento = {
            'timestamp_local': self.relogio_logico,
            'relogio_fisico': self.relogio_fisico,
            'mensagem': mensagem
        }
        self.log.append(evento)
        with open(f'log_servidor_{self.id}.txt', 'a') as f:
            f.write(json.dumps(evento) + '\n')

    def enviar_mensagem(self, destino, conteudo):
        self.relogio_logico += 1
        mensagem = {
            'tipo': 'replicacao',
            'origem': self.id,
            'timestamp': self.relogio_logico,
            'conteudo': conteudo
        }
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(destino)
            s.sendall(json.dumps(mensagem).encode())
        self.registrar_log(mensagem)

    def enviar_hora(self, conn):
        resposta = {'hora': self.relogio_fisico}
        conn.sendall(json.dumps(resposta).encode())

    def ajustar_relogio(self, diferenca):
        self.relogio_fisico += diferenca
        print(f"[{self.id}] Ajuste de relógio aplicado: {diferenca:.3f} segundos")

    def eleger_coordenador(self):
        maior_id = self.id
        for _, _, sid in self.servidores:
            if sid > maior_id:
                maior_id = sid
        self.coordenador = (maior_id == self.id)
        if self.coordenador:
            print(f"[{self.id}] Fui eleito coordenador!")
            self.executar_berkeley()

    def executar_berkeley(self):
        diferencas = []
        for host, port, _ in self.servidores:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.sendall(json.dumps({'tipo': 'hora'}).encode())
                    resposta = json.loads(s.recv(4096).decode())
                    delta = resposta['hora'] - time.time()
                    diferencas.append(delta)
            except:
                continue
        media = sum(diferencas + [self.relogio_fisico - time.time()]) / (len(diferencas) + 1)
        for host, port, _ in self.servidores:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                    s.sendall(json.dumps({'tipo': 'ajuste', 'diferenca': media}).encode())
            except:
                continue
        self.ajustar_relogio(media)

    def adicionar_seguidor(self, seguidor, alvo):
        if alvo not in self.seguidores:
            self.seguidores[alvo] = []
        if seguidor not in self.seguidores[alvo]:
            self.seguidores[alvo].append(seguidor)
        print(f"[{self.id}] {seguidor} está seguindo {alvo}")

    def notificar_seguidores(self, autor, conteudo):
        seguidores = self.seguidores.get(autor, [])
        for seguidor in seguidores:
            print(f"[{self.id}] Notificando {seguidor} da nova postagem de {autor}: {conteudo}")

    def entregar_mensagem_privada(self, mensagem):
        destino = mensagem['destino']
        if destino not in self.inboxes:
            self.inboxes[destino] = []
        self.atualizar_relogio(mensagem['timestamp'])
        self.inboxes[destino].append(mensagem)
        self.registrar_log(mensagem)
        print(f"[{self.id}] Mensagem privada de {mensagem['origem']} para {destino} armazenada.")

if __name__ == '__main__':
    servidor = Servidor('127.0.0.1', 8000, 'S1')
    servidor.servidores = [
        ('127.0.0.1', 8001, 'S2'),
        ('127.0.0.1', 8002, 'S3')
    ]
    servidor.iniciar()

    time.sleep(5)
    servidor.eleger_coordenador()
    time.sleep(2)
    servidor.enviar_mensagem(('127.0.0.1', 8001), 'Postagem sincronizada')

# Projeto: Rede Social Distribuída

Este projeto simula uma rede social distribuída com múltiplos servidores e usuários, permitindo postagens públicas, mensagens privadas, seguidores, replicação e sincronização de relógios.

---

## 🔧 Tecnologias Usadas
- **Python 3** (servidores)
- **Node.js** (clientes)
- **Docker** e **Docker Compose** (execução facilitada)

---

## Como Executar

### 1. Clone o repositório e acesse a pasta do projeto
```bash
git clone <URL-do-repositorio>
cd projeto-rede-social
```

### 2. Inicie os serviços
```bash
docker-compose up --build
```

- Inicia 3 servidores Python (portas 8000, 8001, 8002)
- Inicia 5 clientes Node.js (U1 a U5)
- Os clientes enviam postagens regulares, seguem usuários e enviam mensagens privadas

### 3. Para encerrar
```bash
docker-compose down
```

---

## Testes

### Teste de Postagem e Seguidores (2 pontos)
- Observe nos logs do servidor que as postagens de um usuário geram notificações para seus seguidores.

### Teste de Mensagens Privadas (2 pontos)
- Os clientes enviam mensagens privadas a cada 5 segundos.
- Os servidores armazenam essas mensagens em `inboxes`, e registram nos logs.

### Teste de Replicação (2 pontos)
- Cada servidor replica mensagens entre si.
- Logs de replicação podem ser encontrados em `log_servidor_SX.txt`

### Teste de Sincronização de Relógios (2 pontos)
- Coordenador executa o algoritmo de Berkeley.
- A sincronização é visível nos logs dos servidores como "ajuste de relógio aplicado".

### Teste de Relógio Lógico (1 ponto)
- Cada evento nos logs possui `timestamp_local` baseado em relógio lógico.

---

## Estrutura das Mensagens

### Postagem pública
```json
{
  "tipo": "usuario",
  "origem": "U1",
  "timestamp": 10,
  "conteudo": "Olá mundo!"
}
```

### Seguir usuário
```json
{
  "tipo": "seguir",
  "origem": "U2",
  "alvo": "U1"
}
```

### Mensagem privada
```json
{
  "tipo": "mensagem_privada",
  "origem": "U3",
  "destino": "U4",
  "timestamp": 25,
  "conteudo": "Mensagem privada"
}
```

---

## Arquitetura
- Servidores escutam conexões e replicam mensagens.
- Clientes enviam mensagens e interagem com a rede.
- Relógios lógicos garantem ordenação.
- Algoritmo de Berkeley sincroniza os servidores.

---

## Ponto Extra
- Execução automatizada via Docker Compose garante fácil inicialização da rede distribuída.

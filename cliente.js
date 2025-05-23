const net = require('net');
const fs = require('fs');

class Cliente {
  constructor(id, servidorHost, servidorPorta, logPath) {
    this.id = id;
    this.relogioLogico = Math.floor(Math.random() * 10);
    this.servidorHost = servidorHost;
    this.servidorPorta = servidorPorta;
    this.logPath = logPath;
  }

  atualizarRelogio(timestamp) {
    this.relogioLogico = Math.max(this.relogioLogico, timestamp) + 1;
  }

  enviarMensagem(conteudo) {
    this.relogioLogico++;
    const mensagem = {
      tipo: 'usuario',
      origem: this.id,
      timestamp: this.relogioLogico,
      conteudo: conteudo
    };
    this.enviarParaServidor(mensagem);
  }

  seguirUsuario(alvo) {
    const mensagem = {
      tipo: 'seguir',
      origem: this.id,
      alvo: alvo
    };
    this.enviarParaServidor(mensagem);
  }

  enviarMensagemPrivada(destinatario, conteudo) {
    this.relogioLogico++;
    const mensagem = {
      tipo: 'mensagem_privada',
      origem: this.id,
      destino: destinatario,
      timestamp: this.relogioLogico,
      conteudo: conteudo
    };
    this.enviarParaServidor(mensagem);
  }

  enviarParaServidor(mensagem) {
    const client = new net.Socket();
    client.connect(this.servidorPorta, this.servidorHost, () => {
      client.write(JSON.stringify(mensagem));
      client.end();
      this.registrarLog(mensagem);
    });

    client.on('error', (err) => {
      console.error('Erro na conexão:', err.message);
    });
  }

  registrarLog(mensagem) {
    const log = {
      timestamp_local: this.relogioLogico,
      mensagem: mensagem
    };
    fs.appendFileSync(this.logPath, JSON.stringify(log) + '\n');
  }
}

if (process.argv.length < 6) {
  console.log('Uso: node cliente.js <ID> <HOST> <PORTA> <LOG_FILE> [alvo_para_seguir]');
  process.exit(1);
}

const [_, __, id, host, porta, logFile, followTarget] = process.argv;
const cliente = new Cliente(id, host, parseInt(porta), logFile);

if (followTarget) {
  cliente.seguirUsuario(followTarget);
}

setInterval(() => {
  const conteudo = `Mensagem de ${cliente.id} em ${new Date().toISOString()}`;
  cliente.enviarMensagem(conteudo);

  // Simula envio de mensagem privada de tempos em tempos
  const destino = 'U2'; // exemplo de destino fixo
  const mensagemPrivada = `Privado para ${destino} de ${cliente.id}`;
  cliente.enviarMensagemPrivada(destino, mensagemPrivada);
}, 5000);

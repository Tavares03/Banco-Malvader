CREATE DATABASE banco_malvader;
USE banco_malvader;

-- criaçao das tabelas
CREATE TABLE usuario(
	id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nome VARCHAR(100) NOT NULL,
    cpf VARCHAR(11) UNIQUE NOT NULL,
    data_nascimento DATE NOT NULL,
    telefone VARCHAR(15) NOT NULL,
    tipo_usuario ENUM('FUNCIONARIO', 'CLIENTE') NOT NULL,
    senha_hash VARCHAR(32) NOT NULL,
    otp_ativo VARCHAR(6),
    otp_expiracao DATETIME
);

CREATE TABLE funcionario(
	id_funcionario INT AUTO_INCREMENT PRIMARY KEY,
    id_usuario INT NOT NULL,
    codigo_funcionario VARCHAR(20) UNIQUE NOT NULL,
    cargo ENUM('ESTAGIARIO', 'ATENDENTE', 'GERENTE') NOT NULL,
    id_supervisor INT NOT NULL,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario),
    FOREIGN KEY (id_supervisor) REFERENCES funcionario(id_funcionario)
);

CREATE TABLE cliente(
	id_cliente INT AUTO_INCREMENT PRIMARY KEY,
	id_usuario INT NOT NULL,
	score_credito DECIMAL(5,2) DEFAULT 0,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE endereco(
	id_endereco INT AUTO_INCREMENT PRIMARY KEY,
	id_usuario INT NOT NULL,
	cep VARCHAR(10) NOT NULL,
	lugar VARCHAR(100) NOT NULL,
	numero_casa INT NOT NULL,
	bairro VARCHAR(50) NOT NULL,
	cidade VARCHAR(50) NOT NULL,
	estado CHAR(2) NOT NULL,
	complemento VARCHAR(50),
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE agencia(
	id_agencia INT AUTO_INCREMENT PRIMARY KEY,
	nome VARCHAR(50) NOT NULL,
	codigo_agencia VARCHAR(10) UNIQUE NOT NULL,
	id_endereco INT NOT NULL,
	FOREIGN KEY (id_endereco) REFERENCES endereco(id_endereco)
);

CREATE TABLE conta(
	id_conta INT AUTO_INCREMENT PRIMARY KEY,
	numero_conta VARCHAR(20) UNIQUE NOT NULL,
	id_agencia INT NOT NULL,
	saldo DECIMAL(15,2) NOT NULL DEFAULT 0,
	tipo_conta ENUM('POUPANCA', 'CORRENTE', 'INVESTIMENTO') NOT NULL,
	id_cliente INT NOT NULL,
	data_abertura DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
	status ENUM('ATIVA', 'ENCERRADA', 'BLOQUEADA') NOT NULL DEFAULT 'ATIVA',
	FOREIGN KEY (id_agencia) REFERENCES agencia(id_agencia),
    FOREIGN KEY (id_cliente) REFERENCES cliente(id_cliente)
);

CREATE TABLE conta_poupanca(
	id_conta_poupanca INT AUTO_INCREMENT PRIMARY KEY,
	id_conta INT NOT NULL UNIQUE,
	taxa_rendimento DECIMAL(5,2) NOT NULL,
	ultimo_rendimento DATETIME,
	FOREIGN KEY (id_conta) REFERENCES conta(id_conta)
);

CREATE TABLE conta_corrente(
	id_conta_corrente INT AUTO_INCREMENT PRIMARY KEY,
	id_conta INT NOT NULL UNIQUE,
	limite DECIMAL(15,2) NOT NULL DEFAULT 0,
	data_vencimento DATE NOT NULL,
	taxa_manutencao DECIMAL(5,2) NOT NULL DEFAULT 0,
    FOREIGN KEY (id_conta) REFERENCES conta(id_conta)
);

CREATE TABLE conta_investimento(
	id_conta_investimento INT AUTO_INCREMENT PRIMARY KEY,
	id_conta INT UNIQUE NOT NULL,
	perfil_risco ENUM('BAIXO', 'MEDIO', 'ALTO') NOT NULL,
	valor_minimo DECIMAL(15,2) NOT NULL,
	taxa_rendimento_base DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (id_conta) REFERENCES conta(id_conta)
);

CREATE TABLE transacao(
	id_transacao INT AUTO_INCREMENT PRIMARY KEY,
	id_conta_origem INT NOT NULL,
	id_conta_destino INT NOT NULL,
	tipo_transacao ENUM('DEPOSITO', 'SAQUE', 'TRANSFERENCIA', 'TAXA', 'RENDIMENTO') NOT NULL,
	valor DECIMAL(15,2) NOT NULL,
	data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	descricao VARCHAR(100),
    FOREIGN KEY (id_conta_origem) REFERENCES conta(id_conta),
	FOREIGN KEY (id_conta_destino) REFERENCES conta(id_conta)
);

CREATE TABLE auditoria(
	id_auditoria INT AUTO_INCREMENT PRIMARY KEY,
	id_usuario INT NOT NULL,
	acao VARCHAR(50) NOT NULL,
	data_hora TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	detalhes TEXT,
    FOREIGN KEY (id_usuario) REFERENCES usuario(id_usuario)
);

CREATE TABLE relatorio(
	id_relatorio INT AUTO_INCREMENT PRIMARY KEY,
	id_funcionario INT NOT NULL,
	tipo_relatorio VARCHAR(50) NOT NULL,
	data_geracao TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
	conteudo TEXT NOT NULL,
	FOREIGN KEY (id_funcionario) REFERENCES funcionario(id_funcionario)
);

-- selects das tabelas
SELECT * FROM usuario;
SELECT * FROM funcionario;
SELECT * FROM endereco;
SELECT * FROM conta;
SELECT * FROM cliente;
SELECT * FROM conta_corrente;
SELECT * FROM conta_poupanca;
SELECT * FROM transacao;

-- para deletar usuarios, clientes e funcionarios de todas as tabelas, com os seus enderecos
DELETE FROM cliente WHERE id_usuario = 31;
DELETE FROM funcionario WHERE id_usuario = 31;
DELETE FROM endereco WHERE id_usuario = 31;
DELETE FROM usuario WHERE id_usuario = 31;

-- deleta tudo dessas tabelas
DELETE FROM transacao WHERE id_transacao > 0;
DELETE FROM conta WHERE id_conta > 0;
DELETE FROM agencia WHERE id_agencia > 0;

-- faz um deposito ou saque manualmente para teste
INSERT INTO transacao (
  id_conta_origem,
  id_conta_destino,
  tipo_transacao,
  valor,
  descricao
)
VALUES (
  4, -- id_conta do cliente
  4, -- mesmo id_conta (para depósito)
  'SAQUE',
  50.00,
  'Depósito inicial de teste'
);

-- comando para criar um suario, endereco e agencia
INSERT INTO usuario (
  nome, cpf, data_nascimento, telefone, tipo_usuario, senha_hash
) VALUES (
  'Agência Fake', '99999999999', '2000-01-01', '0000000000', 'FUNCIONARIO', MD5('agencia123')
);

SET @id_usuario := LAST_INSERT_ID();

INSERT INTO endereco (
  id_usuario, cep, lugar, numero_casa, bairro, cidade, estado, complemento
)
VALUES (
  @id_usuario, '00000-000', 'Av. Malvader', 123, 'Centro', 'São Paulo', 'SP', 'Sede Central'
);

SET @id_endereco := LAST_INSERT_ID();

INSERT INTO agencia (id_agencia, nome, codigo_agencia, id_endereco)
VALUES (1, 'Agência Central Malvader', '0001', @id_endereco);

-- criando o gerente para colocar como inicio
INSERT INTO usuario (
  nome, cpf, data_nascimento, telefone, tipo_usuario, senha_hash
) VALUES (
  'Gerente Base', '11111111111', '1980-01-01', '11999999999', 'FUNCIONARIO', MD5('senha123')
);

SET @id_usuario_gerente := LAST_INSERT_ID();

INSERT INTO endereco (
  id_usuario, cep, lugar, numero_casa, bairro, cidade, estado, complemento
) VALUES (
  @id_usuario_gerente, '00000-000', 'Rua Central', 1, 'Centro', 'Cidade', 'SP', 'Sede Geral'
);

ALTER TABLE funcionario MODIFY id_supervisor INT NULL;

INSERT INTO funcionario (
  id_usuario, codigo_funcionario, cargo, id_supervisor
) VALUES (
  @id_usuario_gerente, 'GERENTEBASE', 'GERENTE', NULL
);

SET @id_func_gerente := LAST_INSERT_ID();

UPDATE funcionario SET id_supervisor = @id_func_gerente WHERE id_funcionario = @id_func_gerente;

-- cria uma conta_corrente
INSERT INTO conta_corrente (
  id_conta, limite, data_vencimento, taxa_manutencao
)
VALUES (
  4, 1000.00, CURDATE() + INTERVAL 30 DAY, 5.00
);

-- area das procedures
DELIMITER $$
CREATE TRIGGER atualizar_saldo AFTER INSERT ON transacao
FOR EACH ROW
BEGIN
    IF NEW.tipo_transacao = 'DEPOSITO' THEN
        UPDATE conta SET saldo = saldo + NEW.valor WHERE id_conta = NEW.id_conta_origem;
    ELSEIF NEW.tipo_transacao IN ('SAQUE', 'TAXA') THEN
        UPDATE conta SET saldo = saldo - NEW.valor WHERE id_conta = NEW.id_conta_origem;
    ELSEIF NEW.tipo_transacao = 'TRANSFERENCIA' THEN
        UPDATE conta SET saldo = saldo - NEW.valor WHERE id_conta = NEW.id_conta_origem;
        UPDATE conta SET saldo = saldo + NEW.valor WHERE id_conta = NEW.id_conta_destino;
    END IF;
END $$
DELIMITER ;

DROP TRIGGER IF EXISTS validar_senha;

DELIMITER $$
CREATE TRIGGER validar_senha BEFORE UPDATE ON usuario
FOR EACH ROW
BEGIN
    IF NEW.senha_hash != OLD.senha_hash THEN
        IF NEW.senha_hash REGEXP '^[0-9a-f]{32}$' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Senha deve ser atualizada via procedure com validação';
        END IF;
    END IF;
END $$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER limite_deposito BEFORE INSERT ON transacao
FOR EACH ROW
BEGIN
    DECLARE total_dia DECIMAL(15,2);
    SELECT SUM(valor) INTO total_dia
    FROM transacao
    WHERE id_conta_origem = NEW.id_conta_origem
      AND tipo_transacao = 'DEPOSITO'
      AND DATE(data_hora) = DATE(NEW.data_hora);
    IF (total_dia + NEW.valor) > 10000 THEN
        SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Limite diário de depósito excedido';
    END IF;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS gerar_otp;

DELIMITER $$
CREATE PROCEDURE gerar_otp(IN pid_usuario INT)
BEGIN
    DECLARE novo_otp VARCHAR(6);
    SET novo_otp = LPAD(FLOOR(RAND() * 1000000), 6, '0');
    
    UPDATE usuario
    SET otp_ativo = novo_otp, otp_expiracao = NOW() + INTERVAL 5 MINUTE
    WHERE id_usuario = pid_usuario;

    SELECT novo_otp AS novo_otp;
END $$
DELIMITER ;

DELIMITER $$
CREATE PROCEDURE calcular_score_credito(IN id_cliente INT)
BEGIN
    DECLARE total_trans DECIMAL(15,2);
    DECLARE media_trans DECIMAL(15,2);
    SELECT SUM(valor), AVG(valor) INTO total_trans, media_trans
    FROM transacao t
    JOIN conta c ON t.id_conta_origem = c.id_conta
    WHERE c.id_cliente = id_cliente AND t.tipo_transacao IN ('DEPOSITO', 'SAQUE');
    UPDATE cliente SET score_credito = LEAST(100, (total_trans / 1000) + (media_trans / 100))
    WHERE id_cliente = id_cliente;
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS criar_cliente_e_conta;

DELIMITER $$
CREATE PROCEDURE criar_cliente_e_conta(IN pid_usuario INT)
BEGIN
    DECLARE novo_id_cliente INT;
    DECLARE novo_id_conta INT;
    DECLARE numero_conta_gerado VARCHAR(20);

    -- Cria o cliente
    INSERT INTO cliente (id_usuario) VALUES (pid_usuario);
    SET novo_id_cliente = LAST_INSERT_ID();

    -- Gera número de conta aleatório
    SET numero_conta_gerado = LPAD(FLOOR(RAND() * 1000000000), 10, '0');

    -- Cria a conta (tipo CORRENTE)
    INSERT INTO conta (
        numero_conta, id_agencia, saldo, tipo_conta, id_cliente, status
    ) VALUES (
        numero_conta_gerado, 1, 0.00, 'CORRENTE', novo_id_cliente, 'ATIVA'
    );
    SET novo_id_conta = LAST_INSERT_ID();

    -- Cria a entrada na tabela conta_corrente
    INSERT INTO conta_corrente (
        id_conta, limite, data_vencimento, taxa_manutencao
    ) VALUES (
        novo_id_conta, 1000.00, CURDATE() + INTERVAL 30 DAY, 5.00
    );
END $$
DELIMITER ;

DROP PROCEDURE IF EXISTS criar_funcionario_padrao;

DELIMITER $$
CREATE PROCEDURE criar_funcionario_padrao(
  IN pid_usuario INT,
  IN pcodigo_funcionario VARCHAR(20)
)
BEGIN
    DECLARE cargo_base ENUM('ESTAGIARIO','ATENDENTE','GERENTE');
    DECLARE cargo_alvo VARCHAR(20);
    DECLARE id_supervisor_base INT;

    -- Define o menor cargo disponível (pega o primeiro da enum manualmente)
    SET cargo_alvo = 'ESTAGIARIO';

    -- Busca o ID do supervisor com cargo = 'GERENTE'
    SELECT f.id_funcionario INTO id_supervisor_base
    FROM funcionario f
    JOIN usuario u ON f.id_usuario = u.id_usuario
    WHERE f.cargo = 'GERENTE'
    ORDER BY f.id_funcionario ASC
    LIMIT 1;

    -- Insere o novo funcionário com cargo e supervisor definidos
    INSERT INTO funcionario (
        id_usuario,
        codigo_funcionario,
        cargo,
        id_supervisor
    ) VALUES (
        pid_usuario,
        pcodigo_funcionario,
        cargo_alvo,
        id_supervisor_base
    );
END $$
DELIMITER ;

-- area das views
CREATE VIEW vw_resumo_contas AS
SELECT c.id_cliente, u.nome, COUNT(co.id_conta) AS total_contas, SUM(co.saldo) AS saldo_total
FROM cliente c
JOIN usuario u ON c.id_usuario = u.id_usuario
JOIN conta co ON c.id_cliente = co.id_cliente
GROUP BY c.id_cliente, u.nome;

CREATE VIEW vw_movimentacoes_recentes AS
SELECT t.*, c.numero_conta, u.nome AS cliente
FROM transacao t
JOIN conta c ON t.id_conta_origem = c.id_conta
JOIN cliente cl ON c.id_cliente = cl.id_cliente
JOIN usuario u ON cl.id_usuario = u.id_usuario
WHERE t.data_hora >= NOW() - INTERVAL 90 DAY;

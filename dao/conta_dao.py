from util.db import conectar
import random, hashlib

def criar_conta_extra(id_usuario, tipo_conta):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # Busca id_cliente
            cursor.execute("SELECT id_cliente FROM cliente WHERE id_usuario = %s", (id_usuario,))
            cliente = cursor.fetchone()
            if not cliente:
                return False
            id_cliente = cliente["id_cliente"]

            numero_conta = f"{random.randint(1000000000, 9999999999)}"

            # Criar conta
            cursor.execute("""
                INSERT INTO conta (numero_conta, id_agencia, saldo, tipo_conta, id_cliente, status)
                VALUES (%s, %s, %s, %s, %s, 'ATIVA')
            """, (numero_conta, 1, 0.00, tipo_conta, id_cliente))

            id_conta = cursor.lastrowid

            if tipo_conta == "POUPANCA":
                cursor.execute("""
                    INSERT INTO conta_poupanca (id_conta, taxa_rendimento, ultimo_rendimento)
                    VALUES (%s, %s, NULL)
                """, (id_conta, 0.50))  # exemplo de rendimento

            elif tipo_conta == "INVESTIMENTO":
                cursor.execute("""
                    INSERT INTO conta_investimento (id_conta, perfil_risco, valor_minimo, taxa_rendimento_base)
                    VALUES (%s, %s, %s, %s)
                """, (id_conta, 'MEDIO', 500.00, 1.25))

        conexao.commit()
        return True
    finally:
        conexao.close()

def historico_transacoes(id_conta: int):
    """
    Busca o histórico de transações de uma conta específica.
    """
    # Assume que você tem uma função conectar() que retorna uma conexão
    conexao = conectar() 
    try:
        with conexao.cursor() as cursor:
            # A query SQL busca todas as transações da conta e cria uma coluna "movimento"
            # para identificar se foi uma entrada ou saída de dinheiro.
            sql = """
                SELECT 
                    data_hora,
                    tipo_transacao,
                    valor,
                    descricao,
                    CASE
                        WHEN id_conta_origem = %(id_conta)s AND tipo_transacao IN ('SAQUE', 'TRANSFERENCIA', 'TAXA') THEN 'SAIDA'
                        WHEN id_conta_destino = %(id_conta)s AND tipo_transacao IN ('DEPOSITO', 'TRANSFERENCIA', 'RENDIMENTO') THEN 'ENTRADA'
                        WHEN id_conta_origem = %(id_conta)s AND tipo_transacao IN ('DEPOSITO', 'RENDIMENTO') THEN 'ENTRADA'
                    END as movimento
                FROM transacao
                WHERE id_conta_origem = %(id_conta)s OR id_conta_destino = %(id_conta)s
                ORDER BY data_hora DESC;
            """
            # Usamos um dicionário como parâmetro por causa do placeholder nomeado %(id_conta)s
            cursor.execute(sql, {'id_conta': id_conta})
            
            # fetchall() irá retornar a lista de dicionários, pronta para o template
            return cursor.fetchall()
    finally:
        # Garante que a conexão seja sempre fechada
        conexao.close()

def conta_por_id(id_conta: int):
    """
    Busca os dados de uma conta específica pelo seu ID.
    """
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = "SELECT id_conta, numero_conta, saldo, tipo_conta FROM conta WHERE id_conta = %s"
            
            cursor.execute(sql, (id_conta,))
            
            # fetchone() retorna um único dicionário com os dados da conta
            return cursor.fetchone()
    finally:
        conexao.close()

def conta_por_usuario(id_usuario):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            sql = """
                SELECT co.id_conta
                FROM conta co
                JOIN cliente cl ON co.id_cliente = cl.id_cliente
                WHERE cl.id_usuario = %s AND co.status = 'ATIVA'
                LIMIT 1
            """
            cursor.execute(sql, (id_usuario,))
            return cursor.fetchone()
    finally:
        conexao.close()

def transferir_valor(id_conta_origem, id_conta_destino, valor):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # Verifica se a conta origem tem saldo suficiente
            cursor.execute("SELECT saldo FROM conta WHERE id_conta = %s", (id_conta_origem,))
            origem = cursor.fetchone()

            if not origem or origem["saldo"] < valor:
                return False

            # Realiza a transferência como uma transação
            cursor.execute("""
                INSERT INTO transacao (
                    id_conta_origem, id_conta_destino, tipo_transacao, valor, descricao
                ) VALUES (%s, %s, 'TRANSFERENCIA', %s, %s)
            """, (
                id_conta_origem, id_conta_destino, valor, "Transferência entre contas"
            ))

        conexao.commit()
        return True
    except:
        return False
    finally:
        conexao.close()

def realizar_deposito(id_conta: int, valor: float):
    """
    Realiza um depósito em uma conta específica.
    Insere um registro na tabela de transações.
    """
    # Validação para garantir que o valor do depósito seja positivo
    if not isinstance(valor, (int, float)) or valor <= 0:
        print("Erro: O valor do depósito deve ser um número positivo.")
        return False

    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # Para depósitos, a conta de origem e destino são a mesma
            sql = """
                INSERT INTO transacao 
                    (id_conta_origem, id_conta_destino, tipo_transacao, valor, descricao)
                VALUES 
                    (%s, %s, 'DEPOSITO', %s, %s)
            """
            descricao = f"Depósito no valor de R$ {valor:.2f}"
            
            # Executa a query com os parâmetros
            cursor.execute(sql, (id_conta, id_conta, valor, descricao))

        # Confirma a transação no banco de dados
        conexao.commit()
        return True # Retorna sucesso

    except Exception as e:
        # Em caso de erro, desfaz a transação
        conexao.rollback()
        print(f"Erro ao realizar depósito: {e}")
        return False
        
    finally:
        # Garante que a conexão seja sempre fechada
        conexao.close()

def get_limite_e_score(id_conta: int):
    """
    Busca o limite de crédito atual e o score de crédito do cliente
    para uma conta corrente específica.
    """
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # Esta query une as tabelas para pegar todas as informações necessárias
            sql = """
                SELECT 
                    cc.limite, 
                    cl.score_credito
                FROM conta_corrente cc
                JOIN conta co ON cc.id_conta = co.id_conta
                JOIN cliente cl ON co.id_cliente = cl.id_cliente
                WHERE cc.id_conta = %s
            """
            cursor.execute(sql, (id_conta,))
            return cursor.fetchone() # Retorna um dicionário com {'limite': X, 'score_credito': Y}
    finally:
        conexao.close()

def realizar_saque(id_conta: int, valor: float):
    """
    Realiza um saque de uma conta específica após verificar o saldo.
    """
    if not isinstance(valor, (int, float)) or valor <= 0:
        print("Erro: O valor do saque deve ser um número positivo.")
        return False

    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # PASSO 1: VERIFICAR O SALDO ATUAL
            cursor.execute("SELECT saldo FROM conta WHERE id_conta = %s", (id_conta,))
            resultado = cursor.fetchone()

            if not resultado:
                print(f"Erro: Conta com ID {id_conta} não encontrada.")
                return False

            saldo_atual = resultado['saldo']

            # PASSO 2: VALIDAR SE O SALDO É SUFICIENTE
            if saldo_atual < valor:
                print("Erro: Saldo insuficiente para realizar o saque.")
                # Retornamos um código específico para que a rota possa saber o motivo da falha
                return 'SALDO_INSUFICIENTE' 
            
            # PASSO 3: SE O SALDO FOR SUFICIENTE, INSERE A TRANSAÇÃO
            sql_insert = """
                INSERT INTO transacao 
                    (id_conta_origem, id_conta_destino, tipo_transacao, valor, descricao)
                VALUES 
                    (%s, %s, 'SAQUE', %s, %s)
            """
            descricao = f"Saque no valor de R$ {valor:.2f}"
            cursor.execute(sql_insert, (id_conta, id_conta, valor, descricao))

        # Se tudo deu certo, confirma a transação
        conexao.commit()
        return True

    except Exception as e:
        conexao.rollback()
        print(f"Erro ao realizar saque: {e}")
        return False
        
    finally:
        conexao.close()

def encerrar_conta(numero_conta: str, cpf: str, senha: str):
    """
    Encerra uma conta após validar as credenciais e o saldo.
    """
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # 1. Busca todos os dados necessários com uma única query segura
            sql_select = """
                SELECT 
                    co.id_conta, 
                    co.saldo,
                    co.status,
                    u.senha_hash
                FROM conta co
                JOIN cliente cl ON co.id_cliente = cl.id_cliente
                JOIN usuario u ON cl.id_usuario = u.id_usuario
                WHERE co.numero_conta = %s AND u.cpf = %s
            """
            cursor.execute(sql_select, (numero_conta, cpf))
            dados_conta = cursor.fetchone()

            # 2. Valida se os dados da conta e CPF conferem
            if not dados_conta:
                return 'DADOS_INCORRETOS' # Conta e/ou CPF não correspondem

            # 3. Valida a senha do usuário
            senha_md5 = hashlib.md5(senha.encode()).hexdigest()
            if senha_md5 != dados_conta['senha_hash']:
                return 'DADOS_INCORRETOS' # Senha incorreta

            # 4. Valida se a conta já não está encerrada
            if dados_conta['status'] == 'ENCERRADA':
                return 'CONTA_JA_ENCERRADA'
            
            # 5. Valida se o saldo da conta é zero
            if dados_conta['saldo'] != 0.00:
                return 'SALDO_NAO_ZERADO' # Não pode encerrar conta com saldo
                
            # 6. Se todas as validações passaram, atualiza o status
            id_conta_para_encerrar = dados_conta['id_conta']
            sql_update = "UPDATE conta SET status = 'ENCERRADA' WHERE id_conta = %s"
            cursor.execute(sql_update, (id_conta_para_encerrar,))
            
            conexao.commit()
            return True # Sucesso

    except Exception as e:
        conexao.rollback()
        print(f"Erro ao encerrar conta: {e}")
        return False
        
    finally:
        conexao.close()

def criar_conta_completa(id_usuario, tipo_conta, **kwargs):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # Busca id_cliente
            cursor.execute("SELECT id_cliente FROM cliente WHERE id_usuario = %s", (id_usuario,))
            cliente = cursor.fetchone()
            if not cliente:
                # Se não existe cliente, cria
                cursor.execute("INSERT INTO cliente (id_usuario) VALUES (%s)", (id_usuario,))
                id_cliente = cursor.lastrowid
            else:
                id_cliente = cliente["id_cliente"]

            numero_conta = f"{random.randint(1000000000, 9999999999)}"
            cursor.execute("""
                INSERT INTO conta (numero_conta, id_agencia, saldo, tipo_conta, id_cliente, status)
                VALUES (%s, %s, %s, %s, %s, 'ATIVA')
            """, (numero_conta, 1, 0.00, tipo_conta, id_cliente))
            id_conta = cursor.lastrowid

            if tipo_conta == "POUPANCA":
                cursor.execute("""
                    INSERT INTO conta_poupanca (id_conta, taxa_rendimento, ultimo_rendimento)
                    VALUES (%s, %s, NULL)
                """, (id_conta, kwargs.get('taxa_rendimento', 0.5)))
            elif tipo_conta == "INVESTIMENTO":
                cursor.execute("""
                    INSERT INTO conta_investimento (id_conta, perfil_risco, valor_minimo, taxa_rendimento_base)
                    VALUES (%s, %s, %s, %s)
                """, (
                    id_conta,
                    kwargs.get('perfil_risco', 'MEDIO'),
                    kwargs.get('valor_minimo', 500.00),
                    kwargs.get('taxa_rendimento_base', 1.25)
                ))
            elif tipo_conta == "CORRENTE":
                cursor.execute("""
                    INSERT INTO conta_corrente (id_conta, limite, data_vencimento, taxa_manutencao)
                    VALUES (%s, %s, %s, %s)
                """, (
                    id_conta,
                    kwargs.get('limite', 1000.00),
                    kwargs.get('data_vencimento', '2099-12-31'),
                    kwargs.get('taxa_manutencao', 5.00)
                ))
        conexao.commit()
        return True
    finally:
        conexao.close()

def atualizar_dados_conta_corrente(numero_conta, novo_limite, nova_data_vencimento, nova_taxa_manutencao):
    conexao = conectar()
    try:
        with conexao.cursor() as cursor:
            # Busca o id_conta pelo número
            cursor.execute("SELECT id_conta FROM conta WHERE numero_conta = %s AND tipo_conta = 'CORRENTE'", (numero_conta,))
            conta = cursor.fetchone()
            if not conta:
                return False  # Conta não encontrada ou não é corrente
            id_conta = conta['id_conta']
            # Atualiza os dados na conta_corrente
            cursor.execute("""
                UPDATE conta_corrente
                SET limite = %s, data_vencimento = %s, taxa_manutencao = %s
                WHERE id_conta = %s
            """, (novo_limite, nova_data_vencimento, nova_taxa_manutencao, id_conta))
        conexao.commit()
        return True
    finally:
        conexao.close()
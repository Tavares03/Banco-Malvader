# Banco-Malvader

Projeto de um sistema bancário desenvolvido em Flask.

## Pré-requisitos

- Python 3.8 ou superior instalado
- Git instalado (opcional, para clonar o repositório)
- MySQL ou MariaDB instalado e rodando
- Variáveis de ambiente configuradas (ver `.env.example` ou instruções
abaixo)

## Inicializar o projeto

1. **Clone o repositório (opcional):**
   ```bash
   git clone https://github.com/seu-usuario/Banco-Malvader.git
   cd Banco-Malvader
   ```

2. **Crie e ative o ambiente virtual (recomendado):**
   ```bash
   python -m venv venv
   venv\Scripts\activate   # No Windows
   # Ou, no Linux/Mac:
   # source venv/bin/activate
   ```

3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure o arquivo `.env`:**
   - Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
     ```
     SECRET_KEY=sua_chave_secreta
     DB_HOST=localhost
     DB_USER=seu_usuario
     DB_PASSWORD=sua_senha
     DB_NAME=nome_do_banco
     ```
   - Ajuste os valores conforme seu ambiente.

5. **Configure o banco de dados:**
   - Crie o banco de dados e as tabelas necessárias no MySQL/MariaDB.
   - Importe o script SQL fornecido (caso exista) ou crie as tabelas manualmente conforme o modelo do projeto.

6. **Inicie o projeto:**
   ```bash
   python app.py
   ```

7. **Acesse no navegador:**
   ```
   http://localhost:5000/
   ```

## Observações

- O projeto utiliza Flask, Bootstrap e conexão com banco de dados MySQL/MariaDB.
- Para adicionar novos usuários, utilize a tela de cadastro.
- Para dúvidas sobre variáveis de ambiente, consulte o arquivo `.env.example` (se disponível) ou peça suporte ao desenvolvedor.


# Importação das bibliotecas necessárias
import requests  # Para fazer requisições HTTP
import msvcrt    # Para capturar entrada de teclado (usado no final do script)
import json      # Para manipulação de dados no formato JSON
import time      # Para manipulação de tempo (usado na função de token)

# Caminho para o arquivo JSON que contém as credenciais do Notion
notion_credenciais_json = "C:\\Users\\Scripts\\notion_credenciais.json"

# Abre o arquivo JSON e carrega as credenciais do Notion
with open(notion_credenciais_json, 'r', encoding='utf-8') as nc:
    notion_credenciais = json.load(nc)

# Extrai a chave da API, o ID da base de dados de solicitação de pagamentos e o ID da base de dados bancários de fornecedores
NOTION_API_KEY = notion_credenciais["Pagamentos_de_Projetos_Key"]  # Chave da API do Notion
SOLICITACAO_PAGAMENTO_DATABASE_ID = notion_credenciais["Pagamentos_de_Projetos_ID"]  # ID da base de dados de solicitação de pagamentos
BANCO_DE_DADOS_ID = notion_credenciais["Dados_Bancarios_Fornecedores_ID"]  # ID da base de dados bancários de fornecedores

# Caminho para o arquivo JSON que contém as credenciais do Banco Inter
inter_credenciais_json = "C:\\Users\\Scripts\\Inter_API-Chave_e_Certificado\\inter_credenciais.json"

# Abre o arquivo JSON e carrega as credenciais do Banco Inter
with open(inter_credenciais_json, 'r', encoding='utf-8') as ic:
    inter_credenciais = json.load(ic)

# Caminhos para o certificado e chave do Banco Inter
cert_path = "C:\\Users\\Scripts\\Inter_API-Chave_e_Certificado\\Certificado.crt"
key_path = "C:\\Users\\Scripts\\Inter_API-Chave_e_Certificado\\Chave.key"

# Extrai as credenciais do Banco Inter
conta_corrente = inter_credenciais["CONTA_CORRENTE"]
client_id = inter_credenciais["CLIENT_ID"]
client_secret = inter_credenciais["CLIENT_SECRET"]

# Função para obter dados de uma base de dados do Notion
def get_notion_data(database_id):
    print(f"Fetching data from Notion database ID: {database_id}")
    url = f"https://api.notion.com/v1/databases/{database_id}/query"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28"
    }
    response = requests.post(url, headers=headers)
    if response.status_code == 200:
        print("Data fetched successfully from Notion.")
        return response.json()
    else:
        raise Exception(f"Failed to fetch data from Notion: {response.status_code}, {response.text}")

# Função para extrair o valor de uma propriedade específica de uma página do Notion
def extract_property_value(page_id, property_name):
    print(f"Fetching property '{property_name}' for page ID: {page_id}")
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        page_data = response.json()
        value = page_data['properties'].get(property_name, {}).get('rollup', {}).get('array', [{}])[0].get('rich_text', [{}])[0].get('text', {}).get('content', '')
        print(f"Property value for '{property_name}': {value}")
        return value
    else:
        raise Exception(f"Failed to fetch page data from Notion: {response.status_code}, {response.text}")

# Função para obter os nomes relacionados a IDs de relação no Notion
def get_relation_names(relation_ids):
    names = []
    print(f"Fetching names for relation IDs: {relation_ids}")
    for relation_id in relation_ids:
        url = f"https://api.notion.com/v1/pages/{relation_id}"
        headers = {
            "Authorization": f"Bearer {NOTION_API_KEY}",
            "Notion-Version": "2022-06-28"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            page_data = response.json()
            name = page_data['properties'].get('Nome', {}).get('title', [{}])[0].get('text', {}).get('content', '')
            print(f"Name for relation ID {relation_id}: {name}")
            names.append(name)
        else:
            raise Exception(f"Failed to fetch page data from Notion: {response.status_code}, {response.text}")
    return names

# Função para obter o valor de uma propriedade específica de um objeto de propriedades
def get_property_value(properties, key, default=''):
    try:
        value = properties.get(key, {}).get('rollup', {}).get('array', [{}])[0].get('rich_text', [{}])[0].get('text', {}).get('content', default)
        print(f"Property '{key}' value: {value}")
        return value
    except (IndexError, KeyError):
        print(f"Property '{key}' not found or has an error.")
        return default

# Função para obter o valor de texto de uma propriedade específica
def get_text_value(properties, key, default=''):
    try:
        value = properties.get(key, {}).get('title', [{}])[0].get('text', {}).get('content', default)
        print(f"Text value for '{key}': {value}")
        return value
    except (IndexError, KeyError):
        print(f"Text value for '{key}' not found or has an error.")
        return default

# Função para atualizar o status de uma página no Notion
def atualizar_status_notion(page_id, novo_status):
    print(f"Atualizando status na pagina {page_id} para '{novo_status}'")
    
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    data = {
        "properties": {
            "Status": {
                "status": {  
                    "name": novo_status
                }
            }
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"Status atualizado com sucesso para a page ID {page_id}.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err}, Response: {response.text}")
    except Exception as e:
        print(f"Failed to update page status in Notion: {e}")

# Função para inserir o ID da transação no Notion
def inserir_id_transacao(page_id, codigoSolicitacao):
    print(f"Inserindo ID da transação no Notion para page ID {page_id} com valor '{codigoSolicitacao}'")
    
    url = f"https://api.notion.com/v1/pages/{page_id}"
    headers = {
        "Authorization": f"Bearer {NOTION_API_KEY}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    data = {
        "properties": {
            "codigoSolicitacao": {
                "rich_text": [
                    {
                        "text": {
                            "content": codigoSolicitacao
                        }
                    }
                ]
            }
        }
    }
    
    try:
        response = requests.patch(url, headers=headers, json=data)
        response.raise_for_status()
        print(f"ID de transação inserido com sucesso para a page ID {page_id}.")
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error: {err}, Response: {response.text}")
    except Exception as e:
        print(f"Failed to insert transaction ID in Notion: {e}")

# Função para obter o token de acesso do Banco Inter
def obter_token():
    print("Obtendo token do Banco Inter")
    request_body = f'client_id={client_id}&client_secret={client_secret}&scope=pagamento-pix.write&grant_type=client_credentials'
    response = requests.post(
        "https://cdpj.partners.bancointer.com.br/oauth/v2/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        cert=(cert_path, key_path),
        data=request_body
    )
    response.raise_for_status()
    token = response.json().get("access_token")
    if not token:
        raise Exception("Failed to obtain access token from Banco Inter")
    print("Token obtido com sucesso.")
    return token

# Função para carregar o token do arquivo ou obter um novo se necessário
def carregar_token():
    print("Loading token from file or fetching new one.")
    token_path = "C:\\Users\\Scripts\\Inter_API-Chave_e_Certificado\\inter_credenciais.json"
    
    # Tenta carregar o arquivo JSON existente
    try:
        with open(token_path, 'r') as f:
            data = json.load(f)
            token = data.get("token")
            token_time = data.get("time")

            # Verifica se o token ainda é válido
            if token and time.time() - token_time < 3600:
                print("Token is still valid.")
                return token
    except (FileNotFoundError, json.JSONDecodeError):
        print("Token file not found or is invalid.")
    
    # Obtém um novo token
    token = obter_token()
    
    # Atualiza o dicionário com o novo token
    try:
        with open(token_path, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # Se o arquivo não existir ou estiver inválido, inicia um novo dicionário
        data = {}

    # Adiciona ou atualiza o token no JSON existente
    data.update({"token": token, "time": time.time()})

    # Salva as atualizações de volta no arquivo JSON
    with open(token_path, 'w') as f:  # Aqui usamos 'w' para sobrescrever o arquivo com o conteúdo atualizado
        json.dump(data, f, indent=4)

    print("Token saved and fetched.")
    return token

# Obtém os dados da base de dados de solicitação de pagamento
print("Fetching data from Solicitação de Pagamento database")
solicitacao_pagamento_data = get_notion_data(SOLICITACAO_PAGAMENTO_DATABASE_ID)

# Obtém os dados da base de dados bancária
print("Fetching data from Banco de Dados database")
banco_de_dados_data = get_notion_data(BANCO_DE_DADOS_ID)

# Prepara os payloads para enviar os pagamentos
payloads = []
for result in solicitacao_pagamento_data.get('results', []):
    properties = result['properties']
    status = properties.get('Status', {}).get('status', {}).get('name', '')

    # Verifica o status antes de qualquer outra operação
    if status != 'Pgtos em processamento':
        print(f"Item {result['id']} ignorado porque o status não é 'Pgtos em processamento'")
        continue

    valor = properties.get('Valor', {}).get('number', 0.0)
    titulo = get_text_value(properties, 'Título')
    chave_pix_valor = get_property_value(properties, 'Chave Pix')
    conta = get_property_value(properties, 'Conta')
    cpf_cnpj = get_property_value(properties, 'CPF/CNPJ')
    agencia = get_property_value(properties, 'Agência')
    ispb = get_property_value(properties, 'ISPB')
    data_pagamento = properties.get('Data de pagamento', {}).get('date', {}).get('start', '')
    status = properties.get('Status', {}).get('status', {}).get('name', '')
    
    nome_relacionado = properties.get('Fornecedores Cadastrados', {}).get('relation', [])
    nomes = get_relation_names([relation['id'] for relation in nome_relacionado])
    nome = nomes[0] if nomes else ''
    
    print(f"Processing item {result['id']} with status '{status}'")
    

    if status == 'Pgtos em processamento':
        if 'Chave Pix' and chave_pix_valor:
            payload = {
                "valor": str(valor),
                "dataPagamento": data_pagamento,
                "descricao": titulo,
                "destinatario": {
                    "tipo": "CHAVE",
                    "chave": chave_pix_valor
                }
            }
            print(f"Payload criado (Chave Pix): {payload}")
        elif 'Dados Bancários':
            if not chave_pix_valor:  # Garantir que não existe chave Pix
                # Verificar se todos os campos estão presentes e válidos
                if conta and agencia and ispb:
                    payload = {
                        "valor": str(valor),
                        "dataPagamento": data_pagamento,
                        "descricao": titulo,
                        "destinatario": {
                            "tipo": "DADOS_BANCARIOS",
                            "nome": nome,
                            "contaCorrente": conta,
                            "tipoConta": "CONTA_CORRENTE",
                            "cpfCnpj": cpf_cnpj,
                            "agencia": str(agencia),
                            "instituicaoFinanceira": {
                                "ispb": ispb.zfill(8)  # Garantir que o ISPB tenha 8 dígitos
                            }
                        }
                    }
                    print(f"Payload criado (Dados Bancários): {payload}")
                else:
                    print(f"Dados bancários incompletos para o item {result['id']}. Ignorando...")
                    continue
        else:
            print(f"Forma de lançamento inválida ou faltando para o item {result['id']}. Ignorando...")
            continue
        
        payloads.append((json.dumps(payload), result['id'], result['id']))

print("Payloads preparados:", payloads)

# Obtém o token do Banco Inter
token = carregar_token()
print("Token obtido:", token)

# Configura os headers para a requisição de pagamento PIX
headers_pix = {
    'Authorization': f"Bearer {token}",
    'x-conta-corrente': conta_corrente,
    'Content-Type': 'application/json'
}

# Envia os pagamentos para a API do Banco Inter
for payload, item_id, item_id_notion in payloads:
    try:
        print(f"Enviando pagamento de ID_Page: {item_id_notion}")
        response = requests.post(
            "https://cdpj.partners.bancointer.com.br/banking/v2/pix", 
            headers=headers_pix, 
            cert=(cert_path, key_path), 
            data=payload
        )
        response.raise_for_status()  # Garante que a exceção será lançada para status de erro HTTP

        response_data = response.json()  # Pega o JSON da resposta
        print("Resposta do pagamento de Pix:", response_data)

        # Verifica se o pagamento foi aprovado
        if response_data.get('tipoRetorno') == 'APROVACAO':
            print(f"Pagamento aprovado para o item ID {item_id_notion}. Atualizando status...")
            
            # Atualiza status no Notion
            atualizar_status_notion(item_id_notion, "Pgtos em aprovação")
            
            # Insere o ID da transação no Notion
            codigoSolicitacao = response_data.get('codigoSolicitacao')
            if codigoSolicitacao:
                inserir_id_transacao(item_id_notion, codigoSolicitacao)

    except requests.exceptions.HTTPError as errh:
        print("HTTP Error:", errh, response.text)
    except requests.exceptions.ConnectionError as errc:
        print("Error Connecting:", errc)
    except requests.exceptions.Timeout as errt:
        print("Timeout Error:", errt)
    except requests.exceptions.RequestException as err:
        print("Oops: Something Else", err)

# Aguarda a pressão de qualquer tecla para encerrar o script
print("Pressione qualquer tecla para encerrar...")
msvcrt.getch()
import re
from datetime import datetime, timedelta
import requests
from notion_client import Client
# pip install requests notion-client

# Inicializar o cliente Notion
notion = Client(auth="secret_F0IdS4Tes9mqkUpDtL5dtq832slEjdwKOWb495qCxaM")

# Database ID do Notion
database_id = "72d47ee714644ae9a20de5f47d1b89e4"

# Horários
horarios_manha = {
    '1': '07:30',
    '2': '08:20',
    '3': '11:10',
    '4': '12:00',
    '5': '12:50'
}

horarios_tarde = {
    '1': '13:30',
    '2': '14:20',
    '3': '15:20',
    '4': '16:10',
    '5': '17:00',
    '6': '17:10',
    '7': '18:00',
}

# Cada aula possui 50 minutos de duração (10 minutos de intervalo)

# Função para calcular o horário de término da aula
def calcular_horario_fim(horario_inicio, num_periodos):
    fmt = '%H:%M'
    hora_inicio = datetime.strptime(horario_inicio, fmt)
    
    # O tempo total será de 50 minutos por período
    horario_fim = hora_inicio + timedelta(minutes=50 * num_periodos)
    return horario_fim.strftime(fmt)

# Função para extrair dados e criar eventos recorrentes
def criar_eventos_recorrentes():
    # Obter os itens da database
    response = notion.databases.query(database_id=database_id)
    
    # Expressão regular para correspondência do formato
    pattern = r'(\d)([MTN])(\d+)'
    
    # Percorrer os itens da database
    for item in response['results']:
        # Supondo que o texto esteja em uma propriedade chamada "Horário"
        texto_horario = item['properties']['Horário Atual']['rich_text'][0]['text']['content']
        
        # Aplicar a expressão regular
        matches = re.findall(pattern, texto_horario)
        
        # Criar eventos recorrentes com base nos dados extraídos
        for match in matches:
            dia_semana = match[0]
            turno = match[1]
            horarios_aulas = match[2]
            
            # Selecionar o mapeamento de horários adequado com base no turno
            if turno == 'M':
                horarios_turno = horarios_manha
            elif turno == 'T':
                horarios_turno = horarios_tarde
            else:
                continue  # Ignorar turno noturno

            print(f"Matéria: {item['properties']['Nome']['title'][0]['plain_text']}")
            print(f"Horários das aulas: {horarios_aulas}")
            print(f"Horários do turno: {horarios_turno}")

            # Agrupar períodos consecutivos
            i = 0
            while i < len(horarios_aulas):
                periodo_inicial = horarios_aulas[i]
                horario_inicio = horarios_turno[periodo_inicial]

                # Encontrar o último período consecutivo
                while (i + 1 < len(horarios_aulas) and 
                       int(horarios_aulas[i + 1]) == int(horarios_aulas[i]) + 1):
                    i += 1
                
                periodo_final = horarios_aulas[i]
                num_periodos = int(periodo_final) - int(periodo_inicial) + 1
                horario_fim = calcular_horario_fim(horarios_turno[periodo_inicial], num_periodos)
                
                # Criar o evento no calendário do Notion
                """ notion.pages.create(
                    parent={"database_id": "your_calendar_database_id"},
                    properties={
                        "Name": {"title": [{"text": {"content": f"Aula {periodo_inicial}-{periodo_final}"}}]},
                        "Date": {"date": {"start": f"{dia_semana}T{horario_inicio}:00.000Z", "end": f"{dia_semana}T{horario_fim}:00.000Z"}}
                    }
                ) """

                i += 1  # Avançar para o próximo período

                print(f"Horário de início: {horario_inicio}")
                print(f"Horário de término: {horario_fim}")
                print()

# Executar a função
criar_eventos_recorrentes()
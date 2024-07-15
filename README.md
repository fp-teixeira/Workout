# WorkoutAPI

Esta é uma replicação da WorkoutAPI para o desafio "Desenvolvendo sua Primeira API com FastAPI, Python e Docker". 
Para a reprodução do desafio, foram feitas as seguintes alterações: Dispensa do uso de Makefile, uma vez que foi realizado no sistema windows.

# Desafio Final
Como adicional ao desafio que foi feito:

    - adicionar query parameters nos endpoints
        - atleta
            - nome
            - cpf
    - customizar response de retorno de endpoints
        - get all
            - atleta
                - nome
                - centro_treinamento
                - categoria
    - Manipular exceção de integridade dos dados em cada módulo/tabela
        - sqlalchemy.exc.IntegrityError e devolver a seguinte mensagem: “Já existe um atleta cadastrado com o cpf: x”
        - status_code: 303

O que faltou concluir:

    - Adicionar paginação utilizando a lib: fastapi-pagination
        - limit e offset

Problemas no input de parametros de limit e offset. Não foi possível concluir a implementação até o momento.

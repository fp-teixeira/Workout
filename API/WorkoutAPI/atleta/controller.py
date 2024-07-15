from datetime import datetime
from typing import Union
from uuid import uuid4
from fastapi import APIRouter, Body, HTTPException, Query, status
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError  # Adicionando o import do IntegrityError

from WorkoutAPI.atleta.schemas import AtletaIn, AtletaOut, AtletaUpdate
from WorkoutAPI.atleta.models import AtletaModel
from WorkoutAPI.categorias.models import CategoriaModel
from WorkoutAPI.centro_treinamento.models import CentroTreinamentoModel

from WorkoutAPI.contrib.dependencies import DatabaseDependency
from sqlalchemy.future import select

router = APIRouter()

@router.post(
    '/', 
    summary='Criar um novo atleta',
    status_code=status.HTTP_201_CREATED,
    response_model=AtletaOut
)
async def post(
    db_session: DatabaseDependency, 
    atleta_in: AtletaIn = Body(...)
):
    categoria_nome = atleta_in.categoria.nome
    centro_treinamento_nome = atleta_in.centro_treinamento.nome

    categoria = (await db_session.execute(
        select(CategoriaModel).filter_by(nome=categoria_nome))
    ).scalars().first()
    
    if not categoria:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'A categoria {categoria_nome} não foi encontrada.'
        )
    
    centro_treinamento = (await db_session.execute(
        select(CentroTreinamentoModel).filter_by(nome=centro_treinamento_nome))
    ).scalars().first()
    
    if not centro_treinamento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f'O centro de treinamento {centro_treinamento_nome} não foi encontrado.'
        )
    
    try:
        atleta_out = AtletaOut(id=uuid4(), created_at=datetime.utcnow(), **atleta_in.model_dump())
        atleta_model = AtletaModel(**atleta_out.model_dump(exclude={'categoria', 'centro_treinamento'}))

        atleta_model.categoria_id = categoria.pk_id
        atleta_model.centro_treinamento_id = centro_treinamento.pk_id
        
        db_session.add(atleta_model)
        await db_session.commit()
    
    except IntegrityError as e:  
        raise HTTPException(
            status_code=status.HTTP_303_SEE_OTHER, 
            detail=f'Já existe um atleta cadastrado com o cpf: {atleta_in.cpf}'
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail='Ocorreu um erro ao inserir os dados no banco'
        )

    return atleta_out



@router.get(
    '/all', 
    summary='Consultar todos os Atletas',
    status_code=status.HTTP_200_OK,
    response_model=list[dict],
)
async def query(db_session: DatabaseDependency) -> list[dict]:
    atletas: list[AtletaModel] = (await db_session.execute(select(AtletaModel))).scalars().all()
    
    result = []
    for atleta in atletas:
        atleta_dict = {
            'nome': atleta.nome,
            'categoria': atleta.categoria.nome,
            'centro_treinamento': atleta.centro_treinamento.nome
        }
        result.append(atleta_dict)
    
    return result

@router.get(
    '/', 
    summary='Consulta de Atletas',
    status_code=status.HTTP_200_OK,
    response_model=Union[AtletaOut, list[AtletaOut]],
)
async def get_atletas(
    db_session: DatabaseDependency,
    id: UUID4 | None = Query(None, description="ID do atleta para consulta individual"),
    nome: str | None = Query(None, description="Filtrar por nome do atleta"),
    cpf: str | None = Query(None, description="Filtrar por CPF do atleta")
) -> Union[AtletaOut, list[AtletaOut]]:
    if id:
        # Consulta por ID
        atleta = (
            await db_session.execute(select(AtletaModel).filter_by(id=id))
        ).scalars().first()

        if not atleta:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=f'Atleta não encontrado no id: {id}'
            )
        
        return atleta
    else:
        # Consulta por parâmetros de filtro
        query = select(AtletaModel)
        
        if nome:
            query = query.filter(AtletaModel.nome.ilike(f"%{nome}%"))
            
        if cpf:
            query = query.filter(AtletaModel.cpf == cpf)

        atletas: list[AtletaOut] = (await db_session.execute(query)).scalars().all()
        
        return [AtletaOut.model_validate(atleta) for atleta in atletas]


@router.patch(
    '/{id}', 
    summary='Editar um Atleta pelo id',
    status_code=status.HTTP_200_OK,
    response_model=AtletaOut,
)
async def patch(id: UUID4, db_session: DatabaseDependency, atleta_up: AtletaUpdate = Body(...)) -> AtletaOut:
    atleta = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    atleta_update = atleta_up.model_dump(exclude_unset=True)
    for key, value in atleta_update.items():
        setattr(atleta, key, value)

    await db_session.commit()
    await db_session.refresh(atleta)

    return atleta


@router.delete(
    '/{id}', 
    summary='Deletar um Atleta pelo id',
    status_code=status.HTTP_204_NO_CONTENT
)
async def delete(id: UUID4, db_session: DatabaseDependency) -> None:
    atleta = (
        await db_session.execute(select(AtletaModel).filter_by(id=id))
    ).scalars().first()

    if not atleta:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail=f'Atleta não encontrado no id: {id}'
        )
    
    await db_session.delete(atleta)
    await db_session.commit()
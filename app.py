import time
import os
from dotenv import load_dotenv
load_dotenv()
from typing import List, Dict
from fastapi import FastAPI,Depends,APIRouter, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
from astrapy.db import AstraDB

ASTRA_DB_API_ENDPOINT      = os.environ.get("ASTRA_DB_API_ENDPOINT", "")
ASTRA_DB_APPLICATION_TOKEN = os.environ.get("ASTRA_DB_APPLICATION_TOKEN", "")
ASTRA_DB_KEYSPACE          = os.environ.get("ASTRA_DB_KEYSPACE", "vector")
ASTRA_DB_COLLECTION        = os.environ.get("ASTRA_DB_COLLECTION", "fr_site")
ASTRA_DB_DIMENSION         = os.environ.get("ASTRA_DB_DIMENSION", 768)
ASTRA_DB_METRIC            = os.environ.get("ASTRA_DB_METRIC", "cosine")
ASTRA_DB_LIMIT             = os.environ.get("ASTRA_DB_LIMIT", 10)
EXPECTED_POST_TOKEN        = os.environ.get("EXPECTED_POST_TOKEN", "test")
MODEL_NAME                 = os.environ.get("MODEL_NAME", "dangvantuan/sentence-camembert-base")

db = AstraDB(token=ASTRA_DB_APPLICATION_TOKEN,api_endpoint=ASTRA_DB_API_ENDPOINT)

try:
    collection = db.collection(ASTRA_DB_COLLECTION)
    print(f"Connected to Astra DB: {db.get_collections()}")
except:
    print(f"Not Connected to Astra DB: {db.get_collections()}")
    pass


model = SentenceTransformer("dangvantuan/sentence-camembert-base", device='cpu')


class EmbeddingRequest(BaseModel):
    texts: List[str]

class EmbeddingResponse(BaseModel):
    embeddings: List[List[float]]

class SearchResponse(BaseModel):
    results: List[Dict]


def verify_post_token(post_token: str  = "")-> bool :
    print("verify token :" , post_token)
    expected_token = EXPECTED_POST_TOKEN
    if post_token == expected_token:
        print("token is TRUE")
        return True
    else:
        return False
    
def anonymize_value(value: str) -> str:
    value = str(value)
    if not value:
        return value
    length = max(3, int(len(value) * 0.3))  
    return f"{value[:length]}***"
    
def anonymize_result(result: Dict, correct_token: bool) -> Dict:
    print('correct_token',correct_token)
    if not correct_token:
        return {key: anonymize_value(value) for key, value in result.items()}
    else:
        return result


app = FastAPI(
    title="LLM SEARCH API",
    description="Découvrez la puissance des données LLM grâce à la similarité cosinus dans l'analyse et plusieurs méthodes de recherche de texte.",
    version="1.0.0",
    docs_url="/",
)


test = APIRouter()

@test.get("/health")
async def heathcheck():
    return {"status": "ok"}

@test.get("/test_migration")
async def migration()-> bool:
    start          = time.time()
    return True

@test.get("/test_suite")
async def migration()-> bool:
    start          = time.time()
    return True


@test.post("/embed")
async def embed(request: EmbeddingRequest) -> EmbeddingResponse:
    start = time.time()
    embeddings = model.encode(request.texts, normalize_embeddings=True)
    print(f'embedded {len(request.texts)} texts in {(time.time() - start):.2f} seconds')
    return EmbeddingResponse(embeddings=embeddings.tolist())


app.include_router(test, prefix="/test", tags=["Tests"])


search = APIRouter()

@search.post("/cosine_score")
async def cosine_score(limit: int, request: EmbeddingRequest, post_token: str = Depends(verify_post_token))-> SearchResponse:
    start          = time.time()
    embeddings     = model.encode(request.texts, normalize_embeddings=True)
    query          = embeddings.tolist()[0]

    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = ASTRA_DB_LIMIT

    results        = collection.vector_find(
                        query, 
                        limit=limit, 
                        fields={"URL","Email","ContactPage","Title"}
                    )
    
    results_list   = [anonymize_result(result, post_token) for result in results]
    
    print(f'embedded + astra {len(request.texts)} texts in {(time.time() - start):.2f} seconds')

    return SearchResponse(results=results_list)

@search.post("/like_by_keyword_score")
async def like_by_keyword_score(limit: int, request: EmbeddingRequest, post_token: str = Depends(verify_post_token))-> SearchResponse:
    start          = time.time()
    embeddings     = model.encode(request.texts, normalize_embeddings=True)
    query          = embeddings.tolist()[0]

    try:
        limit = int(limit)
    except (ValueError, TypeError):
        limit = ASTRA_DB_LIMIT

    results        = collection.vector_find(
                        query, 
                        limit=limit, 
                        fields={"URL","Email","ContactPage","Title"}
                    )
    
    results_list   = [anonymize_result(result, post_token) for result in results]
    
    print(f'embedded + astra {len(request.texts)} texts in {(time.time() - start):.2f} seconds')

    return SearchResponse(results=results_list)


app.include_router(search, prefix="/search", tags=["Search"])


admin = APIRouter()

@admin.patch("/pre_processing")
async def fine_tune()-> bool:
    start          = time.time()
    return True

@admin.post("/insert")
async def insert()-> bool:
    start          = time.time()
    return True

@admin.patch("/update")
async def update()-> bool:
    start          = time.time()
    return True

@admin.patch("/fine_tune")
async def fine_tune()-> bool:
    start          = time.time()
    return True

app.include_router(admin, prefix="/admin", tags=["Administration"])


contact = APIRouter()

@contact.get("/bot_auto_form")
async def bot_auto_contact()-> bool:
    start          = time.time()
    return True

@contact.post("/send_mail")
async def mailjet_send()-> bool:
    start          = time.time()
    return True

app.include_router(contact, prefix="/contact", tags=["Contact"])


import uuid
from typing import Annotated

from fastapi import FastAPI, Query, HTTPException, Path

from db import redis_client

from utils import get_prime_factors


app = FastAPI()

@app.post("/values")
async def write_value(value: Annotated[int, Path(title="Min value is 2", lt=2)], ttl: int = Query(None)):
    prime_factors = get_prime_factors(value)
    value_id = str(uuid.uuid4())
    redis_client.sadd(value_id, *prime_factors)
    if ttl:
        redis_client.expire(value_id, ttl)
    return {"value_id": value_id}


@app.get("/values/{prime_factor}")
async def get_values(prime_factor: int):
    values = []
    for key in redis_client.scan_iter():
        if redis_client.sismember(key, prime_factor):
            values.append(int(key))
    if not values:
        raise HTTPException(status_code=404, detail="No values found")
    return {"values": values}

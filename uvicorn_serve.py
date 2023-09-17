import uvicorn

if __name__ == "__main__":
    uvicorn.run("webhook:app", host="0.0.0.0", port=8008, log_level="info")

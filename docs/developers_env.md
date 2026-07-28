# Run local

Install python
Create virtual env (recomended)

Run local in developer debug mode

    litestar run --reload --debug

Or run local

    litestar run --reload 
    
or

    uvicorn app:app --port 8000 --host 127.0.0.1

Litestar or uvicorn is equivalent, couse litestar runs the uvicorn.

See `.env.example` file for example.

# Prepare prod

Copy `.env.example` to `.env` file and set up your production settings.
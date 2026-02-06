from fastapi import FastAPI, Request, Form, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import engine, Message, create_db_and_tables
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan)
templates = Jinja2Templates(directory="templates")


def get_session():
    with Session(engine) as session:
        yield session


@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request, session: Session = Depends(get_session)):
    messages = session.exec(select(Message).order_by(Message.id.desc())).all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "messages": messages}
    )


@app.post("/submit", response_class=HTMLResponse)
async def submit_message(
    request: Request, content: str = Form(...), session: Session = Depends(get_session)
):
    message = Message(content=content)
    session.add(message)
    session.commit()
    session.refresh(message)

    # Reload the list to show the new message
    messages = session.exec(select(Message).order_by(Message.id.desc())).all()
    return templates.TemplateResponse(
        "index.html", {"request": request, "messages": messages}
    )

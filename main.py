from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select
from database import engine, Reservation, create_db_and_tables
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
    reservations = session.exec(select(Reservation)).all()

    # Organize data for the dashboard: by room, then by time
    # Rooms: Meeting Room A, Meeting Room B
    # Hours: 9 to 18
    rooms = ["Meeting Room A", "Meeting Room B"]
    hours = range(9, 19)  # 9, 10, ... 18

    # Create a grid structure
    # grid[room][hour] = Reservation or None
    grid = {room: {h: None for h in hours} for room in rooms}

    for r in reservations:
        if r.room_name in grid:
            # Simple assumption: 1 hour slots for visualization
            if r.start_time in grid[r.room_name]:
                grid[r.room_name][r.start_time] = r

    return templates.TemplateResponse(
        "index.html", {"request": request, "rooms": rooms, "hours": hours, "grid": grid}
    )


@app.post("/reserve", response_class=HTMLResponse)
async def make_reservation(
    request: Request,
    reserver_name: str = Form(...),
    room_name: str = Form(...),
    start_time: int = Form(...),
    session: Session = Depends(get_session),
):
    # Basic validation: Check if already booked
    end_time = start_time + 1  # Default to 1 hour

    existing = session.exec(
        select(Reservation)
        .where(Reservation.room_name == room_name)
        .where(Reservation.start_time == start_time)
    ).first()

    if existing:
        # For simplicity, just return to index with a failure message query param?
        # Or render error page. Let's just redirect for now.
        return RedirectResponse(url="/?error=already_booked", status_code=303)

    reservation = Reservation(
        reserver_name=reserver_name,
        room_name=room_name,
        start_time=start_time,
        end_time=end_time,
    )
    session.add(reservation)
    session.commit()

    return RedirectResponse(url="/", status_code=303)

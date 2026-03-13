from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import secrets
import os
from app.utils.email import send_confirmation_email
from app.api import product  # Ajusta si tu router está en otra carpeta

app = FastAPI()

# Middleware CORS: por si móvil bloquea cookies/localStorage en desarrollo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Solo para desarrollo, restringe en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Seguridad básica
security = HTTPBasic()
ADMIN_USER = "admin"
ADMIN_PASS = "1234"

def verify_credentials(credentials: HTTPBasicCredentials = Depends(security)):
    if not (secrets.compare_digest(credentials.username, ADMIN_USER) and
            secrets.compare_digest(credentials.password, ADMIN_PASS)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

# Archivos estáticos
app.mount("/admin/static", StaticFiles(directory="app/static"), name="static_admin")
app.mount("/static", StaticFiles(directory="app/static"), name="static_public")

# Panel de admin
@app.get("/admin", response_class=HTMLResponse)
def admin_panel(username: str = Depends(verify_credentials)):
    with open("app/static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Página principal pública (hero)
@app.get("/", response_class=HTMLResponse)
def home_page():
    with open("app/static/home.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Página de catálogo de productos
@app.get("/tienda", response_class=HTMLResponse)
def public_products_page():
    with open("app/static/public.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Página de resumen de compra
@app.get("/shop", response_class=HTMLResponse)
def serve_shop():
    with open(os.path.join("app", "static", "shop.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())

# Endpoint de compra
@app.post("/checkout")
async def checkout(request: Request):
    data = await request.json()
    email = data.get("email")
    cart = data.get("cart", [])

    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Correo electrónico no válido")

    print(f"🛒 Pedido de {email}:")
    for item in cart:
        print(f"  - {item['name']} ({item['price']} €)")

    send_confirmation_email(email, cart)

    return {"message": "Pedido recibido"}

# Rutas de productos (API REST de productos)
app.include_router(product.router)

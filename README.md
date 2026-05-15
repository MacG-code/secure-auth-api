# 🔐 Secure Authentication API

API de autenticación segura desarrollada con Django REST Framework, enfocada en seguridad, autenticación JWT y buenas prácticas backend.

## 🚀 Caracteristicas
### ​✅​ Autenticacion
- Registro de usuarios
- Login con JWT
- Logout con blascklist de tokens
- Refresh tokens
- Verificacion de email
- Reset de contraseña

### 🔐 Seguridad
- Hash seguro de contraseñas
- Roles y permisos
- Protección con JWT
- Tokens blacklist
- Variables de entorno con `.env`

### 👤 Gestión de usuarios
- Usuarios personalizados
- Roles (`admin`, `user`)
- Protección de rutas privadas

## 🛠️ Tecnologías

- Python
- Django
- Django REST Framework
- PostgreSQL
- JWT (SimpleJWT)
- SMTP Gmail
- python-decouple

##  📂 Estructura del proyecto

```bash
secure_auth_api/
│
├── accounts/
├── config/
├── manage.py
├── requirements.txt
├── .env.example
└── README.md
```

## 🔑 Endpoints principales

| Método | Endpoint                                | Descripción     |
| ------ | --------------------------------------- | --------------- |
| POST   | `/api/register/`                        | Registro        |
| POST   | `/api/login/`                           | Login           |
| POST   | `/api/logout/`                          | Logout          |
| POST   | `/api/token/refresh/`                   | Refresh token   |
| GET    | `/api/profile/`                         | Perfil usuario  |
| POST   | `/api/request-password-reset/`          | Solicitar reset |
| POST   | `/api/reset-password/<uidb64>/<token>/` | Reset password  |
| GET    | `/api/verify-email/<token>/`            | Verificar email |

## 📌 Estado del proyecto

  ⚠️​ EN DESARROLLO ACTIVO!!! ⚠️​


## ⚙️ Instalación
###  Clonar repositorio
```bash
git clone https://github.com/MacG-code/secure-auth-api.git
cd secure-auth-api
pip install -r requirements.txt
```

### Entorno virtual
```bash
python -m venv venv
```
#### Windows
```bash
venv\Scripts\activate
```
#### Linux/Mac
```bash
source venv/bin/activate
```

### Instalar dependencias
```bash
pip install -r requirements.txt
```

### Ejecutar servidor
```bash
python manage.py runserver
```


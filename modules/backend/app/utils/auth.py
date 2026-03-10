from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer
from fastapi import HTTPException, Depends

SECRET_KEY = "mysecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

# Criptografia de senhas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

class AuthUtils:
    @staticmethod
    def verify_password(plain_password, hashed_password):
        """Verifica a senha usando o hash armazenado."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password):
        """Gera o hash da senha."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: timedelta = None):
        """Cria o token JWT com a data de expiração."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc)   + expires_delta  # Alterado para utcnow()
        else:
            expire = datetime.now(timezone.utc)  + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str):
        """Decodifica o token JWT e retorna o payload."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise Exception("Token inválido ou expirado.")
        except Exception as e:
            raise Exception(f"Erro ao decodificar o token: {str(e)}")

    @staticmethod
    def get_user_from_token(token: str):
        """Extrai o usuário do token JWT, normalmente utilizado para acessar dados do usuário autenticado."""
        payload = AuthUtils.decode_access_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token or expired")
        return username
    

    @staticmethod
    def get_current_data_from_token(token: str = Depends(oauth2_scheme)):
        """Decodifica o token JWT e retorna todas as informações contidas nele."""
        try:
            payload = AuthUtils.decode_access_token(token)  # Decodifica o token
            if not payload:  # Verifica se há dados no token
                raise HTTPException(status_code=401, detail="Invalid token or expired")
            return payload  # Retorna o dicionário completo
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    
    # @staticmethod
    # def get_current_user(token: str = Depends(oauth2_scheme)):
    #     """Decodifica o token JWT e retorna o usuário."""
    #     try:
    #         payload = AuthUtils.decode_access_token(token)
    #         username = payload.get("sub")
    #         if not username:
    #             raise HTTPException(status_code=401, detail="Invalid token or expired")
    #         return username
    #     except Exception as e:
    #         raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")
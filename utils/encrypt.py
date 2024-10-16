from passlib.context import CryptContext

PasswordEncrypt = CryptContext(schemes=["bcrypt"], deprecated="auto")

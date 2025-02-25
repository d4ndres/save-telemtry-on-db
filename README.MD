# Instrucciones para ejecutar el proyecto

## 1. Correr Docker Compose

Para iniciar los servicios con Docker Compose, ejecuta el siguiente comando en la terminal:

```sh
docker-compose up
```

## 2. Crear el archivo `.env`

Es necesario crear un archivo `.env` en la raíz del proyecto basado en `example.env`. Puedes copiar el archivo y renombrarlo:

```sh
cp example.env .env
```

## 3. Activar un entorno virtual

Para activar un entorno virtual en Python, sigue estos pasos:

### En Windows

```sh
python -m venv venv
.\venv\Scripts\activate
```

### En macOS y Linux

```sh
python3 -m venv venv
source venv/bin/activate
```

## 4. Instalar dependencias

Con el entorno virtual activado, instala las dependencias listadas en `requirements.txt`:

```sh
pip install -r requirements.txt
```

## 5. Correr el archivo `main.py`

Finalmente, para ejecutar el archivo `main.py`, usa el siguiente comando:

```sh
python main.py
```

# Proyecto 1: Chat-Bot mediante Socket en Python.

Para correr el modelo cliente-servidor es necesario correr una terminal para el servidor, n para clientes y m para
ejecutivos, en cada una de estas es sugerido abrir el virtual environment de python 3.10, que posee todas las librerías
necesarias para poder correr el proyecto, sobre todo por las librerías de NLP.

Una vez abiertas las líneas de comando apuntando a la carpeta del proyecto, se debe correr el ambiente con el comando
``` .\venv\Scripts\activate``` en cada una de ellas. En caso de existir errores, siempre se puede correr con el intéprete
de la máquina del usuario haciendo ```pip install torch ```, ```pip install numpy```, ```pip install nltk``` y descomentar
```#nltk.download('punkt')``` en nltk_utils.py la primera vez que se corre el código, para descargar un paquete adicional para
el modelo de NLP.

Luego de esto, es posible iniciar la conexión con el servidor de la forma usual, entregando el RUT y el usuario, para clientes
nuevos, o el RUT para clientes antiguos. En el caso del ejecutivo, este solo podrá ingresar si posee un RUT válido de ejecutivo.

Integrantes: 

- Benjamín Brito
- Sebastián Guzmán
- Diego Sanz

Curso EL4112-1 - Otoño 2022 - Principios de Comunicaciones
# Keylogger con Python + scripting

## Tutorial

### Pasos básicos

1. Crea un entorno virtual para tu proyecto de Python
2. Instala la librería pynput para manejar la entrada de teclado (o si prefieres utilizar otra, la que sea). Asegurate de estar en el entorno virtual!
3. Crea un archivo main.py e importa la librería de teclado
4. Crea una función que procese la pulsación de una tecla y la escriba en un archivo
5. Crea una función que permita salir del programa (opcional)
6. Crea la función main para el programa y escucha en bucle la pulsación de teclas
7. Crea un script en bash que mueva el archivo a una ruta oculta, le cambie el nombre y lo ejecute en segundo plano

### Pasos extra
8. Envía periódicamente el archivo que registra las teclas a través de la red
9. Modifica el script de bash para que modifique el nombre del proceso en el task manager

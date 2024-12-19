import csv
import unicodedata
import tt_kmeans  # Asegúrate de importar el módulo corregido

# Función para normalizar etiquetas (evitar diferencias por mayúsculas/acentos)
def normalizar_etiqueta(texto):
    texto = texto.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

# Archivos de entrada
archivo_lexicon = "SEL.csv"
archivo_pruebas = "pruebas.csv"

# Cargar centroides desde el archivo léxico
centroides = tt_kmeans.centroidesCSV(archivo_lexicon)

# Variables para almacenar resultados
y_true = []
y_pred = []
frases = []
otros = []  # Frases que no contienen palabras del léxico
vocabulario = set(palabra for c in centroides.values() for palabra in c)

# Leer y procesar el archivo de pruebas
with open(archivo_pruebas, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        frase = row['frase'].strip()
        sentimiento_real = normalizar_etiqueta(row['sentimiento'])

        # Analizar el sentimiento usando TT_KMEANS
        sentimiento_predicho, _, detalles = tt_kmeans.analizarSentimiento(frase, centroides)
        sentimiento_predicho = normalizar_etiqueta(sentimiento_predicho)

        # Verificar si la frase tiene palabras en el léxico
        palabras = tt_kmeans.tokenizar(frase)
        tiene_palabras = any(palabra in vocabulario for palabra in palabras)
        
        if tiene_palabras:
            y_true.append(sentimiento_real)
            y_pred.append(sentimiento_predicho)
        else:
            # Asignar "otros" si no tiene palabras relevantes
            y_true.append(sentimiento_real)
            y_pred.append("otros")
            otros.append(frase)

        frases.append((frase, sentimiento_real, sentimiento_predicho))

# Crear etiquetas (clases) y agregar "otros"
etiquetas = sorted(set(y_true))
if "otros" not in etiquetas:
    etiquetas.append("otros")
indice = {et: i for i, et in enumerate(etiquetas)}

# Construir la matriz de confusión
n = len(etiquetas)
matriz_confusion = [[0 for _ in range(n)] for _ in range(n)]

for real, pred in zip(y_true, y_pred):
    i = indice[real]
    j = indice[pred]
    matriz_confusion[i][j] += 1

# Calcular exactitud
aciertos = sum(matriz_confusion[i][i] for i in range(n))
total = len(y_true)
exactitud = aciertos / total if total > 0 else 0.0

# Mostrar resultados
print("\nMatriz de Confusión:")
print("       " + " ".join(f"{et:>10}" for et in etiquetas))
for i, fila in enumerate(matriz_confusion):
    print(f"{etiquetas[i]:>10} " + " ".join(f"{val:>10}" for val in fila))

print("\nExactitud del modelo: {:.2f}%".format(exactitud * 100))
print("Frases con palabras del léxico:", len(y_true) - len(otros))
print("Frases sin palabras en el léxico:", len(otros))

# Mostrar frases sin palabras relevantes
if otros:
    print("\nFrases sin palabras en el léxico:")
    for frase in otros:
        print(f" - {frase}")

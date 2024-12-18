import csv
import unicodedata
import tt_kmeans

def normalizar_etiqueta(texto):
    texto = texto.lower().strip()
    return ''.join(c for c in unicodedata.normalize('NFD', texto) if unicodedata.category(c) != 'Mn')

archivo_lexicon = "SEI_LEXICON_TT_033.csv"
archivo_pruebas = "pruebas.csv"

centroides = tt_kmeans.centroidesCSV(archivo_lexicon)

y_true = []
y_pred = []
frases = []
count = 0
count2 = 0

# Contador para frases con palabras del léxico
count_palabras = 0

# Leer el CSV y predecir
with open(archivo_pruebas, mode='r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        frase = row['frase'].strip()
        sentimiento_real = normalizar_etiqueta(row['sentimiento'])

        # Analizar el sentimiento
        sentimiento_predicho, _ = tt_kmeans.analizarSentimiento(frase, centroides)
        sentimiento_predicho = normalizar_etiqueta(sentimiento_predicho)

        y_true.append(sentimiento_real)
        y_pred.append(sentimiento_predicho)
        frases.append((frase, sentimiento_real, sentimiento_predicho))

etiquetas = sorted(list(set(y_true)))
# Añadimos la etiqueta 'otros' al final
etiquetas.append("otros")

# Creamos índice para las etiquetas (incluyendo otros)
indice = {et: i for i, et in enumerate(etiquetas)}

# Lista para almacenar aquellas frases que no tengan palabras con peso en el léxico
otros = []

vocabulario = set(palabra for c in centroides.values() for palabra in c)

# Aquí generamos nuevas listas tomando en cuenta que ahora "otros" estará en la matriz
y_true_filtrado = []
y_pred_filtrado = []

for (frase, real, pred) in frases:
    palabras = tt_kmeans.tokenizar(frase)
    # Verificamos si hay alguna palabra del vocabulario
    tiene_palabras = any(palabra in vocabulario for palabra in palabras)
    
    if tiene_palabras:
        # Si tiene palabras del léxico, la contamos normalmente
        y_true_filtrado.append(real)
        y_pred_filtrado.append(pred)
        count_palabras += 1  # Incrementamos el contador
    else:
        # Si no tiene palabras, lo contamos como "otros"
        y_true_filtrado.append(real)
        y_pred_filtrado.append("otros")
        otros.append(frase)

n = len(etiquetas)
matriz_confusion = [[0 for _ in range(n)] for _ in range(n)]

for real, pred in zip(y_true_filtrado, y_pred_filtrado):
    i = indice[real]
    j = indice[pred]
    matriz_confusion[i][j] += 1

aciertos = sum(matriz_confusion[i][i] for i in range(n))
total = len(y_true_filtrado)
exactitud = aciertos / total if total > 0 else 0.0

print("\nMatriz de Confusión:")
print("       " + " ".join(f"{et:>10}" for et in etiquetas))
for i, fila in enumerate(matriz_confusion):
    print(f"{etiquetas[i]:>10} " + " ".join(f"{val:>10}" for val in fila))

print("\nExactitud del modelo: {:.2f}%".format(exactitud * 100))

# Imprimir cuántas frases tuvieron palabras del léxico
print("Frases con palabras del léxico:", count_palabras)

# Al final imprimimos cuántas quedaron en 'otros'
if otros:
    for f in otros:
        count += 1
    print('Frases sin palabras en el lexico:', count)

import math
import csv
import unicodedata

# Normalizar palabras (quitar acentos y convertir a minúsculas)
def normalizar(palabra):
    return ''.join(c for c in unicodedata.normalize('NFD', palabra) if unicodedata.category(c) != 'Mn').lower().strip()

# Función para calcular la distancia euclidiana
def distanciaEuclidiana(vectorTexto, vector):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(vectorTexto, vector)))

# Cargar centroides desde el archivo CSV
def centroidesCSV(archivo_csv):
    centroides = {}
    with open(archivo_csv, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for fila in reader:
            sentimiento = fila['Categoria'].strip()
            palabra = normalizar(fila['Palabra'])
            peso = float(fila['PFA'])
            if sentimiento not in centroides:
                centroides[sentimiento] = {}
            centroides[sentimiento][palabra] = peso
    return centroides

# Eliminar stopwords y tokenizar
def tokenizar(texto):
    stopwords = {"de", "el", "la", "y", "en", "a", "los", "las", "por", "con", "del", "al", "que", "un", "una", "este", "esta", "es", "muy"}
    texto = texto.translate(str.maketrans("", "", ".,:;¡¿!?\"'()[]{}"))
    palabras = texto.lower().split()
    palabrasFiltradas = [normalizar(palabra) for palabra in palabras if palabra not in stopwords]
    return palabrasFiltradas

# Convertir un texto a vector y obtener detalles de las palabras
def textoVectorDetalles(texto, centroides):
    palabras = tokenizar(texto)
    vocabulario = list(set(palabra for c in centroides.values() for palabra in c))
    vector = []
    detalles = []

    for palabra in vocabulario:
        peso = sum(centroides[sentimiento].get(palabra, 0) for sentimiento in centroides)
        frecuencia = palabras.count(palabra)
        contribucion = frecuencia * peso
        vector.append(contribucion)
        
        if contribucion > 0:
            detalles.append({
                "palabra": palabra,
                "frecuencia": frecuencia,
                "peso": peso,
                "contribucion": contribucion,
                "sentimientos": [sent for sent, centroide in centroides.items() if palabra in centroide]
            })

    return vector, detalles

# Analizar el sentimiento del texto
def analizarSentimiento(texto, centroides):
    _, detalles = textoVectorDetalles(texto, centroides)

    # Calcular contribuciones acumuladas por sentimiento
    contribucionesPorSentimiento = {sentimiento: 0 for sentimiento in centroides}
    for d in detalles:
        for sentimiento in d["sentimientos"]:
            contribucionesPorSentimiento[sentimiento] += d["contribucion"]

    # Normalizar las contribuciones a porcentajes
    totalContribuciones = sum(contribucionesPorSentimiento.values())
    porcentaje = {sentimiento: (contrib / totalContribuciones) * 100 if totalContribuciones > 0 else 0.0
                  for sentimiento, contrib in contribucionesPorSentimiento.items()}

    # Determinar el sentimiento dominante
    sentimientoDominante = max(porcentaje, key=porcentaje.get)
    return sentimientoDominante, porcentaje, detalles


# Programa principal
if __name__ == "__main__":
    archivo_csv = "SEL.csv" 
    texto = input("Escribe una frase para analizar su sentimiento: ")

    # Cargar los centroides desde el archivo CSV
    centroides = centroidesCSV(archivo_csv)

    # Analizar el sentimiento del texto
    sentimientoDominante, porcentaje, detalles = analizarSentimiento(texto, centroides)

    print(f"\nTexto analizado: {texto}")
    print(f"Sentimiento dominante: {sentimientoDominante}")
    print("\nPorcentajes de sentimientos:")
    for s, p in porcentaje.items():
        print(f"{s}: {p:.2f}%")

    print("\nDetalles de las palabras que contribuyeron:")
    for d in detalles:
        print(f"Palabra: {d['palabra']}, Frecuencia: {d['frecuencia']}, Peso: {d['peso']:.3f}, "
              f"Contribución: {d['contribucion']:.3f}, Sentimientos: {', '.join(d['sentimientos'])}")

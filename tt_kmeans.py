import math
import csv
import unicodedata

def normalizar(palabra):
    return ''.join(c for c in unicodedata.normalize('NFD', palabra) if unicodedata.category(c) != 'Mn').lower().strip()

# Función para calcular la distancia euclidiana
def distanciaEuclidiana(vectorTexto, vector):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(vectorTexto, vector)))

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

def tokenizar(texto):
    stopwords = {"de", "el", "la", "y", "en", "a", "los", "las", "por", "con", "del", "al", "que", "un", "una", "este", "esta", "es", "muy"}
    texto = texto.translate(str.maketrans("", "", ".,:;¡¿!?\"'()[]{}"))
    palabras = texto.lower().split()
    palabrasFiltradas = [normalizar(palabra) for palabra in palabras if palabra not in stopwords]
    return palabrasFiltradas

# Convertir un texto a un vector basado en los centroides
def textoVector(texto, centroides):
    palabras = tokenizar(texto)
    vocabulario = set(palabra for c in centroides.values() for palabra in c)
    vector = []
    for palabra in vocabulario:
        peso = sum(centroides[sentimiento].get(palabra, 0) for sentimiento in centroides)
        frecuencia = palabras.count(palabra)
        vector.append(frecuencia * peso)
    return vector

# Determinar el sentimiento dominante y devolver porcentajes
def analizarSentimiento(texto, centroides):
    vectorTexto = textoVector(texto, centroides)
    # print("\nVector del texto:", vectorTexto)

    # Convertimos cada sentimiento en su vector correspondiente
    vectoresSentimientos = {
        sentimiento: textoVector(" ".join(centroide.keys()), centroides)
        for sentimiento, centroide in centroides.items()
    }
    # distancia euclidiana entre el texto y cada sentimiento
    distancias = {
        sentimiento: distanciaEuclidiana(vectorTexto, vector)
        for sentimiento, vector in vectoresSentimientos.items()
    }
    print("\nDistancias euclidianas:", distancias)

    maxDistancia = max(distancias.values())
    similitudesEuclidiana = {sentimiento: maxDistancia - distancia for sentimiento, distancia in distancias.items()}
    print("Similitudes euclidianas invertidas:", similitudesEuclidiana)

    # Convertir similitudes euclidianas a porcentajes
    totalSimilitudesEuclidiana = sum(similitudesEuclidiana.values())
    if totalSimilitudesEuclidiana == 0:
        print("\nNo se encontraron palabras relevantes en el texto.")
        porcentajeEuclidiana = {sentimiento: 0.0 for sentimiento in centroides.keys()}
    else:
        porcentajeEuclidiana = {sentimiento: (similitud / totalSimilitudesEuclidiana) * 100
                                for sentimiento, similitud in similitudesEuclidiana.items()}

    # Encontrar el sentimiento dominante
    sentimientoDominanteEuclidiana = max(porcentajeEuclidiana, key=porcentajeEuclidiana.get)

    return sentimientoDominanteEuclidiana, porcentajeEuclidiana

# Programa principal
if __name__ == "__main__":
    archivo_csv = "SEL.csv"  
    texto = input("Escribe una frase para analizar su sentimiento: ") 
    # Cargar los centroides desde el archivo CSV
    centroides = centroidesCSV(archivo_csv)
    
    # Analizar el sentimiento del texto
    sentimientoEuc, porcentajeEuc = analizarSentimiento(texto, centroides)
    
    print(f"\nTexto analizado: {texto}")
    print(f"\nSentimiento dominante (Euclidiana): {sentimientoEuc}")
    print("\nPorcentajes:")
    for s, p in porcentajeEuc.items():
        print(f"{s}: {p:.2f}%")

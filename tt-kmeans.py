import math

# Función para calcular la distancia euclidiana
def distanciaEuclidiana(vectorTexto, vector):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(vectorTexto, vector)))

# Crear vectores representativos (centroides) para cada sentimiento
centroides = {
    "Alegría": {"feliz": 1.0, "contento": 0.8, "risa": 1.2, "amor": 0.9},
    "Tristeza": {"triste": 1.0, "llorar": 1.1, "solitario": 0.9, "perdido": 0.8},
    "Enojo": {"furioso": 1.0, "ira": 1.2, "enfado": 0.9, "molesto": 1.0},
    "Miedo": {"asustado": 1.0, "pánico": 1.2, "temor": 0.9, "inseguro": 1.1}
}

def tokenizar(texto):
    # Lista de palabras comunes a eliminar (stopwords)
    stopwords = {"de", "el", "la", "y", "en", "a", "los", "las", "por", "con", "del", "al", "que", "un", "una", "este", "esta", "es", "muy"}
    
    # Dividimos el texto en palabras, convertimos a minúsculas y filtramos
    palabras = texto.lower().split()
    palabrasFiltradas = [palabra for palabra in palabras if palabra not in stopwords]
    return palabrasFiltradas


# Convertir un texto a un vector basado en los centroides
def textoVector(texto, centroides):
    palabras = tokenizar(texto)
    vocabulario = set(palabra for c in centroides.values() for palabra in c)
    vector = []
    for palabra in vocabulario:
        peso = sum(centroides[sentimiento].get(palabra, 0) for sentimiento in centroides)
        frecuencia = palabras.count(palabra)  # Frecuencia en el texto
        vector.append(frecuencia * peso)  # Ponderación
    return vector

# Determinar el sentimiento dominante y devolver porcentajes
def analizarSentimiento(texto, centroides):

    vectorTexto = textoVector(texto, centroides)
    
    # Convertimos cada sentimiento en su vector correspondiente
    vectoresSentimientos = {
        sentimiento: textoVector(" ".join(centroide.keys()), centroides)
        for sentimiento, centroide in centroides.items()
    }
    
    # Calculamos la distancia euclidiana entre el texto y cada sentimiento
    distancias = {
        sentimiento: distanciaEuclidiana(vectorTexto, vector)
        for sentimiento, vector in vectoresSentimientos.items()
    }
    
    # Invertir distancias para convertirlas en similitud
    maxDistancia = max(distancias.values())
    similitudes = {sentimiento: maxDistancia - distancia for sentimiento, distancia in distancias.items()}
    
    # Convertir a porcentajes
    totalSimilitudes = sum(similitudes.values())
    porcentaje = {sentimiento: (similitud / totalSimilitudes) * 100 for sentimiento, similitud in similitudes.items()}
    
    # Encontrar el sentimiento dominante
    sentimientoDominante = max(porcentaje, key=porcentaje.get)
    return sentimientoDominante, porcentaje

# Programa principal
if __name__ == "__main__":
    texto = input("Escribe una frase para analizar su sentimiento: ")
    sentimiento, porcentaje = analizarSentimiento(texto, centroides)
    
    print(f"\nTexto analizado: {texto}")
    print(f"Sentimiento dominante: {sentimiento}")
    print("\nPorcentajes de cada sentimiento:")
    for s, p in porcentaje.items():
        print(f"{s}: {p:.2f}%")

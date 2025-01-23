import random


def generare_parinti(numar: int, marime_cromozom: int) -> list:
    lista_parinti = []
    for _ in range(numar):
        random_numbers = [str(random.randint(0, 1))
                          for _ in range(marime_cromozom)]
        random_string = ''.join(random_numbers)
        lista_parinti.append(random_string)
    return lista_parinti


def calcul_fitness(cromozom: str, lista_valori: list, lista_greutati: list, marime_rucsac: int) -> tuple:
    fitness = 0
    greutate = 0
    for i in range(len(cromozom)):
        if cromozom[i] == '1':
            if greutate + lista_greutati[i] > marime_rucsac:
                break
            fitness += lista_valori[i]
            greutate += lista_greutati[i]
    return fitness, greutate


def selectie_cei_mai_buni(parinti: list, lista_valori: list, lista_greutati: list, marime_rucsac: int, procent: float) -> list:
    fitness_scores = [
        (parinte, *calcul_fitness(parinte, lista_valori, lista_greutati, marime_rucsac))
        for parinte in parinti
    ]
    # Filtrăm doar cromozomii valizi
    fitness_scores = [fs for fs in fitness_scores if fs[2] <= marime_rucsac]

    if not fitness_scores:
        print("Eroare: Nu există cromozomi valizi după selecție.")
        return []

    # Sortăm după fitness, în ordine descrescătoare
    fitness_scores.sort(key=lambda x: x[1], reverse=True)

    numar_elitism = int(len(fitness_scores) * procent)
    return [parinte for parinte, _, _ in fitness_scores[:numar_elitism]]


def crossover(punct_taiere: int, parinti_finali: list) -> list:
    size = len(parinti_finali[0])
    if punct_taiere < 0 or punct_taiere >= size:
        print("Punct de tăiere invalid")
        return []

    offspring1 = parinti_finali[0][:punct_taiere] + \
        parinti_finali[1][punct_taiere:]
    offspring2 = parinti_finali[1][:punct_taiere] + \
        parinti_finali[0][punct_taiere:]
    return [offspring1, offspring2]


def aplicare_crossover(parinti: list, lista_valori: list, lista_greutati: list, marime_rucsac: int, procent_crossover: float) -> list:
    numar_crossover = int(len(parinti) * procent_crossover)
    offspring = []

    # Alegem aleatoriu cromozomi pentru crossover
    grupuri_parinti = random.sample(parinti, numar_crossover)

    for i in range(0, numar_crossover, 2):  # Fiecare pereche produce 2 descendenți
        parinte1 = grupuri_parinti[i]
        parinte2 = grupuri_parinti[i + 1] if i + \
            1 < len(grupuri_parinti) else grupuri_parinti[i]

        punct_taiere = random.randint(1, len(parinti[0]) - 1)
        offspring += mutatie_optimizanta(
            crossover(punct_taiere, [parinte1, parinte2]),
            lista_valori, lista_greutati, marime_rucsac
        )

    return offspring


def aplicare_mutatie(parinti: list, procent_mutatie: float) -> list:
    numar_mutatii = int(len(parinti) * procent_mutatie)

    # Alegem aleatoriu cromozomi pentru mutație
    indivizi_aleatori = random.sample(parinti, numar_mutatii)

    for individ in indivizi_aleatori:
        index_mutatie = random.randint(0, len(individ) - 1)
        cromozom_nou = list(individ)
        cromozom_nou[index_mutatie] = '1' if cromozom_nou[index_mutatie] == '0' else '0'
        parinti.append(''.join(cromozom_nou))

    return parinti


def gaseste_cel_mai_bun_individ(populatie: list, lista_valori: list, lista_greutati: list, marime_rucsac: int) -> dict:
    fitness_scores = [
        {
            "cromozom": cromozom,
            "fitness": calcul_fitness(cromozom, lista_valori, lista_greutati, marime_rucsac)[0],
            "greutate": calcul_fitness(cromozom, lista_valori, lista_greutati, marime_rucsac)[1],
        }
        for cromozom in populatie
    ]
    fitness_scores = [
        fs for fs in fitness_scores if fs["greutate"] <= marime_rucsac]

    if not fitness_scores:
        print("Eroare: Toți cromozomii sunt invalizi. Algoritmul se oprește.")
        return None

    fitness_scores.sort(key=lambda x: x["fitness"], reverse=True)
    return fitness_scores[0]


def mutatie_optimizanta(offspring: list, lista_valori: list, lista_greutati: list, marime_rucsac: int) -> list:
    cromozomi_validi = []

    for cromozom in offspring:
        fitness, greutate = calcul_fitness(
            cromozom, lista_valori, lista_greutati, marime_rucsac)

        # Dacă greutatea depășește limita, mutăm cromozomul aleatoriu pentru a-l face valid
        while greutate > marime_rucsac:
            # Alegem aleatoriu o genă '1' pe care să o schimbăm în '0'
            index_mutatie = random.choice(
                [i for i in range(len(cromozom)) if cromozom[i] == '1'])
            cromozom = cromozom[:index_mutatie] + \
                '0' + cromozom[index_mutatie + 1:]

            # Recalculăm greutatea
            fitness, greutate = calcul_fitness(
                cromozom, lista_valori, lista_greutati, marime_rucsac)

        cromozomi_validi.append(cromozom)

    return cromozomi_validi


if __name__ == "__main__":
    marime_rucsac = 40
    lista_valori = [100, 120, 5, 7, 60, 15, 92, 77, 40, 35]
    lista_greutati = [2, 5, 7, 12, 3, 1, 9, 4, 12, 11]

    numar_parinti = 2000
    marime_cromozom = len(lista_valori)
    procent_elitism = 0.15
    procent_crossover = 0.80
    procent_mutatie = 0.05
    numar_generatii = 100  # Numărul de generații pe care vrem să rulăm

    # Generăm populația inițială
    populatie = generare_parinti(numar_parinti, marime_cromozom)

    for generatie in range(numar_generatii):
        print(f"Generația {generatie + 1}")
        cei_mai_buni = selectie_cei_mai_buni(
            populatie, lista_valori, lista_greutati, marime_rucsac, procent_elitism
        )

        if not cei_mai_buni:
            # print("Nu există cromozomi valizi în selecție. Regenerăm populația.")
            populatie = generare_parinti(numar_parinti, marime_cromozom)
            continue

        descendentii = aplicare_crossover(
            cei_mai_buni, lista_valori, lista_greutati, marime_rucsac, procent_crossover
        )
        populatie = aplicare_mutatie(descendentii, procent_mutatie)
        populatie = mutatie_optimizanta(
            populatie, lista_valori, lista_greutati, marime_rucsac
        )

        if not populatie:
            print("Eroare: Toți cromozomii sunt invalizi. Regenerăm populația.")
            populatie = generare_parinti(numar_parinti, marime_cromozom)
            continue

        cel_mai_bun = gaseste_cel_mai_bun_individ(
            populatie, lista_valori, lista_greutati, marime_rucsac
        )
        if cel_mai_bun:
            print(f"Cromozom: {cel_mai_bun['cromozom']}, Fitness: {cel_mai_bun['fitness']}, Greutate: {cel_mai_bun['greutate']}")

    solutie_finala = gaseste_cel_mai_bun_individ(
        populatie, lista_valori, lista_greutati, marime_rucsac)
    if solutie_finala:
        print("\nSoluția finală:")
        print(f"Cromozom: {solutie_finala['cromozom']}")
        print(f"Fitness: {solutie_finala['fitness']}")
        print(f"Greutate totală: {solutie_finala['greutate']} din {marime_rucsac}")
    else:
        print("Algoritmul nu a găsit o soluție validă.")

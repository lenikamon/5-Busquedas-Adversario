import copy

class ModeloJuegoZT2:
    def inicializa(self):
        raise NotImplementedError()
    def jugadas_legales(self, s, j):
        raise NotImplementedError()
    def transicion(self, s, a, j):
        raise NotImplementedError()
    def terminal(self, s):
        raise NotImplementedError()
    def ganancia(self, s):
        raise NotImplementedError()

class Othello(ModeloJuegoZT2):

    def inicializa(self):
        tablero = [[0]*8 for _ in range(8)]
        tablero[3][3] = 2
        tablero[3][4] = 1
        tablero[4][3] = 1
        tablero[4][4] = 2
        return tablero

    def jugadas_legales(self, s, j):
        rival = 2 if j == 1 else 1
        movimientos = []
        direcciones = [(-1, -1), (-1, 0), (-1, 1),
                       (0, -1),          (0, 1),
                       (1, -1),  (1, 0), (1, 1)]

        for x in range(8):
            for y in range(8):
                if s[x][y] != 0:
                    continue
                for dx, dy in direcciones:
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < 8 and 0 <= ny < 8):
                        continue
                    if s[nx][ny] != rival:
                        continue
                    while 0 <= nx < 8 and 0 <= ny < 8:
                        if s[nx][ny] == 0:
                            break
                        if s[nx][ny] == j:
                            movimientos.append((x, y))
                            break
                        nx += dx
                        ny += dy
                    if (x, y) in movimientos:
                        break
        return movimientos

    def transicion(self, s, a, j):
        tablero = copy.deepcopy(s)
        x, y = a
        rival = 2 if j == 1 else 1
        tablero[x][y] = j
        direcciones = [(-1, -1), (-1, 0), (-1, 1),
                       (0, -1),          (0, 1),
                       (1, -1),  (1, 0), (1, 1)]

        for dx, dy in direcciones:
            fichas = []
            nx, ny = x + dx, y + dy
            while 0 <= nx < 8 and 0 <= ny < 8 and tablero[nx][ny] == rival:
                fichas.append((nx, ny))
                nx += dx
                ny += dy
            if 0 <= nx < 8 and 0 <= ny < 8 and tablero[nx][ny] == j:
                for fx, fy in fichas:
                    tablero[fx][fy] = j
        return tablero

    def terminal(self, s):
        return len(self.jugadas_legales(s, 1)) == 0 and len(self.jugadas_legales(s, 2)) == 0

    def ganancia(self, s):
        cont1 = sum(f == 1 for fila in s for f in fila)
        cont2 = sum(f == 2 for fila in s for f in fila)
        if cont1 > cont2:
            return 1
        elif cont2 > cont1:
            return 2
        else:
            return 0


def ordena_jugadas_othello(juego, estado, jugadas, jugador):
    def puntaje(j):
        x, y = j
        if (x, y) in [(0, 0), (0, 7), (7, 0), (7, 7)]:
            return 100
        elif x in [0, 7] or y in [0, 7]:
            return 10
        else:
            return 1
    return sorted(jugadas, key=puntaje, reverse=True)


def evalua_othello(juego, estado, jugador):
    rival = 2 if jugador == 1 else 1
    fichas_j = sum(f == jugador for fila in estado for f in fila)
    fichas_r = sum(f == rival for fila in estado for f in fila)
    mov_j = len(juego.jugadas_legales(estado, jugador))
    mov_r = len(juego.jugadas_legales(estado, rival))
    esquinas = [(0, 0), (0, 7), (7, 0), (7, 7)]
    esc_j = sum(estado[x][y] == jugador for x, y in esquinas)
    esc_r = sum(estado[x][y] == rival for x, y in esquinas)

    return (
        10 * (fichas_j - fichas_r) +
        20 * (esc_j - esc_r) +
        5 * (mov_j - mov_r)
    )


def negamax(juego, estado, jugador, prof_max, evalua, ordena_jugadas, prof=0):
    if juego.terminal(estado) or prof == prof_max:
        return evalua(juego, estado, jugador), None

    jugadas = juego.jugadas_legales(estado, jugador)
    if not jugadas:
        return negamax(juego, estado, 3 - jugador, prof_max, evalua, ordena_jugadas, prof + 1)[0], None

    mejor_valor = float('-inf')
    mejor_jugada = None
    jugadas = ordena_jugadas(juego, estado, jugadas, jugador)
    for jugada in jugadas:
        nuevo_estado = juego.transicion(estado, jugada, jugador)
        val, _ = negamax(juego, nuevo_estado, 3 - jugador, prof_max, evalua, ordena_jugadas, prof + 1)
        val = -val
        if val > mejor_valor:
            mejor_valor = val
            mejor_jugada = jugada
    return mejor_valor, mejor_jugada


def imprime_tablero(tablero):
    simbolos = {0: '.', 1: '●', 2: '○'}
    print("  " + " ".join(str(i) for i in range(8)))
    for i, fila in enumerate(tablero):
        print(i, " ".join(simbolos[c] for c in fila))
    print()



def juega_humano_vs_ia(juego, ia, prof_max, jugador_ia, evalua, ordena_jugadas):
    estado = juego.inicializa()
    jugador = 1
    while not juego.terminal(estado):
        imprime_tablero(estado)
        jugadas = juego.jugadas_legales(estado, jugador)
        if not jugadas:
            print(f"{jugador} pasa turno, no hay jugadas:()")
            jugador = 3 - jugador
            continue
        if jugador == jugador_ia:
            print(f"ia ({jugador}) estoy calculando mi plan maestropara ganarte ")
            _, jugada = ia(juego, estado, jugador, prof_max, evalua, ordena_jugadas)
        else:
            print(f"turno : {jugador})")
            print("Jugadas posibles:", jugadas)
            while True:
                entrada = input("Ingresa tu jugada como si fueran las coordenadas'y x': ")
                try:
                    x, y = map(int, entrada.strip().split())
                    jugada = (x, y)
                    if jugada in jugadas:
                        break
                    else:
                        print("no es valida")
                except:
                    print("vuelve a ingresar la jugada")
        estado = juego.transicion(estado, jugada, jugador)
        jugador = 3 - jugador

    imprime_tablero(estado)
    ganador = juego.ganancia(estado)
    if ganador == 0:
        print("¡waaaa fue un empate!")
    else:
        print(f"El campeón mundial del juego othello es {ganador} {'(ia :0)' if ganador == jugador_ia else '(humano)'}")



if __name__ == "__main__":
    juego = Othello()
    juega_humano_vs_ia(
        juego=juego,
        ia=negamax,
        prof_max=4,
        jugador_ia=2,
        evalua=evalua_othello,
        ordena_jugadas=ordena_jugadas_othello
    )

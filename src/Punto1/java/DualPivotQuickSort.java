
public class DualPivotQuickSort {

    public static void ordenar(int[] arreglo) {

        if (arreglo.length <= 1) {
            return;
        }

        // Pila para evitar recursión profunda.
        int[] pila = new int[arreglo.length * 2];

        int cima = 0;

        pila[cima++] = 0;
        pila[cima++] = arreglo.length - 1;

        while (cima > 0) {

            int derecha = pila[--cima];
            int izquierda = pila[--cima];

            if (izquierda >= derecha) {
                continue;
            }

            if (arreglo[izquierda] > arreglo[derecha]) {
                intercambiar(arreglo, izquierda, derecha);
            }

            int pivote1 = arreglo[izquierda];
            int pivote2 = arreglo[derecha];

            int menor = izquierda + 1;
            int mayor = derecha - 1;
            int actual = menor;

            while (actual <= mayor) {

                if (arreglo[actual] < pivote1) {

                    intercambiar(arreglo, actual, menor);

                    menor++;
                    actual++;

                } else if (arreglo[actual] > pivote2) {

                    while (
                            actual < mayor
                                    && arreglo[mayor] > pivote2
                    ) {
                        mayor--;
                    }

                    intercambiar(arreglo, actual, mayor);

                    mayor--;

                    if (arreglo[actual] < pivote1) {

                        intercambiar(
                                arreglo,
                                actual,
                                menor
                        );

                        menor++;
                    }

                    actual++;

                } else {
                    actual++;
                }
            }

            menor--;
            mayor++;

            intercambiar(arreglo, izquierda, menor);
            intercambiar(arreglo, derecha, mayor);

            // Región izquierda
            if (izquierda < menor - 1) {
                pila[cima++] = izquierda;
                pila[cima++] = menor - 1;
            }

            // Región central
            if (menor + 1 < mayor - 1) {
                pila[cima++] = menor + 1;
                pila[cima++] = mayor - 1;
            }

            // Región derecha
            if (mayor + 1 < derecha) {
                pila[cima++] = mayor + 1;
                pila[cima++] = derecha;
            }
        }
    }

    private static void intercambiar(
            int[] arreglo,
            int i,
            int j
    ) {

        int temporal = arreglo[i];
        arreglo[i] = arreglo[j];
        arreglo[j] = temporal;
    }
}

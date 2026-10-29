
public class HeapSort {

    public static void ordenar(int[] arreglo) {

        int n = arreglo.length;

        // Construir montículo máximo.
        for (int i = n / 2 - 1; i >= 0; i--) {
            heapify(arreglo, n, i);
        }

        // Extraer el máximo repetidamente.
        for (int fin = n - 1; fin > 0; fin--) {

            intercambiar(arreglo, 0, fin);

            heapify(arreglo, fin, 0);
        }
    }

    private static void heapify(
            int[] arreglo,
            int tamano,
            int raiz
    ) {

        while (true) {

            int mayor = raiz;

            int izquierdo = 2 * raiz + 1;
            int derecho = 2 * raiz + 2;

            if (
                    izquierdo < tamano
                            && arreglo[izquierdo] > arreglo[mayor]
            ) {
                mayor = izquierdo;
            }

            if (
                    derecho < tamano
                            && arreglo[derecho] > arreglo[mayor]
            ) {
                mayor = derecho;
            }

            if (mayor == raiz) {
                break;
            }

            intercambiar(arreglo, raiz, mayor);

            raiz = mayor;
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

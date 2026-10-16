
public class MergeSort {

    public static void ordenar(int[] arreglo) {

        int[] auxiliar = new int[arreglo.length];

        ordenarRecursivo(
                arreglo,
                auxiliar,
                0,
                arreglo.length
        );
    }

    private static void ordenarRecursivo(
            int[] arreglo,
            int[] auxiliar,
            int inicio,
            int fin
    ) {

        if (fin - inicio <= 1) {
            return;
        }

        int medio = (inicio + fin) / 2;

        ordenarRecursivo(
                arreglo,
                auxiliar,
                inicio,
                medio
        );

        ordenarRecursivo(
                arreglo,
                auxiliar,
                medio,
                fin
        );

        int i = inicio;
        int j = medio;
        int k = inicio;

        while (i < medio && j < fin) {

            if (arreglo[i] <= arreglo[j]) {
                auxiliar[k++] = arreglo[i++];
            } else {
                auxiliar[k++] = arreglo[j++];
            }
        }

        while (i < medio) {
            auxiliar[k++] = arreglo[i++];
        }

        while (j < fin) {
            auxiliar[k++] = arreglo[j++];
        }

        for (int posicion = inicio; posicion < fin; posicion++) {
            arreglo[posicion] = auxiliar[posicion];
        }
    }
}

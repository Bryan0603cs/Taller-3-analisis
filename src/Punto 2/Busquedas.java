public class Busquedas {

    public static int lineal(int[] arr, int objetivo) {
        for (int i = 0; i < arr.length; i++) {
            if (arr[i] == objetivo) {
                return i;
            }
        }
        return -1;
    }

    public static int binaria(int[] arr, int objetivo) {
        int inicio = 0;
        int fin = arr.length - 1;

        while (inicio <= fin) {
            int medio = inicio + (fin - inicio) / 2;

            if (arr[medio] == objetivo) {
                return medio;
            }

            if (arr[medio] < objetivo) {
                inicio = medio + 1;
            } else {
                fin = medio - 1;
            }
        }

        return -1;
    }

    public static int ternaria(int[] arr, int objetivo) {
        int inicio = 0;
        int fin = arr.length - 1;

        while (inicio <= fin) {
            int tercio = (fin - inicio) / 3;

            int medio1 = inicio + tercio;
            int medio2 = fin - tercio;

            if (arr[medio1] == objetivo) {
                return medio1;
            }

            if (arr[medio2] == objetivo) {
                return medio2;
            }

            if (objetivo < arr[medio1]) {
                fin = medio1 - 1;
            } else if (objetivo > arr[medio2]) {
                inicio = medio2 + 1;
            } else {
                inicio = medio1 + 1;
                fin = medio2 - 1;
            }
        }

        return -1;
    }

    public static int salto(int[] arr, int objetivo) {
        int n = arr.length;

        if (n == 0) {
            return -1;
        }

        int salto = (int) Math.sqrt(n);
        int anterior = 0;
        int actual = salto;

        while (anterior < n &&
                arr[Math.min(actual, n) - 1] < objetivo) {

            anterior = actual;
            actual += salto;

            if (anterior >= n) {
                return -1;
            }
        }

        while (anterior < Math.min(actual, n)) {
            if (arr[anterior] == objetivo) {
                return anterior;
            }

            if (arr[anterior] > objetivo) {
                return -1;
            }

            anterior++;
        }

        return -1;
    }

    public static int interpolacion(int[] arr, int objetivo) {
        int inicio = 0;
        int fin = arr.length - 1;

        while (inicio <= fin &&
                objetivo >= arr[inicio] &&
                objetivo <= arr[fin]) {

            if (arr[inicio] == arr[fin]) {
                return arr[inicio] == objetivo ? inicio : -1;
            }

            int pos = inicio + (int)(
                    ((long)(objetivo - arr[inicio]) *
                            (fin - inicio)) /
                            (arr[fin] - arr[inicio])
            );

            if (arr[pos] == objetivo) {
                return pos;
            }

            if (arr[pos] < objetivo) {
                inicio = pos + 1;
            } else {
                fin = pos - 1;
            }
        }

        return -1;
    }

    public static int exponencial(int[] arr, int objetivo) {
        int n = arr.length;

        if (n == 0) {
            return -1;
        }

        if (arr[0] == objetivo) {
            return 0;
        }

        int i = 1;

        while (i < n && arr[i] <= objetivo) {
            i *= 2;
        }

        return binariaRango(
                arr,
                objetivo,
                i / 2,
                Math.min(i, n - 1)
        );
    }

    private static int binariaRango(
            int[] arr,
            int objetivo,
            int inicio,
            int fin) {

        while (inicio <= fin) {
            int medio = inicio + (fin - inicio) / 2;

            if (arr[medio] == objetivo) {
                return medio;
            }

            if (arr[medio] < objetivo) {
                inicio = medio + 1;
            } else {
                fin = medio - 1;
            }
        }

        return -1;
    }
}
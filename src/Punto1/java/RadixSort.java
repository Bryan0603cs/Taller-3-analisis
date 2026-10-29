
public class RadixSort {

    public static void ordenar(int[] arreglo) {

        int n = arreglo.length;

        if (n <= 1) {
            return;
        }

        int maximo = arreglo[0];

        for (int numero : arreglo) {

            if (numero < 0) {
                throw new IllegalArgumentException(
                        "Radix Sort requiere enteros no negativos"
                );
            }

            if (numero > maximo) {
                maximo = numero;
            }
        }

        int[] salida = new int[n];

        long posicion = 1;

        while (maximo / posicion > 0) {

            int[] conteo = new int[10];

            // Contar cada dígito.
            for (int numero : arreglo) {

                int digito = (int) (
                        (numero / posicion) % 10
                );

                conteo[digito]++;
            }

            // Calcular posiciones acumuladas.
            for (int i = 1; i < 10; i++) {
                conteo[i] += conteo[i - 1];
            }

            // Construir la salida estable.
            for (int i = n - 1; i >= 0; i--) {

                int numero = arreglo[i];

                int digito = (int) (
                        (numero / posicion) % 10
                );

                int indice = conteo[digito] - 1;

                salida[indice] = numero;

                conteo[digito]--;
            }

            // Copiar al arreglo original.
            System.arraycopy(
                    salida,
                    0,
                    arreglo,
                    0,
                    n
            );

            posicion *= 10;
        }
    }
}

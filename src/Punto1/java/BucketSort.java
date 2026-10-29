
import java.util.ArrayList;
import java.util.List;

public class BucketSort {

    public static void ordenar(int[] arreglo) {

        int n = arreglo.length;

        if (n <= 1) {
            return;
        }

        int minimo = arreglo[0];
        int maximo = arreglo[0];

        for (int numero : arreglo) {

            if (numero < minimo) {
                minimo = numero;
            }

            if (numero > maximo) {
                maximo = numero;
            }
        }

        if (minimo == maximo) {
            return;
        }

        int cantidadCubetas = Math.max(
                1,
                (int) Math.sqrt(n)
        );

        List<List<Integer>> cubetas = new ArrayList<>();

        for (int i = 0; i < cantidadCubetas; i++) {
            cubetas.add(new ArrayList<>());
        }

        long rango = (long) maximo - minimo + 1;

        // Distribuir los números.
        for (int numero : arreglo) {

            int indice = (int) (
                    ((long) numero - minimo)
                            * cantidadCubetas
                            / rango
            );

            cubetas.get(indice).add(numero);
        }

        // Ordenar cada cubeta y unirlas.
        int posicion = 0;

        for (List<Integer> cubeta : cubetas) {

            insertionSortCubeta(cubeta);

            for (int numero : cubeta) {
                arreglo[posicion++] = numero;
            }
        }
    }

    private static void insertionSortCubeta(
            List<Integer> cubeta
    ) {

        for (int i = 1; i < cubeta.size(); i++) {

            int actual = cubeta.get(i);
            int j = i - 1;

            while (
                    j >= 0
                            && cubeta.get(j) > actual
            ) {

                cubeta.set(
                        j + 1,
                        cubeta.get(j)
                );

                j--;
            }

            cubeta.set(j + 1, actual);
        }
    }
}

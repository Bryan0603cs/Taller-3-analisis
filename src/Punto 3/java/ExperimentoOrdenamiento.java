
import java.io.BufferedReader;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.TimeUnit;

public class ExperimentoOrdenamiento {

    static final int[] TAMANOS = {
            1000, 10000, 100000, 1000000
    };

    static final String[] VARIANTES = {
            "aleatorio", "ascendente", "descendente"
    };

    static final int REPETICIONES = 5;
    static final long LIMITE_SEGUNDOS = 300;

    static final boolean GUARDAR_RESULTADOS = true;

    public static void main(String[] args) throws Exception {

        if (args.length == 3 && args[0].equals("--worker")) {

            ejecutarWorker(
                    args[1],
                    Paths.get(args[2])
            );

            return;
        }

        String algoritmo = args.length > 0
                ? args[0]
                : "insertion_sort";

        ejecutarExperimento(algoritmo);
    }

    static void ejecutarWorker(
            String algoritmo,
            Path ruta
    ) throws IOException {

        int[] arreglo = leerArreglo(ruta);

        long inicio = System.nanoTime();

        ordenar(algoritmo, arreglo);

        long fin = System.nanoTime();

        for (int i = 1; i < arreglo.length; i++) {

            if (arreglo[i - 1] > arreglo[i]) {
                throw new IllegalStateException(
                        "El arreglo no quedó ordenado"
                );
            }
        }

        double tiempoMs = (fin - inicio) / 1_000_000.0;

        System.out.printf(
                Locale.US,
                "TIEMPO_MS=%.6f%n",
                tiempoMs
        );
    }


    static void ordenar(String algoritmo, int[] arreglo) {

        switch (algoritmo) {

            case "insertion_sort":
                InsertionSort.ordenar(arreglo);
                break;

            case "dual_pivot_quicksort":
                DualPivotQuickSort.ordenar(arreglo);
                break;

            case "merge_sort":
                MergeSort.ordenar(arreglo);
                break;

            case "heap_sort":
                HeapSort.ordenar(arreglo);
                break;

            case "radix_sort":
                RadixSort.ordenar(arreglo);
                break;

            case "bucket_sort":
                BucketSort.ordenar(arreglo);
                break;

            default:
                throw new IllegalArgumentException(
                        "Algoritmo no implementado: " + algoritmo
                );
        }
    }


    static int[] leerArreglo(Path ruta) throws IOException {

        List<Integer> numeros = new ArrayList<>();

        try (
                BufferedReader lector = Files.newBufferedReader(
                        ruta,
                        StandardCharsets.UTF_8
                )
        ) {

            String linea;

            while ((linea = lector.readLine()) != null) {

                if (!linea.isBlank()) {
                    numeros.add(Integer.parseInt(linea.trim()));
                }
            }
        }

        int[] arreglo = new int[numeros.size()];

        for (int i = 0; i < numeros.size(); i++) {
            arreglo[i] = numeros.get(i);
        }

        return arreglo;
    }

    static Double medirConLimite(
            String algoritmo,
            Path ruta
    ) throws Exception {

        String java = Paths.get(
                System.getProperty("java.home"),
                "bin",
                "java"
        ).toString();

        String classpath = System.getProperty(
                "java.class.path"
        );

        ProcessBuilder constructor = new ProcessBuilder(
                java,
                "-cp",
                classpath,
                "ExperimentoOrdenamiento",
                "--worker",
                algoritmo,
                ruta.toAbsolutePath().toString()
        );

        constructor.redirectErrorStream(true);

        Process proceso = constructor.start();

        boolean termino = proceso.waitFor(
                LIMITE_SEGUNDOS,
                TimeUnit.SECONDS
        );

        if (!termino) {

            proceso.destroyForcibly();
            proceso.waitFor();

            return null;
        }

        String salida = new String(
                proceso.getInputStream().readAllBytes(),
                StandardCharsets.UTF_8
        );

        if (proceso.exitValue() != 0) {
            throw new RuntimeException(
                    "Error en el proceso Java:\n" + salida
            );
        }

        for (String linea : salida.split("\\R")) {

            if (linea.startsWith("TIEMPO_MS=")) {

                return Double.parseDouble(
                        linea.substring("TIEMPO_MS=".length())
                );
            }
        }

        throw new RuntimeException(
                "No se recibió el tiempo de ejecución: " + salida
        );
    }

    static void ejecutarExperimento(
            String algoritmo
    ) throws Exception {

        Path base = Paths.get("..").toAbsolutePath().normalize();

        Path carpetaDatos = base.resolve(
                "datos/datos"
        );

        Path carpetaResultados = base.resolve(
                "resultados/java/" + algoritmo
        );

        if (GUARDAR_RESULTADOS) {
            Files.createDirectories(carpetaResultados);
        }

        for (int n : TAMANOS) {

            StringBuilder json = new StringBuilder();

            json.append("{\n");
            json.append("  \"algoritmo\": \"")
                    .append(algoritmo)
                    .append("\",\n");
            json.append("  \"lenguaje\": \"Java\",\n");
            json.append("  \"tamano\": ")
                    .append(n)
                    .append(",\n");
            json.append("  \"repeticiones_solicitadas\": ")
                    .append(REPETICIONES)
                    .append(",\n");
            json.append("  \"limite_segundos\": ")
                    .append(LIMITE_SEGUNDOS)
                    .append(",\n");
            json.append("  \"resultados\": {\n");

            for (int v = 0; v < VARIANTES.length; v++) {

                String variante = VARIANTES[v];

                Path ruta = carpetaDatos.resolve(
                        variante + "_" + n + ".txt"
                );

                if (!Files.exists(ruta)) {
                    throw new IOException(
                            "No existe el archivo: " + ruta
                    );
                }

                System.out.println(
                        "\nAlgoritmo: " + algoritmo
                                + " | Variante: " + variante
                                + " | Tamaño: " + n
                );

                List<Double> tiempos = new ArrayList<>();

                boolean tiempoAgotado = false;

                for (int r = 0; r < REPETICIONES; r++) {

                    Double tiempo = medirConLimite(
                            algoritmo,
                            ruta
                    );

                    if (tiempo == null) {

                        tiempoAgotado = true;

                        System.out.println(
                                "Ejecución " + (r + 1)
                                        + ": superó cinco minutos"
                        );

                        break;
                    }

                    tiempos.add(tiempo);

                    System.out.printf(
                            Locale.US,
                            "Ejecución %d: %.4f ms%n",
                            r + 1,
                            tiempo
                    );
                }

                json.append("    \"")
                        .append(variante)
                        .append("\": {\n");

                if (!tiempoAgotado) {

                    double promedio = promedio(tiempos);
                    double desviacion = desviacion(tiempos);

                    json.append(
                            "      \"tipo\": \"medido\",\n"
                    );

                    json.append(
                                    "      \"tiempos_ms\": "
                            ).append(listaJson(tiempos))
                            .append(",\n");

                    json.append(
                                    "      \"promedio_ms\": "
                            ).append(promedio)
                            .append(",\n");

                    json.append(
                                    "      \"desviacion_estandar_ms\": "
                            ).append(desviacion)
                            .append("\n");

                    System.out.printf(
                            Locale.US,
                            "Promedio: %.4f ms%n",
                            promedio
                    );

                } else {

                    json.append(
                            "      \"tipo\": \"incompleto\",\n"
                    );

                    json.append(
                                    "      \"tiempos_medidos_ms\": "
                            ).append(listaJson(tiempos))
                            .append(",\n");

                    json.append(
                                    "      \"repeticiones_completadas\": "
                            ).append(tiempos.size())
                            .append(",\n");

                    json.append(
                            "      \"motivo\": "
                                    + "\"Límite de cinco minutos alcanzado\"\n"
                    );
                }

                json.append("    }");

                if (v < VARIANTES.length - 1) {
                    json.append(",");
                }

                json.append("\n");
            }

            json.append("  }\n");
            json.append("}\n");

            if (GUARDAR_RESULTADOS) {

                Path archivo = carpetaResultados.resolve(
                        n + ".json"
                );

                Files.writeString(
                        archivo,
                        json.toString(),
                        StandardCharsets.UTF_8
                );

                System.out.println(
                        "\nResultados guardados: " + archivo
                );
            }
        }

        System.out.println(
                "\nEXPERIMENTO FINALIZADO"
        );
    }

    static double promedio(List<Double> tiempos) {

        double suma = 0;

        for (double tiempo : tiempos) {
            suma += tiempo;
        }

        return suma / tiempos.size();
    }

    static double desviacion(List<Double> tiempos) {

        double media = promedio(tiempos);
        double suma = 0;

        for (double tiempo : tiempos) {

            double diferencia = tiempo - media;

            suma += diferencia * diferencia;
        }

        return Math.sqrt(
                suma / (tiempos.size() - 1)
        );
    }

    static String listaJson(List<Double> tiempos) {

        StringBuilder resultado = new StringBuilder("[");

        for (int i = 0; i < tiempos.size(); i++) {

            if (i > 0) {
                resultado.append(", ");
            }

            resultado.append(tiempos.get(i));
        }

        resultado.append("]");

        return resultado.toString();
    }
}

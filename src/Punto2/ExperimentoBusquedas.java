package Punto2;

import java.nio.file.*;
import java.util.*;
import java.io.IOException;

public class ExperimentoBusquedas {

    static final int[] TAMANOS = {1000, 10000, 100000, 1000000};
    static final int REPETICIONES = 5;
    static volatile long checksumGlobal = 0;

    interface Busqueda {
        int buscar(int[] arreglo, int clave);
    }

    static int[] leer(Path ruta) throws IOException {
        return Files.lines(ruta)
                .filter(s -> !s.isBlank())
                .mapToInt(Integer::parseInt)
                .toArray();
    }

    static double[] medir(Busqueda busqueda, int[] arreglo, int[] claves) {
        double[] tiempos = new double[REPETICIONES];

        for (int r = 0; r < REPETICIONES; r++) {
            long checksum = 0;
            long inicio = System.nanoTime();

            for (int clave : claves) {
                checksum += busqueda.buscar(arreglo, clave);
            }

            long fin = System.nanoTime();
            checksumGlobal ^= checksum;
            tiempos[r] = (fin - inicio) / (double) claves.length;
        }
        return tiempos;
    }

    static void calentamiento(Busqueda b, int[] arreglo, int[] claves) {
        for (int i = 0; i < 3; i++) {
            long s = 0;
            for (int clave : claves) s += b.buscar(arreglo, clave);
            checksumGlobal ^= s;
        }
    }

    static double promedio(double[] x) {
        double s = 0;
        for (double v : x) s += v;
        return s / x.length;
    }

    static double desviacion(double[] x) {
        double m = promedio(x);
        double s = 0;
        for (double v : x) s += (v - m) * (v - m);
        return Math.sqrt(s / (x.length - 1));
    }

    static String arregloJson(double[] x) {
        return Arrays.toString(x);
    }

    static void guardar(Path ruta, String algoritmo, int n, double[] tiempos)
            throws IOException {

        Files.createDirectories(ruta.getParent());

        String json = "{\n" +
                "  \"algoritmo\": \"" + algoritmo + "\",\n" +
                "  \"lenguaje\": \"Java\",\n" +
                "  \"n\": " + n + ",\n" +
                "  \"tipo\": \"medido\",\n" +
                "  \"unidad\": \"ns_por_busqueda\",\n" +
                "  \"repeticiones_ns\": " + arregloJson(tiempos) + ",\n" +
                "  \"promedio_ns\": " + promedio(tiempos) + ",\n" +
                "  \"desviacion_ns\": " + desviacion(tiempos) + "\n" +
                "}\n";

        Files.writeString(ruta, json);
    }

    public static void main(String[] args) throws Exception {

        Path raiz = Path.of(".").toAbsolutePath().normalize();

        Path punto2 = raiz
                .resolve("src")
                .resolve("Punto2");

        Path datos = raiz
                .resolve("src")
                .resolve("Punto1")
                .resolve("datos")
                .resolve("datos");

        Path clavesDir = punto2.resolve("claves");

        Path salida = punto2
                .resolve("resultados")
                .resolve("java");
        LinkedHashMap<String, Busqueda> algoritmos = new LinkedHashMap<>();
        algoritmos.put("lineal", Busquedas::lineal);
        algoritmos.put("binaria", Busquedas::binaria);
        algoritmos.put("ternaria", Busquedas::ternaria);
        algoritmos.put("salto", Busquedas::salto);
        algoritmos.put("interpolacion", Busquedas::interpolacion);
        algoritmos.put("exponencial", Busquedas::exponencial);

        for (int n : TAMANOS) {
            int[] arreglo = leer(datos.resolve("ascendente_" + n + ".txt"));
            int[] claves = leer(clavesDir.resolve("claves_" + n + ".txt"));

            System.out.println("\n===== n=" + n + " =====");

            for (var e : algoritmos.entrySet()) {
                calentamiento(e.getValue(), arreglo, claves);
                double[] tiempos = medir(e.getValue(), arreglo, claves);

                guardar(
                        salida.resolve(e.getKey() + "_" + n + ".json"),
                        e.getKey(), n, tiempos
                );

                System.out.printf(
                        Locale.US,
                        "%s: %.3f ns/búsqueda%n",
                        e.getKey(), promedio(tiempos)
                );
            }
        }

        int n = 1_000_000;
        int[] arreglo = leer(datos.resolve("ascendente_" + n + ".txt"));

        LinkedHashMap<String, Integer> posiciones = new LinkedHashMap<>();
        posiciones.put("inicio", arreglo[0]);
        posiciones.put("centro", arreglo[n / 2]);
        posiciones.put("final", arreglo[n - 1]);

        StringBuilder json = new StringBuilder("{\n");
        int a = 0;

        for (var e : algoritmos.entrySet()) {
            json.append("  \"").append(e.getKey()).append("\": {\n");
            int p = 0;

            for (var pos : posiciones.entrySet()) {
                int[] claves = new int[1000];
                Arrays.fill(claves, pos.getValue());

                calentamiento(e.getValue(), arreglo, claves);
                double[] tiempos = medir(e.getValue(), arreglo, claves);

                json.append("    \"").append(pos.getKey()).append("\": {")
                        .append("\"clave\": ").append(pos.getValue()).append(", ")
                        .append("\"tipo\": \"medido\", ")
                        .append("\"promedio_ns\": ").append(promedio(tiempos)).append(", ")
                        .append("\"desviacion_ns\": ").append(desviacion(tiempos)).append(", ")
                        .append("\"repeticiones_ns\": ").append(arregloJson(tiempos))
                        .append("}");

                if (++p < posiciones.size()) json.append(",");
                json.append("\n");
            }

            json.append("  }");
            if (++a < algoritmos.size()) json.append(",");
            json.append("\n");
        }

        json.append("}\n");
        Files.createDirectories(salida);
        Files.writeString(salida.resolve("posiciones_1000000.json"), json.toString());

        System.out.println("Finalizado. checksum=" + checksumGlobal);
    }
}

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Locale;

public class Simulator {

    private final double L;
    private final ArrayList<Particle> particleList;
    private final CollisionSystem collisionSystem;
    private Double t = 0.0;
    private int step = 0;
    private final int maxT;

    public Simulator(double L, ArrayList<Particle> particleList, Path outputPath, int maxTimesteps) throws IOException {
        this.L = L;
        this.particleList = particleList;
        this.maxT = maxTimesteps;
        collisionSystem = new CollisionSystem(particleList);
        executeSimulation(outputPath);
    }

    public void executeSimulation(Path outputPath) throws IOException {
        try (OutputWriter out = OutputWriter.open(outputPath)) {
            while (step < maxT) {
                out.writeStep(particleList, t);
                t+= collisionSystem.nextStep();
                step++;
            }
        }
    }


   public static void main(String[] args) throws IOException {
        int N = Integer.parseInt(args[0]);
        double L = Double.parseDouble(args[1]);
        int iterations = Integer.parseInt(args[2]);
        int maxTimesteps = Integer.parseInt(args[3]);
        String inputDir = args[4];
        String outputDir = args[5];
        if (N <= 0 || L <= 0 || iterations <= 0 || maxTimesteps <= 0 || inputDir.isEmpty() || outputDir.isEmpty()) {
            System.out.println("Error: Parameters should be: N, L, iterations, maxTimesteps");
            return;
        }
        for (int i = 0; i < iterations; i++) {
            InputParser parser = new InputParser(inputDir + "/N" + N + "/input_N" + N + "_" + String.format("%04d", i) + ".txt", N);
            ArrayList<Particle> particles = parser.parseInputs();
            if (particles.size() != N) {
                System.out.println("Error: Number of particles does not match the expected amount");
                return;
            }
            String L_dir = String.format(Locale.US, "L%.3f", L);
            Path directory = Files.createDirectories(Path.of(outputDir, "N_" + N + "_" + L_dir));
            Path fileName =  Path.of(directory + String.format("/output_N%d_%s_t%d_%s.csv", N, L_dir, maxTimesteps, String.format("%04d", i)));
            Simulator s = new Simulator(L, particles,  fileName, maxTimesteps);
        }


   }

}

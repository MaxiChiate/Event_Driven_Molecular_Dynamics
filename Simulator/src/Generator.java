import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

//The output file will contain the following information for each particle:
//x, y, v_x, v_y, radius
public class Generator {

    private final int particleCount;
    private final double boardSize;
    private final double speed;
    private final double radius;
    private static final String OUTPUT_PATH = "./inputs";

    public Generator(int particleCount, double boardSize, double speed, double radius) {
        this.particleCount = particleCount;
        this.boardSize = boardSize;
        this.speed = speed;
        this.radius = radius;
    }

    public boolean checkOverlap(Particle p1, Particle p2) {
        double dx = p1.getX() - p2.getX();
        double dy = p1.getY() - p2.getY();
        double distance = Math.sqrt(dx * dx + dy * dy);
        return distance < (p1.getRadius() + p2.getRadius());
    }

    public boolean checkCollision(Particle[] particles, Particle new_particle, int created_particles) {
        for (int i = 0; i < created_particles; i++) {
            if (checkOverlap(particles[i], new_particle)) return true;
        }
        return false;
    }


    public void generateInputs(int iteration) throws IOException {
        String dirPath = OUTPUT_PATH + "/" + "N" + particleCount;
        Files.createDirectories(Path.of(dirPath));
        String fileName = String.format("input_N%d_%s.txt", particleCount, String.format("%04d", iteration));
        File file = new File(dirPath + "/" + fileName);
        if (file.exists()) {
            file.delete();
        }
        file.createNewFile();
        int i = 0;
        Particle[] particles = new Particle[particleCount];
        while (i < particleCount) {
            double x = Math.random() * (boardSize - 2 * radius) + radius;
            double y = Math.random() * (boardSize - 2 * radius) + radius;
            double angle = Math.random() * 2 * Math.PI;
            double vx = speed * Math.cos(angle);
            double vy = speed * Math.sin(angle);
            Particle new_particle = new Particle(x, y, vx, vy, radius);
            if (!checkCollision(particles, new_particle, i)) {
                particles[i] = new_particle;
                String particle = String.format(Locale.US, "%.17g %.17g %.17g %.17g %.5f%n", x, y, vx, vy, radius);
                java.nio.file.Files.write(file.toPath(), particle.getBytes(), java.nio.file.StandardOpenOption.APPEND);
                i++;
            }

        }
        System.out.println("File " + file.getName() + " created successfully.");
    }


    public static void main(String[] args) throws IOException {
        int N = Integer.parseInt(args[0]);
        double L = Double.parseDouble(args[1]);
        double speed = Double.parseDouble(args[2]);
        double radius = Double.parseDouble(args[3]);
        int iterations = Integer.parseInt(args[4]);
        if (N <= 0 || L <= 0 || speed <= 0 || radius <= 0 || iterations <= 0) {
            System.out.println("Error: Parameters should be: N, L, speed, radius, iterations");
            return;
        }
        Generator gen = new Generator(N, L, speed, radius);
        for (int i = 0; i < iterations; i++) {
            gen.generateInputs(i);
        }
    }
}
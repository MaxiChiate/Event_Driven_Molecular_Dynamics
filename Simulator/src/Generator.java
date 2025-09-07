import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

//The output file will contain the following information for each particle:
//x, y, v_x, v_y, radius
public class Generator {

    private static final int PARTICLES_AMOUNT = 300;
    private static final double BOARD_SIZE = 0.09;
    private static final double SPEED = 0.01;
    private static final double RADIUS = 0.0015;
    private static final int ITERATIONS = 5;
    private static final String OUTPUT_PATH = "./inputs";


    public boolean checkOverlap(Particle p1, Particle p2) {
        double dx = p1.getX() - p2.getX();
        double dy = p1.getY() - p2.getY();
        double distance = Math.sqrt(dx * dx + dy * dy);
        return distance < (p1.getRadius() + p2.getRadius());
    }

    public boolean checkCollision(Particle[] particles, Particle new_particle, int created_particles) {
        for (int i = 0; i < created_particles; i ++) {
            if (checkOverlap(particles[i], new_particle)) return true;
        }
        return false;
    }


    public void generateInputs(int iteration) throws IOException {
        String dirPath = OUTPUT_PATH + "/" + "N" + PARTICLES_AMOUNT;
        Files.createDirectories(Path.of(dirPath));
        String fileName = String.format("input_N%d_%s.txt", PARTICLES_AMOUNT, String.format("%04d", iteration));
        File file = new File(dirPath + "/" + fileName);
        if (file.exists()) {
            file.delete();
        }
        file.createNewFile();
        int i=0;
        Particle[] particles = new Particle[PARTICLES_AMOUNT];
        while (i < PARTICLES_AMOUNT) {
            double x = Math.random() * (BOARD_SIZE - 2 * RADIUS) + RADIUS;
            double y = Math.random() * (BOARD_SIZE - 2 * RADIUS) + RADIUS;
            double angle = Math.random() * 2 * Math.PI;
            double vx = SPEED * Math.cos(angle);
            double vy = SPEED * Math.sin(angle);
            Particle new_particle = new Particle(x, y, vx, vy, RADIUS);
            if (!checkCollision(particles, new_particle, i)) {
                particles[i] = new_particle;
                String particle = String.format(Locale.US, "%.17g %.17g %.17g %.17g %.5f%n", x, y, vx, vy, RADIUS);
                java.nio.file.Files.write(file.toPath(), particle.getBytes(), java.nio.file.StandardOpenOption.APPEND);
                i++;
            }

        }
        System.out.println("File " + file.getName() + " created successfully.");
    }


    public static void main(String[] args) throws IOException {
        Generator gen = new Generator();
        for (int i = 0; i < ITERATIONS; i++) {
            gen.generateInputs(i);
        }
    }
}

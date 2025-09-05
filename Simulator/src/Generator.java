import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Locale;

//The output file will contain the following information for each particle:
//x, y, v_x, v_y, radius
public class Generator {

    final int particles_amount = 300;
    final double board_size = 0.09;
    final double speed = 0.01;
    final double radius = 0.0015;
    final static int iterations = 5;
    final String outputPath = "./src/inputs";


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
        String dirPath = outputPath + "/" + "N" + particles_amount;
        Files.createDirectories(Path.of(dirPath));
        String fileName = String.format("input_N%d_%s.txt", particles_amount, String.format("%04d", iteration));
        File file = new File(dirPath + "/" + fileName);
        if (file.exists()) {
            file.delete();
        }
        file.createNewFile();
        int i=0;
        Particle[] particles = new Particle[particles_amount];
        while (i < particles_amount) {
            double x = Math.random() * (board_size - 2 * radius) + radius;
            double y = Math.random() * (board_size - 2 * radius) + radius;
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
        Generator gen = new Generator();
        for (int i = 0; i < iterations; i++) {
            gen.generateInputs(i);
        }
    }
}

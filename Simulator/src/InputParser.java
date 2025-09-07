import java.util.ArrayList;

public class InputParser {
    private final String inputPath;
    private final int particles_amount;
    public InputParser(String inputPath, int particles_amount) {
        this.inputPath = inputPath;
        this.particles_amount = particles_amount;
    }
    ArrayList<Particle> parseInputs() {
        ArrayList<Particle> particles = new ArrayList<>();
        try {
            java.util.List<String> lines = java.nio.file.Files.readAllLines(java.nio.file.Path.of(inputPath));
            for (String line : lines) {
                String[] parts = line.split(" ");
                if (parts.length != 5) {
                    throw new IllegalArgumentException("Invalid input format");
                }
                double x = Double.parseDouble(parts[0]);
                double y = Double.parseDouble(parts[1]);
                double vx = Double.parseDouble(parts[2]);
                double vy = Double.parseDouble(parts[3]);
                double radius = Double.parseDouble(parts[4]);
                Particle particle = new Particle(x, y, vx, vy, radius);
                particles.add(particle);
            }
            if (particles.size() != particles_amount) {
                throw new IllegalArgumentException("Number of particles does not match the expected amount");
            }
        } catch (Exception e) {
            e.printStackTrace();
        }
        return  particles;
    }

}

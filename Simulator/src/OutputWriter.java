import java.io.BufferedWriter;
import java.io.IOException;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.StandardOpenOption;
import java.util.Formatter;
import java.util.List;
import java.util.Locale;

public class OutputWriter implements AutoCloseable {

    private final BufferedWriter bw;
    private final BufferedWriter collisionsBw;
    private final StringBuilder sb;
    private final Formatter fmt;

    private OutputWriter(Path path) throws IOException {
        this.bw = Files.newBufferedWriter(
                path,
                StandardCharsets.UTF_8,
                StandardOpenOption.CREATE,
                StandardOpenOption.TRUNCATE_EXISTING,
                StandardOpenOption.WRITE
        );
        String baseName = path.getFileName().toString();
        String collisionsName = baseName.substring(0, baseName.length() - 4) + "_collisions.csv";
        Path collisionsPath = path.resolveSibling(collisionsName);
        this.collisionsBw = Files.newBufferedWriter(
                collisionsPath,
                StandardCharsets.UTF_8,
                StandardOpenOption.CREATE,
                StandardOpenOption.TRUNCATE_EXISTING,
                StandardOpenOption.WRITE
        );
        this.sb  = new StringBuilder();
        this.fmt = new Formatter(sb, Locale.US);
    }

    public static OutputWriter open(Path path) throws IOException {
        return new OutputWriter(path);
    }


    public void writeStep(List<Particle> particles, double time, WallCollisionDTO collision) throws IOException {
        sb.setLength(0);
        fmt.format("%.4f%n", time);
        for (Particle p : particles) {
            fmt.format("%.17g,%.17g,%.17g,%.17g,%.5f%n", p.getX(), p.getY(), p.getVx(), p.getVy(), p.getRadius());
        }
        bw.write(sb.toString());
        if (collision != null) {
            if (collision.wall() == Wall.CORNER) return;
            sb.setLength(0);
            fmt.format("%.4f,%d,%.17g%n", collision.time(), collision.wall().ordinal(), collision.normalSpeedAbs());
            collisionsBw.write(sb.toString());
        }
    }

    @Override
    public void close() throws IOException {
        fmt.close();
        bw.close();
        collisionsBw.close();
    }
}
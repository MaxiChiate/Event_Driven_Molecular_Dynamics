import java.util.*;

public class CollisionSystem {
    private final List<Particle> particles;
    private final Map<ParticlePair, Double> collisions = new HashMap<>();

    public CollisionSystem(List<Particle> particles) {
        this.particles = particles;
        computeAllCollisions();
    }

    private void computeAllCollisions() {

        int n = particles.size();
        for (int i = 0; i < n; i++) {
            Particle p1 = particles.get(i);

//
//            ParticlePair selfPair = new ParticlePair(p1);
//            collisions.put(selfPair, p1.timeToHitBoundary());

            for (int j = i + 1; j < n; j++) {
                Particle p2 = particles.get(j);
                Double t = p1.timeToHit(p2);
                collisions.put(new ParticlePair(p1, p2), t);
            }
        }
    }

    public Map<ParticlePair, Double> getCollisions() {
        return Map.copyOf(collisions);
    }

    public Map.Entry<ParticlePair, Double> nextCollision() {
        return collisions.entrySet()
                .stream()
                .filter(e -> e.getValue() != null)
                .min(Map.Entry.comparingByValue())
                .orElse(null);
    }
}

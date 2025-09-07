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

            ParticlePair selfPair = new ParticlePair(p1);
            collisions.put(selfPair, p1.timeToHitBoundary());

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

    public Double nextStep() {
        // Siguiente colisión
        Map.Entry<ParticlePair, Double> next = nextCollision();

        if (next == null) return null;

        double dt = next.getValue();
        ParticlePair pair = next.getKey();
        Particle a = pair.getP1();
        Particle b = pair.getP2();

        // Recalculo las posiciones de las partículas
        for(Particle particle : particles) {
            particle.move(dt);
        }

        // Recalculo las direcciones de las que colisionaron
        if(b != null)
            a.bounceOffUnitMass(b);
        else
             a.bounceOffBoundary();

        // Restar dt a todas las demás colisiones
        advanceTime(dt);

        // Recalcular colisiones de las partículas que chocaron
        recomputeCollisionsFor(a);
        if (b != null) recomputeCollisionsFor(b);

        return dt;
    }

    private Map.Entry<ParticlePair, Double> nextCollision() {
        return collisions.entrySet()
                .stream()
                .filter(e -> e.getValue() != null)
                .min(Map.Entry.comparingByValue())
                .orElse(null);
    }

    private void advanceTime(double dt) {
        for (Map.Entry<ParticlePair, Double> entry : collisions.entrySet()) {
            if (entry.getValue() != null) {
                collisions.put(entry.getKey(), entry.getValue() - dt);
            }
        }
    }

    private void recomputeCollisionsFor(Particle p) {
        for (Particle other : particles) {
            if (other == p) continue;
            ParticlePair pair = new ParticlePair(p, other);
            Double t = p.timeToHit(other);
            collisions.put(pair, t);
        }
    }
}

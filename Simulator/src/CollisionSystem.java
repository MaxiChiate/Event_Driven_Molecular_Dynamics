import java.util.*;

@Deprecated
public class CollisionSystem {
    private final List<Particle> particles;

//    private final Map<ParticlePair, Double> collisions = new HashMap<>();
    private final Map<Particle, Collision> collisions;

    public CollisionSystem(List<Particle> particles) {
        this.particles = particles;
        collisions = new HashMap<>();
        computeAllCollisions();
    }

    public Map<Particle, Collision> getAllCollisions() {
        return Map.copyOf(collisions);
    }

    public Double nextStep() {
        // Siguiente colisión
        Map.Entry<Particle, Collision> next = nextCollision();

        if (next == null) return Particle.NO_HIT_TIME;

        Collision collision = next.getValue();
        double dt = collision.getTime();
        Particle a = collision.getP1();
        Particle b = collision.getP2();

        // Recalculo las posiciones de las partículas
        for(Particle particle : particles) {
            particle.move(dt);
        }

        // Recalculo las direcciones de las que colisionaron
        if(b != null)
            a.bounceOff(b);
        else
//            a.bounceOffBoundary();

        // Restar dt a todas las demás colisiones
        advanceTime(dt);

        // Recalcular colisiones de las partículas que chocaron
        recomputeCollisionsFor(a);
        if (b != null) recomputeCollisionsFor(b);

        return dt;
    }

    private void computeAllCollisions() {

        for (Particle particle : particles) {

            collisions.put(particle, computeNextCollisionFor(particle));
        }
    }

    private Collision computeNextCollisionFor(Particle particle) {

        Collision nextCollision = new Collision(particle, null, 3.1415); //particle.timeToHitBoundary());;
        Double timeAux;

        for (Particle particleAux : particles) {

            if(particleAux.equals(particle)) continue;

            timeAux = particle.timeToHit(particleAux);

            if(timeAux.compareTo(nextCollision.getTime()) <= 0) {
                nextCollision = new Collision(particle, particleAux, timeAux);
            }
        }

        return nextCollision;
    }

    private Map.Entry<Particle, Collision> nextCollision() {
        return collisions.entrySet()
                .stream()
                .filter(e -> e.getValue() != null)
                .min(Comparator.comparingDouble(e -> e.getValue().getTime()))
                .orElse(null);
    }


    private void advanceTime(double dt) {
        for (Map.Entry<Particle, Collision> entry : collisions.entrySet()) {
            Collision collision = entry.getValue();
            if (collision != null) {
                collision.advanceTime(dt);
                collisions.put(entry.getKey(), collision);
            }
        }
    }

    private void recomputeCollisionsFor(Particle p) {
        Collision collision = computeNextCollisionFor(p);
        collisions.put(collision.getP1(), collision);

        Collision otherCollision = collisions.get(collision.getP2());
        if( otherCollision != null && collision.compareTo(otherCollision) <= 0) {
            collisions.put(collision.getP2(), collision);
        }
    }
}


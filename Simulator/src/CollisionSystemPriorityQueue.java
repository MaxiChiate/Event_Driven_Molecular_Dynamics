import java.util.List;
import java.util.PriorityQueue;
import java.util.function.Predicate;

public class CollisionSystemPriorityQueue {

    private final List<Particle> particles;
    private final PriorityQueue<Collision> pq = new PriorityQueue<>();
    private final Enclosure mainEnclosure;
//    private final Enclosure secondEnclosure;
    private double currentTime = 0.0;

    public CollisionSystemPriorityQueue(List<Particle> particles, double L) {
        this.particles = particles;
        mainEnclosure = new Enclosure(0.0, 0.0, L);
        // cargar colisiones iniciales
        for (Particle p : particles) {
            predictExclusiveStrong(p);
        }
    }

    public Double nextStep() {
        if(pq.isEmpty()) return null;
        Collision c = pq.poll();

        while(!c.isValid())    {   // Busco la proxima colisión válida
            if(pq.isEmpty()) {
                return null;
            }
            else  {
                c = pq.poll();
            }
        }

        double dt = c.getTime() - currentTime;
        moveParticles(dt);
        currentTime = c.getTime();

        Particle a = c.getP1();
        Particle b = c.getP2();

        if (b != null) {
            a.bounceOff(b);
        } else {
            mainEnclosure.bounceOffBoundary(a);
        }
        a.incrementCollisionCount();
        if (b != null) b.incrementCollisionCount();

        predictExclusive(a, b);
        if (b != null) predict(b);

        return currentTime;
    }

    private void moveParticles(double dt) {
        for (Particle p : particles) {
            p.move(dt);
        }
    }

    private void predict(Particle p) {
        predictGeneral(p, p2 -> true);
    }

    private void predictExclusive(Particle p, Particle toExclude) {
        predictGeneral(p, p2 -> !p2.equals(toExclude));
    }

    private void predictExclusiveStrong(Particle p) {
        predictGeneral(p, p2 -> p.getId() < p2.getId());
    }

    private void predictGeneral(Particle p, Predicate<Particle> condition) {
        if (p == null) return;

        double tMin = mainEnclosure.timeToHitBoundary(p);
        double t;
        Particle other = null;

        for (Particle p2 : particles) {
            if (condition.test(p2)) {
                t = p.timeToHit(p2);

                if (Double.compare(t, tMin) < 0) {
                    tMin = t;
                    other = p2;
                }
            }
        }

        if (Double.compare(tMin, Particle.NO_HIT_TIME) < 0) {
            pq.add(new Collision(p, other, tMin + currentTime));
        }
    }

    public void printState() {
        System.out.println("=== Collision System State ===");
        System.out.println("Current Time: " + currentTime);
        System.out.println("Pending Collisions (in time order):");

        PriorityQueue<Collision> copy = new PriorityQueue<>(pq);
        while (!copy.isEmpty()) {
            Collision c = copy.poll();
            System.out.println("  " + c);
        }
        System.out.println("==============================");
    }

}




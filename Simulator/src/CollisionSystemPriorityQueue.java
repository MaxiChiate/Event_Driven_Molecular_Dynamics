import java.util.List;
import java.util.PriorityQueue;

public class CollisionSystemPriorityQueue {

    private final List<Particle> particles;
    private final PriorityQueue<Collision> pq = new PriorityQueue<>();
    private double currentTime = 0.0;

    public CollisionSystemPriorityQueue(List<Particle> particles) {
        this.particles = particles;
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
            a.bounceOffBoundary();
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
        if (p == null) return;
        Double tMin, t;
        tMin = t = p.timeToHitBoundary();
        Particle other = null;

        for (Particle p2 : particles) {
            t = p.timeToHit(p2);

            if(Double.compare(t, tMin) < 0) {
                tMin = t;
                other = p2;
            }
        }

        if(Double.compare(tMin, Particle.NO_HIT_TIME) < 0) {
            pq.add(new Collision(p, other, tMin + currentTime));
        }
    }

    private void predictExclusive(Particle p, Particle toExclude) {
        if (p == null) return;
        Double tMin, t;
        tMin = t = p.timeToHitBoundary();
        Particle other = null;

        for (Particle p2 : particles) {
            if (!p2.equals(toExclude)) {
                t = p.timeToHit(p2);

                if(Double.compare(t, tMin) < 0) {
                    tMin = t;
                    other = p2;
                }
            }
        }

        if(Double.compare(tMin, Particle.NO_HIT_TIME) < 0) {
            pq.add(new Collision(p, other, tMin + currentTime));
        }
    }

    private void predictExclusiveStrong(Particle p) {
        if (p == null) return;
        Double tMin, t;
        tMin = t = p.timeToHitBoundary();
        Particle other = null;

        for (Particle p2 : particles) {
            if (p.getId() < p2.getId()) {
                t = p.timeToHit(p2);

                if(Double.compare(t, tMin) < 0) {
                    tMin = t;
                    other = p2;
                }
            }
        }

        if(Double.compare(tMin, Particle.NO_HIT_TIME) < 0) {
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




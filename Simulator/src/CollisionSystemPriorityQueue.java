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
            predict(p);
        }
    }

    public Double nextStep() {
        if(pq.isEmpty()) return Double.POSITIVE_INFINITY;
        Collision c = pq.poll();

        while(!c.isValid())    {   // Busco la proxima colisión válida
            if(pq.isEmpty()) {
                return Double.POSITIVE_INFINITY;
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

        predict(a);
        if (b != null) predict(b);

        return dt;
    }

    private void moveParticles(double dt) {
        for (Particle p : particles) {
            p.move(dt);
        }
    }

    private void predict(Particle p) {
        if (p == null) return;
        Double t = p.timeToHitBoundary();
        // borde
        if(Double.compare(t, Particle.NO_HIT_TIME) < 0) {
            pq.add(new Collision(p, null, currentTime + t));
        }
        // otras partículas
        for (Particle other : particles) {
            if (p != other) {
                t = p.timeToHit(other);
                if (Double.compare(t, Particle.NO_HIT_TIME) < 0) {
                    pq.add(new Collision(p, other, currentTime + t));
                }
            }
        }
    }
}



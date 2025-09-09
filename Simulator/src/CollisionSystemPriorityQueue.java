import java.util.*;

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

        public void simulate() {
            while (!pq.isEmpty()) {
                Collision c = pq.poll();

                if (!c.isValid()) continue; // ignorar si ya quedó obsoleta

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
            }
        }

        private void moveParticles(double dt) {
            for (Particle p : particles) {
                p.move(dt);
            }
        }

        private void predict(Particle p) {
            if (p == null) return;
            // borde
            pq.add(new Collision(p, null, currentTime + p.timeToHitBoundary()));
            // otras partículas
            for (Particle other : particles) {
                if (p != other) {
                    double t = p.timeToHit(other);
                    if (t != Double.POSITIVE_INFINITY) {
                        pq.add(new Collision(p, other, currentTime + t));
                    }
                }
            }
        }
    }



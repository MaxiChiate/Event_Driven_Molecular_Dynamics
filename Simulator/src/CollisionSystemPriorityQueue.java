import java.util.List;
import java.util.PriorityQueue;
import java.util.function.Predicate;

public class CollisionSystemPriorityQueue {

    private final List<Particle> particles;
    private final PriorityQueue<Collision> pq = new PriorityQueue<>();
    private final Enclosure mainEnclosure;
//    private final Enclosure secondEnclosure;
    private double currentTime = 0.0;
    private WallCollisionDTO collision = null;
    private int collisionCount = 0;

    public WallCollisionDTO getWallCollision(){
        WallCollisionDTO retCollision = collision;
        collision = null;
        return retCollision;
    }

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
//                if(c.getP2() == null ) {
//                    System.out.println("========= Collision descartada ============");
//                    System.out.println(c);
//                }
                c = pq.poll();
            }
        }

        double dt = c.getTime() - currentTime;
        moveParticles(dt);
        currentTime = c.getTime();

        Particle a = c.getP1();
        Particle b = c.getP2();

        collision = c.resolve();

        a.incrementCollisionCount();
        if (b != null) b.incrementCollisionCount();

        predict(a);
        if (b != null) predictExclusive(b, a);

        ++collisionCount;
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

        // Enqueue next wall collision (minimum among four walls)
        WallCollision wc = mainEnclosure.timeToHitBoundary(p);
        if (wc != null && wc.getTime() < Particle.NO_HIT_TIME) {
            wc.setTime(wc.getTime() + currentTime);
            pq.add(wc);
        }

        for (Particle p2 : particles) {
            if (p2.equals(p)) continue;
            if (!condition.test(p2)) continue;
            double t = p.timeToHit(p2);
            if (t < Particle.NO_HIT_TIME) {
                pq.add(new ParticleCollision(p, p2, t + currentTime));
            }
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

    public void printNextCollision()    {
        System.out.println("=== Next Collision ===");
        System.out.println("Current Time: " + currentTime);
        System.out.println(pq.peek());
    }

    public double getCurrentTime() {
        return currentTime;
    }
}




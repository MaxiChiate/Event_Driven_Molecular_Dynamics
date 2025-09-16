public class ParticleCollision extends Collision {

    private final Particle p2;
    private final int count2;

    public ParticleCollision(Particle p1, Particle p2, Double time) {
        super(p1, time);
        if (p2 == null) {
            throw new IllegalArgumentException("Second particle cannot be null in ParticleCollision");
        }
        this.p2 = p2;
        this.count2 = p2.getCollisionCount();
    }

    @Override
    public Particle getP2() {
        return p2;
    }

    @Override
    public boolean isValid() {
        return super.isValid() && p2.getCollisionCount() == count2;
    }

    @Override
    public WallCollision resolve() {
        getP1().bounceOff(p2);
        return null;
    }

    @Override
    public String toString() {
        return "ParticleCollision{" +
                "p1=" + getP1().getId() +
                ", p2=" + p2.getId() +
                ", time=" + getTime() +
                "}";
    }
}

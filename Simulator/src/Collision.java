public class Collision implements Comparable<Collision> {

    private final Particle p1;
    private final Particle p2;
    private Double time = 0.0;

    private final int count1;
    private final int count2;

    public Collision(Particle p1, Particle p2, Double time) {

        if ((p1 == null && p2 == null) || time == null) throw new IllegalArgumentException();
        this.p1 = p1;
        this.p2 = p2;
        this.time = time;

        this.count1 = (p1 != null) ? p1.getCollisionCount() : -1;
        this.count2 = (p2 != null) ? p2.getCollisionCount() : -1;
    }

    @Override
    public int compareTo(Collision o) {
        return getTime().compareTo(o.getTime());
    }

    public boolean isValid() {
        return (p1 == null || p1.getCollisionCount() == count1)
                && (p2 == null || p2.getCollisionCount() == count2);
    }


    public void advanceTime(double dt) {
        this.time -= dt;
    }

    public Particle getP1() {
        return p1;
    }

    public Particle getP2() {
        return p2;
    }

    public Double getTime() {
        return time;
    }

    @Override
    public String toString() {
        return "Collision{" +
                "p1=" + p1.getId() +
                ", " + (p2 == null ? "wall" : ("p2=" + p2.getId())) +
                ", time=" + time +
                "}\nParticle: " + p1;
    }
}
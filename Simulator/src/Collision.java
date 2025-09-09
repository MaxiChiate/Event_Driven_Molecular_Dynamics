public class Collision implements Comparable<Collision> {

    private final Particle p1;
    private final Particle p2;
    private Double time;

    public Collision(Particle p1, Particle p2, Double time) {

        if ((p1 == null && p2 == null) || time == null) throw new IllegalArgumentException();
        this.p1 = p1;
        this.p2 = p2;
        this.time = time;
    }

    @Override
    public int compareTo(Collision o) {
        return getTime().compareTo(o.getTime());
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
}
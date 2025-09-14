public class WallCollision extends Collision {
    
    private final Wall wall;

    public WallCollision(Particle p1, Wall wall, Double time) {
        super(p1, time);
        this.wall = wall;
    }

    @Override
    public void resolve() {
        Particle p = getP1();
        switch (wall) {
            case LEFT, RIGHT -> p.setVx(-p.getVx());
            case TOP, BOTTOM -> p.setVy(-p.getVy());
        }
    }

    @Override
    public String toString() {
        return "WallCollision{" +
                "p1=" + getP1().getId() +
                ", wall=" + wall +
                ", time=" + getTime() +
                "}";
    }
}

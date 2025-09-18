public class WallCollision extends Collision {

    private final Wall wall;

    public WallCollision(Particle p1, Wall wall, Double time) {
        super(p1, time);
        this.wall = wall;
    }
    public Wall getWall() {
        return  wall;
    }

    @Override
    public WallCollisionDTO resolve() {
        Particle p = getP1();
        WallCollisionDTO c = new WallCollisionDTO(p.getVx(), p.getVy(), wall, this.getTime());
        switch (wall) {
            case LEFT_1, RIGHT_1, RIGHT_2 -> p.setVx(-p.getVx());
            case TOP_1, BOTTOM_1, TOP_2, BOTTOM_2 -> p.setVy(-p.getVy());
            case CORNER -> {
                p.setVx(-p.getVx());
                p.setVy(-p.getVy());
            }
        }
        return c;
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
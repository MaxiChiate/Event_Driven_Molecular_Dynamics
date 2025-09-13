public class Enclosure {

    private final double x0, y0, width, height;
    private final static double DEFAULT = 0.09;
    private final double L;
    private Enclosure neighborLeft, neighborRight;

    public Enclosure(double x0, double y0, double L) {
        this(x0, y0, DEFAULT, DEFAULT, L);
    }

    public Enclosure(double x0, double y0, double height, double L) {
        this(x0, y0, DEFAULT, height, L);
    }

    public Enclosure(double x0, double y0, double width, double height, double L) {
        this.x0 = x0;
        this.y0 = y0;
        this.width = width;
        this.height = height;
        this.L = L;
    }

    public void setNeighborLeft(Enclosure neighbor) {
        this.neighborLeft = neighbor;
    }

    public void setNeighborRight(Enclosure neighbor) {
        this.neighborRight = neighbor;
    }

    public WallCollision timeToHitBoundary(Particle p) {
        double vx = p.getVx(), vy = p.getVy();
        double x = p.getX(), y = p.getY();

        double tx = Particle.NO_HIT_TIME;
        double ty = Particle.NO_HIT_TIME;

        Wall wallX = null;
        Wall wallY = null;

        if (vx < 0) {
            tx = (left(p) - x) / vx;
            wallX = Wall.LEFT;
        }
        if (vx > 0) {
            tx = (right(p) - x) / vx;
            wallX = Wall.RIGHT;
        }

        if (vy < 0) {
            ty = (top(p) - y) / vy;
            wallY = Wall.TOP;
        }
        if (vy > 0) {
            ty = (bottom(p) - y) / vy;
            wallY = Wall.BOTTOM;
        }

        if (tx <= ty) {
            return tx > 0 ? new WallCollision(p, wallX, tx) : new WallCollision(p, wallX, Particle.NO_HIT_TIME);
        } else {
            return ty > 0 ? new WallCollision(p, wallY, ty) : new WallCollision(p, wallY, Particle.NO_HIT_TIME);
        }
    }

//    public void bounceOffBoundary(Particle p) {
//        double vx = p.getVx(), vy = p.getVy();
//
//        switch (p.getWhichWall()) {
//            case Wall.LEFT, Wall.RIGHT -> p.setVx(-vx);
//            case Wall.TOP, Wall.BOTTOM -> p.setVy(-vy);
//        }
//    }

    private double left(Particle p) {
        return x0 + p.getRadius();
    }

    private double right(Particle p) {
        return x0 + width - p.getRadius();
    }

    private double top(Particle p) {
        return y0 + p.getRadius();
    }

    private double bottom(Particle p) {
        return y0 + height - p.getRadius();
    }

//    private double doorMinY() { return y0 + (height - L) / 2.0; }
//    private double doorMaxY() { return y0 + (height + L) / 2.0; }
}

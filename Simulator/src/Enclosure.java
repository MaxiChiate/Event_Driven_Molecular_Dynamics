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

    public double timeToHitBoundary(Particle p) {
        double vx = p.getVx(), vy = p.getVy();
        double x = p.getX(), y = p.getY();

        double tx = Particle.NO_HIT_TIME;
        double ty = Particle.NO_HIT_TIME;

        if (vx < 0)
//            && !(neighborLeft != null && y >= doorMinY() && y <= doorMaxY()))
            tx = (left(p) - x) / vx;
        if (vx > 0 )
//            && !(neighborRight != null && y >= doorMinY() && y <= doorMaxY()))
            tx = (right(p) - x) / vx;

        if (vy < 0) ty = (top(p) - y) / vy;
        if (vy > 0) ty = (bottom(p) - y) / vy;

        double tmin = Math.min(tx, ty);
        return tmin > 0 ? tmin : Particle.NO_HIT_TIME;
    }

    public void bounceOffBoundary(Particle p) {
        double x = p.getX(), y = p.getY();
        double vx = p.getVx(), vy = p.getVy();

        if (x - p.getRadius() <= x0)
//            && !(neighborLeft != null && y >= doorMinY() && y <= doorMaxY()))
            p.setVx(-vx);
        if (x + p.getRadius() >= x0 + width)
//            && !(neighborRight != null && y >= doorMinY() && y <= doorMaxY()))
            p.setVx(-vx);
        if (y - p.getRadius() <= y0)
            p.setVy(-vy);
        if (y + p.getRadius() >= y0 + height)
            p.setVy(-vy);
    }

    private double left(Particle p) { return x0 + p.getRadius(); }
    private double right(Particle p) { return x0 + width - p.getRadius(); }
    private double top(Particle p) { return y0 + p.getRadius(); }
    private double bottom(Particle p) { return y0 + height - p.getRadius(); }

//    private double doorMinY() { return y0 + (height - L) / 2.0; }
//    private double doorMaxY() { return y0 + (height + L) / 2.0; }
}

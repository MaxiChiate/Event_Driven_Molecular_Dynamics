public class Particle {
    double x;
    double y;
    double vx;
    double vy;
    double radius;

    public Particle(double x, double y, double vx, double vy, double radius) {
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.radius = radius;
    }

    public Double timeToHit(Particle other) {
        double dx = other.getX() - getX();
        double dy = other.getY() - getY();
        double dvx = other.getVx() - getVx();
        double dvy = other.getVy() - getVy();

        double dvdr = dx * dvx + dy * dvy;   // producto punto Δr · Δv
        if (dvdr >= 0) return null; // se alejan

        double dvdv = dvx * dvx + dvy * dvy;
        double drdr = dx * dx + dy * dy;
        double sigma = getRadius() + other.getRadius();

        double d = dvdr * dvdr - dvdv * (drdr - sigma * sigma);
        if (d < 0) return null; // no hay solución real

        return -(dvdr + Math.sqrt(d)) / dvdv;
    }

    public void setX(double x) {
        this.x = x;
    }

    public void setY(double y) {
        this.y = y;
    }

    public void setVx(double vx) {
        this.vx = vx;
    }

    public void setVy(double vy) {
        this.vy = vy;
    }

    public void setRadius(double radius) {
        this.radius = radius;
    }

    public double getX() {
        return x;
    }

    public double getY() {
        return y;
    }

    public double getVx() {
        return vx;
    }

    public double getVy() {
        return vy;
    }

    public double getRadius() {
        return radius;
    }

}

public class Particle {

    public static double NO_HIT_TIME = Double.POSITIVE_INFINITY;

    private static long nextId = 0;
    private final long ID;

    private double x, y, vx, vy, radius, mass;
    private int collisionCount;

    public Particle(double x, double y, double vx, double vy, double radius, double mass) {
        this.ID = nextId++;
        this.x = x;
        this.y = y;
        this.vx = vx;
        this.vy = vy;
        this.radius = radius;
        this.mass = mass;
        this.collisionCount = 0;
    }

    public Particle(double x, double y, double vx, double vy, double radius) {
        this(x, y, vx, vy, radius, 1.0);
    }

    public Double timeToHit(Particle other) {
        double dx = other.getX() - getX();
        double dy = other.getY() - getY();
        double dvx = other.getVx() - getVx();
        double dvy = other.getVy() - getVy();

        double dvdr = dx * dvx + dy * dvy;   // producto punto Δr · Δv
        if (dvdr >= 0) return NO_HIT_TIME; // se alejan

        double dvdv = dvx * dvx + dvy * dvy;
        double drdr = dx * dx + dy * dy;
        double sigma = sigma(other);

        double d = dvdr * dvdr - dvdv * (drdr - sigma * sigma);
        if (d < 0) return NO_HIT_TIME; // no hay solución real

        return -(dvdr + Math.sqrt(d)) / dvdv;
    }

//    public Double timeToHitBoundary()   {
//        return NO_HIT_TIME;
//    }

    public void move(double dt) {
        this.x += this.vx * dt;
        this.y += this.vy * dt;
    }

    public void bounceOff(Particle other) {
        double dx = other.x - this.x;
        double dy = other.y - this.y;
        double dvx = other.vx - this.vx;
        double dvy = other.vy - this.vy;

        double dvdr = dx * dvx + dy * dvy; // producto punto Δr · Δv
        double dist = sigma(other);

//        if(dvdr < 0) return;

        // magnitud del impulso
        double J = 2.0 * this.getMass() * other.getMass() * dvdr / ((this.getMass() + other.getMass()) * dist);
        double Jx = J * dx / dist;
        double Jy = J * dy / dist;

        // actualizar velocidades
        this.vx += Jx / this.getMass();
        this.vy += Jy / this.getMass();
        other.vx -= Jx / other.getMass();
        other.vy -= Jy / other.getMass();
    }

//    public void bounceOffBoundary() {
//
//    }

    public void incrementCollisionCount() {
        collisionCount++;
    }

    public int getCollisionCount() {
        return collisionCount;
    }

    public double sigma(Particle other)   {
        return getRadius() + other.getRadius();
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

    public void setMass(double mass) { this.mass = mass; }

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

    public double getMass() {
        return mass;
    }

    public long getId()  { return ID; }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Particle other)) return false;
        return ID == other.ID;
    }

    @Override
    public int hashCode() {
        return Long.hashCode(ID);
    }

    @Override
    public String toString() {
        return "Particle: " + ID + ", x,y = (" + x + ", " + y + "), v = (" + vx + ", " + vy + "), radius = " + radius + ", mass = " + mass;
    }
}

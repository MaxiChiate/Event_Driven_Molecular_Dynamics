import java.util.Map;
import java.util.function.Function;

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
        double x = p.getX(), y = p.getY();
        double vx = p.getVx(), vy = p.getVy();
        double r = p.getRadius();
        // TODO: take into account posibility of vx = 0
        if (x == 0) throw new RuntimeException("Vx is 0");
        double m = vy / vx;
        double b = y - m * x;
        Function<Double, Double> fx = (x_pos) -> m * x_pos + b;
        Function<Double, Double> fy = (y_pos) -> (y_pos - b) / m;
        double t_vertical = Particle.NO_HIT_TIME, t_horizontal = Particle.NO_HIT_TIME;
        Wall w_vertical = null, w_horizontal = null;

        if (vx < 0) {
            t_vertical = p.time_y(fx.apply(x0 + r));
            w_vertical = Wall.LEFT_1;
        } else {
            double y_col = fx.apply(x0 + width - r);
            t_vertical = p.time_y(y_col);
            w_vertical = Wall.RIGHT_1;
            if (t_vertical == Particle.NO_HIT_TIME || (y_col > y0 + (height - L) / 2 && y_col < y0 + (height + L) / 2)) {
                y_col = fx.apply(x0 + 2 * width - r);
                if (y_col >= y0 + (height - L) / 2 && y_col <= y0 + (height + L) / 2) {
                    t_vertical = p.time_y(y_col);
                    w_vertical = Wall.RIGHT_2;
                } else {
                    t_vertical = Particle.NO_HIT_TIME;
                }
            }
        }

        if (vy < 0) {
            if (vx > 0) {
                double x_col = fy.apply(y0 + r);
                t_horizontal = p.time_x(x_col);
                w_horizontal = Wall.TOP_1;
                if (x_col > x0 + width) {
                    x_col = fy.apply(y0 + (height - L) / 2 + r);
                    if (x_col >= x0 + width) {
                        t_horizontal = p.time_x(x_col);
                        w_horizontal = Wall.TOP_2;
                    } else {
                        t_horizontal = Particle.NO_HIT_TIME;
                    }
                }
            } else {
                double x_col = fy.apply(y0 + (height - L) / 2 + r);
                t_horizontal = p.time_x(x_col);
                w_horizontal = Wall.TOP_2;
                if (t_horizontal == Particle.NO_HIT_TIME || x_col < x0 + width) {
                    x_col = fy.apply(y0 + r);
                    if (x_col <= x0 + width) {
                        t_horizontal = p.time_x(x_col);
                        w_horizontal = Wall.TOP_1;
                    } else {
                        t_horizontal = Particle.NO_HIT_TIME;
                    }
                }
            }
        } else {
            if (vx > 0) {
                double x_col = fy.apply(y0 + height - r);
                t_horizontal = p.time_x(x_col);
                w_horizontal = Wall.BOTTOM_1;
                if (x_col > x0 + width) {
                    x_col = fy.apply(y0 + (height + L) / 2 - r);
                    if (x_col >= x0 + width) {
                        t_horizontal = p.time_x(x_col);
                        w_horizontal = Wall.BOTTOM_2;
                    } else {
                        t_horizontal = Particle.NO_HIT_TIME;
                    }
                }
            } else {
                double x_col = fy.apply(y0 + (height + L) / 2 - r);
                t_horizontal = p.time_x(x_col);
                w_horizontal = Wall.BOTTOM_2;
                if (t_horizontal == Particle.NO_HIT_TIME || x_col < x0 + width) {
                    x_col = fy.apply(y0 + height - r);
                    if (x_col <= x0 + width) {
                        t_horizontal = p.time_x(x_col);
                        w_horizontal = Wall.BOTTOM_1;
                    } else {
                        t_horizontal = Particle.NO_HIT_TIME;
                    }
                }
            }
        }

        double coef = 0.98;

        if (x0 + width - r * coef < x && x < x0 + width + r * coef) {
            double t_corner;
            if (vy < 0) {
                t_corner = corner_collision(p, x0 + width, y0 + (height - L) / 2);
            } else {
                t_corner = corner_collision(p, x0 + width, y0 + (height + L) / 2);
            }
            if (t_corner != Particle.NO_HIT_TIME) return new WallCollision(p, Wall.CORNER, t_corner);
        }

        if ((y0 + (height - L) / 2 - r * coef < y && y < y0 + (height - L) / 2 + r * coef) && vx > 0) {
            double t_corner = corner_collision(p, x0 + width, y0 + (height - L) / 2);
            if (t_corner != Particle.NO_HIT_TIME) return new WallCollision(p, Wall.CORNER, t_corner);
        } else if ((y0 + (height + L) / 2 - r * coef < y && y < y0 + (height + L) / 2 + r * coef) && vx > 0) {
            double t_corner = corner_collision(p, x0 + width, y0 + (height + L) / 2);
            if (t_corner != Particle.NO_HIT_TIME) return new WallCollision(p, Wall.CORNER, t_corner);
        }

        if (t_vertical == Particle.NO_HIT_TIME && t_horizontal == Particle.NO_HIT_TIME) {
            double t_corner = corner_collision(p, x0 + width, y0 + (height - L) / 2);
            if (t_corner != Particle.NO_HIT_TIME) return new WallCollision(p, Wall.CORNER, t_corner);
            t_corner = corner_collision(p, x0 + width, y0 + (height + L) / 2);
            if (t_corner != Particle.NO_HIT_TIME) return new WallCollision(p, Wall.CORNER, t_corner);
//            throw new RuntimeException("Shouldn't happen. No collision against enclosure found");
//            return null;
            p.moveBackwards(0.001);
            return timeToHitBoundary(p);
        }

        if (t_vertical <= t_horizontal) {
            return new WallCollision(p, w_vertical, t_vertical);
        } else {
            return new WallCollision(p, w_horizontal, t_horizontal);
        }
    }

    private double corner_collision(Particle p, double x_corner, double y_corner) {
        double x = p.getX(), y = p.getY();
        double vx = p.getVx(), vy = p.getVy();
        double r = p.getRadius();

        double dx = x - x_corner;
        double dy = y - y_corner;

        if (dx * dx + dy * dy <= r * r) {
            p.moveBackwards(0.001);
            x = p.getX();
            y = p.getY();
            vx = p.getVx();
            vy = p.getVy();
            r = p.getRadius();
            dx = x - x_corner;
            dy = y - y_corner;
        }

        double a = vx * vx + vy * vy;
        double b = 2 * (dx * vx + dy * vy);
        double c = dx * dx + dy * dy - r * r;

        if (a == 0.0) {
            if (c <= 0.0) {
                return 0.0; // already touching or overlapping
            } else {
                return Particle.NO_HIT_TIME; // never collides
            }
        }

        double disc = b * b - 4 * a * c;
        if (disc < 0.0) {
            return Particle.NO_HIT_TIME; // no real intersection
        }

        double sqrtD = Math.sqrt(disc);
        double t1 = (-b - sqrtD) / (2 * a);
        double t2 = (-b + sqrtD) / (2 * a);

        double result = Particle.NO_HIT_TIME;

        if (t1 >= 0.0 && (result == Particle.NO_HIT_TIME || t1 < result)) {
            result = t1;
        }
        if (t2 >= 0.0 && (result == Particle.NO_HIT_TIME || t2 < result)) {
            result = t2;
        }

        return result; // NaN if no positive root
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

    private Map<Wall, Double> collisionPositions(Particle p) {
        // TODO: take into account posibility of vx = 0
        if (p.getVx() == 0) throw new RuntimeException("Vx is 0");
        double m = p.getVy() / p.getVx();
        double b = p.getY() - m * p.getX();
        double r = p.getRadius();
        Function<Double, Double> fx = (x) -> m * x + b;
        Function<Double, Double> fy = (y) -> (y - b) / m;
        return Map.of(
                Wall.LEFT_1, fx.apply(x0 + r),
                Wall.RIGHT_1, fx.apply(x0 + width - r),
                Wall.RIGHT_2, fx.apply(x0 + 2 * width - r),
                Wall.TOP_1, fy.apply(y0 + r),
                Wall.BOTTOM_1, fy.apply(y0 + height - r),
                Wall.TOP_2, fy.apply(y0 + (height - L) / 2 + r),
                Wall.BOTTOM_2, fy.apply(y0 + (height + L) / 2 - r)
        );
    }

//    private void particleQuadrant(Particle p) {
//        double x = p.getX(), y = p.getY();
//        double vx = p.getVx(), vy = p.getVy();
//
//        // Lower corner
//        if (x < x0 + width) {
//            if (y < y0 + (height + L) / 2) {
//                // Q1
//            } else if (y > y0 + (height + L) / 2) {
//                // Q2
//            } else {
//                // aligned, idk...
//            }
//        } else if (x > x0 + width) {
//            if (y < y0 + (height + L) / 2) {
//                // Q3
//            } else {
//                // Should never happen.
//            }
//        } else {
//            // idk
//        }
//    }

//    private double doorMinY() { return y0 + (height - L) / 2.0; }
//    private double doorMaxY() { return y0 + (height + L) / 2.0; }
}

public class Utils {

    public static final double EPSILON = 1e-9;
    public static double NO_HIT_TIME = Double.POSITIVE_INFINITY;


    private Utils() {
        throw new RuntimeException("Utility class");
    }

    public static boolean negligible(double a) {
        return equals(a, 0.0);
    }

    public static boolean equals(double a, double b) {
        return Math.abs(a - b) < EPSILON;
    }

    public static boolean lessThan(double a, double b) {
        return a < b - EPSILON;
    }

    public static boolean greaterThan(double a, double b) {
        return a > b + EPSILON;
    }

    public static boolean lessOrEquals(double a, double b) {
        return a < b + EPSILON;
    }

    public static boolean greaterOrEquals(double a, double b) {
        return a > b - EPSILON;
    }
}

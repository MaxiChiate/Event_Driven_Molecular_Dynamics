public record WallCollisionDTO(
        double vx,
        double vy,
        Wall wall,
        double time
) {
    public boolean isVertical() {
        return wall == Wall.LEFT_1 || wall == Wall.RIGHT_1 || wall == Wall.RIGHT_2;
    }
    public double normalSpeed() {
        return isVertical() ? vx : vy;
    }
    public double normalSpeedAbs() {
        return Math.abs(normalSpeed());
    }
}
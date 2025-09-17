public record WallCollisionDTO(
        double vx,
        double vy,
        Wall wall,
        double time
) {
    public boolean isVertical() {
        return wall == Wall.LEFT || wall == Wall.RIGHT;
    }
    public double normalSpeed() {
        return isVertical() ? vx : vy;
    }
    public double normalSpeedAbs() {
        return Math.abs(normalSpeed());
    }
}
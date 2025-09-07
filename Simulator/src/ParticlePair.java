import java.util.Objects;

public class ParticlePair {
        private final Particle p1;
        private final Particle p2; // puede ser null si es solo una partícula

        public ParticlePair(Particle p1) {
            this(p1, null);
        }

        public ParticlePair(Particle p1, Particle p2) {
            if (p1 == null) throw new IllegalArgumentException("p1 no puede ser null");
            this.p1 = p1;
            this.p2 = p2;
        }

        public Particle getP1() {
            return p1;
        }

        public Particle getP2() {
            return p2;
        }

        @Override
        public boolean equals(Object o) {
            if (this == o) return true;
            if (!(o instanceof ParticlePair)) return false;
            ParticlePair other = (ParticlePair) o;

            // El par es igual sin importar el orden
            return Objects.equals(p1, other.p1) && Objects.equals(p2, other.p2) ||
                   Objects.equals(p1, other.p2) && Objects.equals(p2, other.p1);
        }

        @Override
        public int hashCode() {

            int h1 = p1.hashCode();
            int h2 = p2 != null ? p2.hashCode() : 0;
            return h1 + h2;
        }

        @Override
        public String toString() {
            if (p2 == null) return "Particle(" + p1 + ")";
            return "Particle(" + p1 + ") & Particle(" + p2 + ")";
        }
    }
// File: GameBattle.java
public class GameBattle {

    // Basic attack
    public void attack(int damage) {
        System.out.println("Basic attack for " + damage + " points!");
    }

    // Attack with weapon
    public void attack(int damage, String weapon) {
        System.out.println("Attacking with " + weapon + " for " + damage + " points!");
    }

    // Attack with critical option
    public void attack(int damage, String weapon, boolean isCritical) {
        if (isCritical) {
            System.out.println("CRITICAL HIT! " + weapon + " deals " + (damage * 2) + " points!");
        } else {
            attack(damage, weapon); // reuse the overloaded method
        }
    }

    // Team attack
    public void attack(int damage, String[] teammates) {
        int teamSize = teammates.length;
        System.out.print("Team attack with ");
        for (int i = 0; i < teamSize; i++) {
            System.out.print(teammates[i]);
            if (i < teamSize - 1) {
                System.out.print(", ");
            }
        }
        System.out.println(" for " + (damage * teamSize) + " total damage!");
    }

    public static void main(String[] args) {
        // 1. Create GameBattle object
        GameBattle game = new GameBattle();

        // 2. Test overloaded attack methods
        game.attack(50); // Basic attack
        game.attack(75, "Sword"); // Weapon attack
        game.attack(60, "Bow", true); // Critical attack
        String[] team = {"Alice", "Bob"};
        game.attack(40, team); // Team attack
    }
}

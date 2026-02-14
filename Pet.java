/*
 * author yanaburlak_snhu
 */
import java.util.Scanner;   //Import Scanner class to read user input

public class Pet {
	// Static variables to track dog/cat boarding spaces
    private static int dogSpaces = 30;
    private static int catSpaces = 12;
    // Variables to store pet information
    private String petType;
    private String petName;
    private int petAge;
    private int daysStay;
    private double amountDue;
    private boolean isNewPet;

    // Constructor to initialize Pet object
    public Pet(String petType, String petName, int petAge,int daysStay) {
        this.petType = petType;
        this.petName = petName;
        this.petAge = petAge;
        this. daysStay = daysStay;
    }

    // Getters and setters based on UML class diagram
    // See Project One Specification Document for more information
    public String getPetType() {
        return petType;
    }

    public void setPetType(String petType) {
        this.petType = petType;
    }

    public String getPetName() {
        return petName;
    }

    public void setPetName(String petName) {
        this.petName = petName;
    }

    public int getPetAge() {
        return petAge;
    }

    public void setPetAge(int petAge) {
        this.petAge = petAge;
    }
    
    public int getDogSpaces() {
      return dogSpaces;
    }

    public void setDogSpaces(int dogSpaces){
      this.dogSpaces = dogSpaces;
    }

    public int getCatSpaces() {
      return catSpaces;
    }

    public void setCatSpaces(int catSpaces){
      this.catSpaces = catSpaces;
    }
    public int getDaysStay() {
        return daysStay;
    }

    public void setDaysStay(int daysStay) {
        this.daysStay = daysStay;
    }

    public double getAmountDue() {
        return amountDue;
    }

    public void setAmountDue(double amountDue) {
        this.amountDue = amountDue;
    }

    public boolean isNewPet() {
        return isNewPet;
    }

    public void setNewPet(boolean newPet) {
        isNewPet = newPet;
    }

    // Method to check-in a pet
    public static void checkIn(Pet pet) {
        Scanner scanner = new Scanner(System.in);  // Create a new Scanner object

        // Prompt for pet type dog/cat
        System.out.println("Enter pet type (dog/cat):");
        // Read user input, and convert it to lower case
        String type = scanner.nextLine().toLowerCase(); 
        pet.setPetType(type);
        // If input is not dog/cat, display error message "Invalid pet type"
        if (!type.equals("dog") && !type.equals("cat")) {
            System.out.println("Invalid pet type.");
            scanner.close();
            return;
        }
        // Check boarding space availability for dogs/cats
        if (type.equals("dog")) {
            if (dogSpaces <= 0) {
            	// If pet type is dog, dogSpaces <=0, display message "No spaces available for dogs"
                System.out.println("Sorry, no space available for dogs.");
                scanner.close();
                return;
            }
            pet.setDogSpaces(dogSpaces-1);   // Otherwise, update dogs space count
        } else { 
            if (catSpaces <= 0) {
            	// If catSpaces<=0, display message "No spaces available for cats"
                System.out.println("Sorry, no space available for cats.");
                scanner.close();
                return;
            }
            pet.setCatSpaces(catSpaces-1);  // Otherwise, update cats space count
        }

        // Check if it's a new pet and set NewPet to true
        System.out.println("Is this a new pet? (yes/no)");
        String isNew = scanner.nextLine().toLowerCase();
        pet.setNewPet(isNew.equals("yes"));

        // Prompt to enter pet's name
        System.out.println("Enter pet name:");
        String name = scanner.nextLine(); // Read user input
        pet.setPetName(name);
        // If pet had been services before, offer to update pet's information
        if (!pet.isNewPet()) {
            System.out.println("Update " + pet.getPetName() + "'s information? (yes/no)");
            String update = scanner.nextLine().toLowerCase();
            // If input is yes, ask to enter pet's age
            if (update.equals("yes")) {
                System.out.println("Enter pet age:");
                int age = scanner.nextInt();
                pet.setPetAge(age);
            }
        } else {
        	// if pet is new, ask to enter pet's age
            System.out.println("Enter pet age:");
            int age = scanner.nextInt();
            pet.setPetAge(age);
        }
        // Prompt to enter boarding period
        System.out.println("Enter stay duration:");
        int duration = scanner.nextInt();   // Read user input, set number of the days
        pet.setDaysStay(duration);
        // If pet is a dog and number of days is >=2 days
        if (pet.getPetType().equals("dog") && duration >= 2) {
        	// Offer grooming services
            System.out.println("Is grooming requested? (yes/no)");
            String grooming = scanner.next().toLowerCase();  // Read user input
            if (grooming.equals("yes")) {  //  If input is yes, display message "pet will be groomed"
                System.out.println(pet.getPetName() + " will be groomed during the stay.");
            }
        }
        // Display message "Pet was assigned boarding space ID"
        System.out.println("Assign " + pet.getPetName() + " a space ID.");
       // If pet is a dog, dogs boarding spaces were updated
        if (pet.getPetType().equals("dog")) {
            System.out.println("Updating dog boarding availability.");
       // If pet is a cat, cats boarding spaces were updated
        } else if (pet.getPetType().equals("cat")) {
            System.out.println("Updating cat boarding availability.");
        }

        scanner.close(); // Close Scanner object
    }
}

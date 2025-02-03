export class ForgetPassword {
  email: string;

  constructor(email: string) {
    if (!ForgetPassword.isValidEmail(email)) {
      throw new Error("Invalid email format.");
    }
    this.email = email;
  }

  static isValidEmail(email: string): boolean {
    const emailRegex = /\S+@\S+\.\S+/; // Simple email validation regex
    return emailRegex.test(email);
  }
}

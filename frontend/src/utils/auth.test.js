import { calculatePasswordStrength } from './auth';

describe('calculatePasswordStrength', () => {
  it.each([
    "password",
    "123456789",
    "abc123",
    "login123",
    "admin123",
    "1111111111111111111111",
    "1q2w3e",
  ])('returns "Too Weak" for %s', (pwd) => {
    expect(calculatePasswordStrength(pwd)).toStrictEqual("Too Weak")
  })

  it.each([
    // generated with a password generator
    "Iq09k#r3:6?}",
    "4{p_;)T7A95;",
    "m)$*Fl!36|e7"
  ])('returns "Strong" for %s', (pwd) => {
    expect(calculatePasswordStrength(pwd)).toStrictEqual("Strong")
  })
});

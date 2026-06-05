export function setAuth(token) {
  window.localStorage.setItem("token", token);
}

export function getAuthToken() {
  return window.localStorage.getItem("token");
}

export function getAuthPayload() {
  const token = getAuthToken();
  if (token == "null") {
    return null
  }

  const payloadPart = token.split('.')[1]
  const base64 = payloadPart
    .replace('/-/g', '+')
    .replace(/_/g, '/')
    .padEnd(Math.ceil(payloadPart.length / 4) * 4, "=");

  return JSON.parse(atob(base64))
}

export function clearAuth() {
  window.localStorage.removeItem("user");
}

export function calculatePasswordStrength(pwd) {
  const minLength = 8
  if (pwd.length < minLength) {
    return "Weak"
  }
  let score = 0;
  // add a point for every additional 4 chars after the min length of 8
  score += Math.floor((pwd.length - minLength) / 4);
  // standard checks for digits, uppercase, lowercase, symbols
  if (/\d/.test(pwd)) {
    score += 1;
  }
  if (/[A-Z]/.test(pwd)) {
    score += 1;
  }
  if (/[a-z]/.test(pwd)) {
    score += 1;
  }
  if (/[!"£$%^&*()[\]\\\/\.,<>#~;:'@|`¬¦+=_-]/.test(pwd)) {
    score += 1;
  }
  // check for the amount of unique characters.
  // "Aaaaaaaaaaa111!" may score highly on char types
  // but isn't very unique
  score += new Set(pwd).size;

  const commonMistakes = [
    /p[@a]ss(w[o0]rd)?/i, // catch variations of "pass" and "password"
    /123/i, /456/i, /789/i,  // catch number runs
    /321/i, /654/i, /987/i,  // and in reverse
    /abc/i,  // letter runs
    /(\d)\1{2,}/i, // catch strings of repeated chars, such as "1111"
    // other popular ones from https://en.wikipedia.org/wiki/List_of_the_most_common_passwords
    /admin/i, /login/i, /qwerty/i, /welcome/i, /letmein/i, /adobe/i, /photoshop/i, /azerty/i, /master/i, /hello/i,
    /!["@]#\$%\^/i, // top row of symbols in order (US and UK layout)
    /1q2w3e/i  // alternate top row of numbers and letters
  ];
  // penalise these heavily as they'll all be in rainbow tables. Easy to hack
  for (const mistake of commonMistakes) {
    if (mistake.test(pwd)) {
      score -= 5;
    }
  }
  if (score <= 8) {
    // requires minimal length password with a small char variation
    // eg: twentytwo
    return "Weak"
  } else if (score <= 14) {
    // minimal length but more char type variation
    // eg: Twenty26
    return "Medium"
  } else {
    // decent length, good variations and no common mistakes
    // eg: 07iO9I##z%TLxg
    return "Strong"
  }
}
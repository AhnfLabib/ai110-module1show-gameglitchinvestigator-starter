# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
- List at least two concrete bugs you noticed at the start  
  (for example: "the hints were backwards").

  1. I noticed that when you submit with "Enter", it doesn't really work as a submission button.
  2. After you submit any number, it keeps on hinting you to go lower even if the number is higher than your guessed number.
  3. When you choose the difficulty level, regardless of the numerical range, it will choose one number outside that range.

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
- Give one example of an AI suggestion that was incorrect or misleading (including what the AI suggested and how you verified the result).

  1. I used Cursor Auto
  2. Cursor Auto suggested storing the secret in st.session_state.secret so it wouldn’t reset on each Streamlit rerun. I verified by running the app, opening the Developer Debug Info, submitting a guess, and confirming the secret number stayed the same.
  3. Most suggestions were correct once I described the bug clearly. One suggestion was incomplete: it fixed the hint message text but not the condition that decided when to show it, so I had to adjust the condition myself after testing in the app.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
- Did AI help you design or understand any tests? How?

  1. I decided a bug was fixed by (1) running the app and checking the behavior (e.g. hints vs. secret in the debug panel, or Enter key submit), and (2) running pytest so the tests that encode the correct behavior passed.
  2. I ran pytest tests/test_game_logic.py. For example, test_check_guess_numeric_comparison_with_int_secret calls check_guess(9, 100) and expects outcome 'Too Low'. When it passed, it showed that the hint logic correctly treats 9 as lower than 100, so the backwards-hint bug was fixed.
  3. Yes. I asked the AI how to run the tests or what a failing test was checking; it explained that test_check_guess_string_secret_... was ensuring the secret is compared as a number even when passed as a string, which helped me fix the comparison.
---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
- What is one thing you would do differently next time you work with AI on a coding task?
- In one or two sentences, describe how this project changed the way you think about AI generated code.

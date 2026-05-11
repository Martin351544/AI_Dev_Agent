import requests
import tkinter as tk

# prompts for each AI that does everything
PLANNER_PROMPT = """
You are a planning agent.
Break tasks into clear step-by-step technical plans.
Be precise and structured.
"""


CODER_PROMPT = """
You are a senior Python developer.
Write clean, working code based on the plan.
No explanation, only code.
"""


CRITIC_PROMPT = """
You are a code reviewer.
Find bugs, inefficiencies, and missing edge cases.
Be strict and technical.
"""


TESTER_PROMPT = """
You generate test cases for code.
Include edge cases and failure cases.
If you find no problems in the code then output "no issues"
"""


ROUNDS_PROMPT = """
Return a number of iterations (2–4).

Rules:
- Do NOT maximize.
- Prefer the smallest sufficient number.
- Only increase iterations if task is complex.

Return ONLY the number.
"""


OUTPUT_PROMPT = """
Return:
1. Short summary (2–3 lines)
2. Final code exactly as provided
Do not modify code.
"""



# this is the ai's API 
def ask_ollama(prompt, model="llama3"):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(url, json=data)
    return response.json()["response"]




# this is the ai system
def run_task(task, max_rounds):

    plan = ask_ollama(PLANNER_PROMPT + "\nTask: " + task, "llama3")
    
    code = ask_ollama(CODER_PROMPT + "\nPlan:\n" + plan, "llama3")

    for i in range(max_rounds): 
        review = ask_ollama(CRITIC_PROMPT + "\nCode:\n" + code, "llama3" )

        tests = ask_ollama(TESTER_PROMPT + "\nCode:\n" + code, "llama3")

        if "no issues" in review.lower():

            return {
                "Code": code,
                "Review":review,
                "Tests":tests
            }


        fix_prompt = f"""
        Fix the code based on the test results, review and code:
        
        Test results:
        {tests}

        Review:
        {review}

        Code:
        {code}
        """
        
        code = ask_ollama(CODER_PROMPT + fix_prompt, "llama3")


    return {
            "Code": code,
            "Review":review,
            "Tests":tests
        }



# create window
root = tk.Tk()
root.title("AI Chat")
root.geometry("600x650")
root.configure(bg="#111111")

# chat display
chat_display = tk.Text(
    root,
    bg="#1e1e1e",
    fg="white",
    font=("Arial", 12),
    wrap="word"
)

chat_display.pack(padx=10, pady=10, fill="both", expand=True)

# input frame
input_frame = tk.Frame(root, bg="#111111")
input_frame.pack(fill="x", padx=10, pady=10)

# Textbox
textbox = tk.Entry(
    input_frame,
    font=("Arial", 12)
)

textbox.pack(side="left", fill="x", expand=True, padx=(0, 10))

# send function 
def send_message():
    user_text = textbox.get()

    if user_text == "":
        return

    # Show user message
    chat_display.insert(tk.END, "You: " + user_text + "\n")
    
    print("input being processed plase be patient. the AI can take up to 7 min")
    

    rounds_raw = ask_ollama(
        ROUNDS_PROMPT + "\nTheir prompt:\n" + user_text,
        "llama3"
    )   

    digits = ''.join(filter(str.isdigit, rounds_raw))
    rounds = int(digits) if digits  else 2
    rounds = max(2, min(rounds, 4))

    print(rounds)

    
    code = run_task(user_text, int(rounds))

    formated = f"""
    FINAL CODE:
    {code["Code"]}

    REVIEW:
    {code["Review"]}

    TESTS:
    {code["Tests"]}
    """

    
    ai_response = formated

    # Show AI message
    chat_display.insert(tk.END, ai_response + "\n\n")

    # Auto scroll
    chat_display.see(tk.END)

    # Clear textbox
    textbox.delete(0, tk.END)


# Send button
send_button = tk.Button(
    input_frame,
    text="Send",
    command=send_message,
    bg="#2563eb",
    fg="white"
)

send_button.pack(side="right")

# Run app
root.mainloop()

# Rule 5: Mutable Default Argument (List)
def bad_function(data=[]):
    try:
        # Rule 1: print() check
        print("Processing...")
        
        # Rule 2: == None check
        if data == None:
            # Rule 3: eval() Security Risk
            return eval("1+1")
            
    # Rule 6: Bare except block
    except:
        pass

# Rule 4: Too many arguments (6 arguments)
def too_complex(a, b, c, d, e, f):
    return a + b

# --- Level 2: AI (CodeBERT) Targets ---

def save_user_session():
    # Semantic Target: "hardcoded sensitive credentials"
    api_secret = "sk-live-5e9f2a1b3c4d5e6f7g8h9i0j" 
    
    # Semantic Target: "opening files without using with"
    log_file = open("session.log", "a")
    log_file.write("Session started")
    log_file.close()

async def fetch_data_async():
    # Semantic Target: "blocking sleep calls in async functions"
    # AI knows time.sleep() is bad inside an 'async def'
    time.sleep(5) 
    return {"status": "success"}

def calculate_factorial(n):
    # Semantic Target: "recursive function without base case"
    # AI identifies this structure as potentially infinite/unsafe
    return n * calculate_factorial(n - 1)
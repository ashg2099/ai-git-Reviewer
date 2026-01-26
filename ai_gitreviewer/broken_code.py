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
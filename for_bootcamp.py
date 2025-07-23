# Get the number of terms from the user
terms = int(input("Enter the terms ")) 

# Initialize the first two Fibonacci numbers
a = 0 
b = 1 

# Initialize a counter for the loop
count = 0

# Handle edge cases for number of terms
if (terms <= 0): 
    print("Please enter a valid integer") 
elif (terms == 1): 
    print("Fibonacci sequence upto", terms, ":")
    print(a) 
else: # For terms > 1
    print("Fibonacci sequence:") 
    # Use a while loop to generate the sequence
    while (count < terms): 
        print(a, end = ' ') # print current 'a' without newline 
        
        # Calculate the next Fibonacci number
        c = a + b 
        
        # Update values for the next iteration
        # a takes the value of the previous b
        a = b 
        # b takes the value of the newly calculated c
        b = c 
        
        # Increment the counter
        count += 1 
    print() # Print a newline at the end for clean output
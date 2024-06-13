import os
import tkinter as tk
from tkinter import simpledialog
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import string
import random

# Function to generate a random password with at least one number
def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))

    # Ensure the password contains at least one digit
    if not any(char.isdigit() for char in password):
        password = list(password)
        password[random.randint(0, length - 1)] = random.choice(string.digits)
        password = ''.join(password)

    return password

# Function to continue the script after CAPTCHA is solved
def continue_script():
    global captcha_solved, root
    captcha_solved = True
    if root:
        root.destroy()
        root = None

# Function to create an account
def create_account():
    global captcha_solved, root, driver, wait

    try:
        # Set up the Selenium WebDriver with Chrome options
        driver = webdriver.Chrome(options=chrome_options)
        wait = WebDriverWait(driver, 30)  # Set up a wait with a timeout of 30 seconds

        # Step 1: Go to https://mindstudio.ai/ and click on the "Sign up" button
        driver.get("https://mindstudio.ai/")
        wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Sign up"))).click()
        
        # Step 2: Open a new tab and go to https://www.emailfake.org/en
        driver.execute_script("window.open('https://www.emailfake.org/en', '_blank');")
        driver.switch_to.window(driver.window_handles[1])
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "button.custom-email-botton")))

        # Create a simple GUI to wait for CAPTCHA completion
        captcha_solved = False
        root = tk.Tk()
        root.title("CAPTCHA Completion")
        label = tk.Label(root, text="Please complete the CAPTCHA and then click the button below.")
        label.pack(pady=10)
        button = tk.Button(root, text="CAPTCHA Solved", command=continue_script)
        button.pack(pady=10)
        root.mainloop()

        # Wait for the user to indicate CAPTCHA completion
        while not captcha_solved:
            time.sleep(1)

        # Click the button to copy the email address to the clipboard
        copy_button = driver.find_element(By.CSS_SELECTOR, "button.custom-email-botton")
        copy_button.click()
        time.sleep(0.5)  # Wait for the email to be copied to the clipboard

        # Get the fake email address from the clipboard
        fake_email = driver.execute_script("return document.querySelector('#trsh_mail').value")

        # Step 3: Go back to the sign-up tab
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(0.1)  # Ensure the switch is complete

        # Fill in the email and password fields
        email_input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email'][placeholder='Enter your email address']")))
        email_input.send_keys(fake_email)

        # Generate a random password with at least one number
        password = generate_password()

        password_input = driver.find_element(By.CSS_SELECTOR, "input[type='password'][placeholder='Enter a password']")
        password_input.send_keys(password)

        # Step 4: Click the "Create account" button
        create_account_button = driver.find_element(By.CSS_SELECTOR, "button.sc-2bf93adb-2.NtaMC")
        create_account_button.click()

        # Wait for the email to be received
        time.sleep(0.5)

        # Step 4.1: Go back to the email tab and click on the email link
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(0.5)  # Wait for the page to load

        # Locate and click on the email link
        email_link = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.view_email")))
        email_link.click()
        time.sleep(0.5)  # Wait for the email content to load

        # Step 4.2: Switch to the iframe and find the "Confirm My Email" span and click its parent link
        try:
            # Switch to the iframe
            iframe = driver.find_element(By.ID, "myIframe")
            driver.switch_to.frame(iframe)
            
            # Locate and click the "Confirm My Email" span
            confirm_email_span = wait.until(EC.presence_of_element_located((By.XPATH, "//span[text()='Confirm My Email']")))
            confirm_email_link = confirm_email_span.find_element(By.XPATH, "./ancestor::a")
            confirm_email_link.click()
            time.sleep(5)  # Wait for the confirmation page to load
        except Exception as e:
            print(f"Error: {e}")
            print("Page source:")
            print(driver.page_source)

        # Step 5: Append the email and password to a text file
        with open("credentials.txt", "a") as file:
            file.write(f"Email: {fake_email}\n")
            file.write(f"Password: {password}\n")

    except Exception as e:
        print(f"An error occurred during account creation: {e}")

    finally:
        # Close the browser
        driver.quit()

# Set up Chrome options
chrome_options = Options()

# Create a simple GUI to get the number of accounts to create
root = tk.Tk()
root.withdraw()  # Hide the root window

num_accounts = simpledialog.askinteger("Input", "Enter the number of accounts to create:", minvalue=1)
root.destroy()

if num_accounts is None:
    print("No input provided. Exiting.")
    exit(1)

# Create the specified number of accounts
for _ in range(num_accounts):
    create_account()
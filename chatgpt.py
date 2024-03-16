# chatgpt.py
import openai
import config
import time

# Set your API key
api_key = config.OPENAI_API_KEY

# Create an OpenAI client instance with the API key
client = openai.Client(api_key=api_key)

def queryGPT(system, prompt, response_format="text", iscreative=False, deep=config.DEEP):
    try:
        # Validate and set response format
        if isinstance(response_format, str) and response_format.lower() == "json":
            response_format = {"type": "json_object"}
        else:
            response_format = {"type": "text"}

        # Validate and set temperature based on iscreative
        if isinstance(iscreative, bool) and iscreative:
            temperature = 0.8
        else:
            temperature = 0.2

        # Decide model to use
        if deep:
            gptmodel = "gpt-4-0125-preview"
        else:
            gptmodel = "gpt-3.5-turbo-1106"

        start_time = time.time()  # Start the timer

        # Call to OpenAI API
        response = client.chat.completions.create(
            model=gptmodel,
            response_format=response_format,
            max_tokens=4000,
            temperature=temperature,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt}
            ]
        )

        # Time tracking
        end_time = time.time()  # Stop the timer
        total_time = end_time - start_time  # Calculate the total time taken
        print(f"ChatGPT API call took {total_time} seconds")  # Print the total time taken

        # Extracting text content from the response
        conversation_capture = response.choices[0].message.content

        return conversation_capture
    except Exception as e:
        print(f"An error occurred: {e}")
        # Handle or log the error as needed
        return None

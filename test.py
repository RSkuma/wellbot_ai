import asyncio
import os
from dotenv import load_dotenv 
from helper_functions import print_ascii_art
from hume import HumeVoiceClient, MicrophoneInterface, VoiceSocket, VoiceConfig


message_counter = 0



def on_open():
    print_ascii_art("Say hello to EVI, Hume AI's Empathic Voice Interface!")

# Handler for incoming messages
def on_message(message):
    global message_counter
    # Increment the message counter for each received message
    message_counter += 1
    msg_type = message["type"]

    # Start the message box with the common header
    message_box = (
        f"\n{'='*60}\n"
        f"Message {message_counter}\n"
        f"{'-'*60}\n"
    )

    # Add role and content for user and assistant messages
    if msg_type in {"user_message", "assistant_message"}:
        role = message["message"]["role"]
        content = message["message"]["content"]
        message_box += (
            f"role: {role}\n"
            f"content: {content}\n"
            f"type: {msg_type}\n"
        )

        # Add top emotions if available
        if "models" in message and "prosody" in message["models"]:
            scores = message["models"]["prosody"]["scores"]
            num = 3
            # Get the top N emotions based on the scores
            top_emotions = get_top_n_emotions(prosody_inferences=scores, number=num)

            message_box += f"{'-'*60}\nTop {num} Emotions:\n"
            for emotion, score in top_emotions:
                message_box += f"{emotion}: {score:.4f}\n"

    # Add all key-value pairs for other message types, excluding audio_output
    elif msg_type != "audio_output":
        for key, value in message.items():
            message_box += f"{key}: {value}\n"
    else:
        message_box += (
            f"type: {msg_type}\n"
        )

    message_box += f"{'='*60}\n"
    # Print the constructed message box
    print(message_box)

# Function to get the top N emotions based on their scores
def get_top_n_emotions(prosody_inferences, number):
 
    sorted_inferences = sorted(prosody_inferences.items(), key=lambda item: item[1], reverse=True)
    return sorted_inferences[:number]

# Handler for when an error occurs
def on_error(error):
    # Print the error message
    print(f"Error: {error}")

# Handler for when the connection is closed
def on_close():
    # Print a closing message using ASCII art
    print_ascii_art("Thank you for using EVI, Hume AI's Empathic Voice Interface!")


async def user_input_handler(socket: VoiceSocket):
    while True:
        # Asynchronously get user input to prevent blocking other operations
        user_input = await asyncio.to_thread(input, "Type a message to send or 'Q' to quit: ")
        if user_input.strip().upper() == "Q":
            # If user wants to quit, close the connection
            print("Closing the connection...")
            await socket.close()
            break
        else:
            # Send the user input as text to the socket
            await socket.send_text_input(user_input)



# Asynchronous main function to set up and run the client
async def main() -> None:
    try:
        # Retrieve any environment variables stored in the .env file

        # Retrieve the Hume API key from the environment variables
        HUME_API_KEY = os.getenv("HUME_API_KEY")
        HUME_SECRET_KEY = os.getenv("HUME_SECRET_KEY")

        # Connect and authenticate with Hume
        client = HumeVoiceClient(HUME_API_KEY, HUME_SECRET_KEY)

        #CONFIGURATION CREATION(one time)
        #client = HumeVoiceClient("3FjYIcedc3DI5I5trnCM1me32fVLboKRq8G6mLVCFQbgI0AS")
        # config: VoiceConfig = client.create_config(
        #     name=f"testBot2",
        #     prompt="You always start your sentence with 'Yellow!'. You are an AI customer service agent for a non-profit company that helps young teens in need. You help customers with their inquiries, issues and requests. You represent the company and aim to provide excellent, friendly and efficient customer service at all times. Your role is to listen attentively to the customer, understand their needs, and do your best to assist them or direct them to the appropriate resources. If they sound like they need urgent help, try to calm them down first then direct them to emergency services."
        #     )
        # print("Created config: ", config.id)

        #fetching our config
        # config = client.get_config(HUME_API_KEY)
        # print("Fetched config: ", config.name)
        # async with client.connect(config_id="baf1c67f-5dff-4404-93e1-f48ff4dafd3a") as socket:
        #     print("Check!")
        #     await MicrophoneInterface.start(socket)

        #print list of configs
        # for config in client.iter_configs():
        #     print(f"- {config.name} ({config.id})")

        # Start streaming EVI over your device's microphone and speakers
        async with client.connect_with_handlers(
            #insert your own configID for the bot you want"
            config_id="1403d06f-96b6-4802-b7b4-e5fc5ebc0363",
            on_open=on_open,                # Handler for when the connection is opened
            on_message=on_message,          # Handler for when a message is received
            on_error=on_error,              # Handler for when an error occurs
            on_close=on_close,              # Handler for when the connection is closed
            enable_audio=True,              # Flag to enable audio playback (True by default)
        ) as socket:
            # Start the microphone interface in the background; add "device=NUMBER" to specify device
            microphone_task = asyncio.create_task(MicrophoneInterface.start(socket))

            # Start the user input handler
            user_input_task = asyncio.create_task(user_input_handler(socket))

            # The gather function is used to run both async tasks simultaneously
            await asyncio.gather(microphone_task, user_input_task)
    except Exception as e:
        # Catch and print any exceptions that occur
        print(f"Exception occurred: {e}")


# Import pygame module and initialize
import pygame
pygame.init()


# Initialize Game Variables
title = 1
running = True
screen = pygame.display.set_mode((1280, 720))

text_font = pygame.font.SysFont("Comic Sans", 60)
text_col = "Black"
def draw_text(text, x, y):
    img = text_font.render(text,True, text_col)
    screen.blit(img, (x, y))






load_dotenv()
# Game Logic
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Title Scene
    if title == 1:

        # Load Title Screen
        title_screen = pygame.image.load("title.png")
        title_screen = pygame.transform.scale(title_screen, (1280,720))
        screen.blit(title_screen, (0,0))
        pygame.display.update()
        
        # If Return Key is Pressed, Switch Scene
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            title += 1
    
    if title == 2:
        
        asyncio.run(main())

        # Load FirstTime Screen
        title_screen = pygame.image.load("FirstTime.png")
        title_screen = pygame.transform.scale(title_screen, (1280,720))
        screen.blit(title_screen, (0,0))
        pygame.display.update()

        # If Return Key is Pressed, Switch Scene
        keys = pygame.key.get_pressed()
        if keys[pygame.K_y]:
            title += 1

    if title == 3:

        title_screen = pygame.image.load("SecondTime.png")
        title_screen = pygame.transform.scale(title_screen, (1280,720))
        screen.blit(title_screen, (0,0))


        draw_text("Happy", 380, 220)
        draw_text("Sad", 735, 220)
        draw_text("Excited", 1045, 220)
        pygame.display.update()


        # If Return Key is Pressed, Switch Scene
        keys = pygame.key.get_pressed()
        if keys[pygame.K_n]:
            title += 1



pygame.quit()
